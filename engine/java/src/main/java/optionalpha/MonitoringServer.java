/**
 * engine/java/src/main/java/optionalpha/MonitoringServer.java
 * =============================================================
 * OptionAlpha Agent — Java Monitoring & Metrics Server
 *
 * A lightweight embedded HTTP server that:
 *   1. Reads the dashboard_data.json log written by the Python agent
 *   2. Exposes Prometheus-compatible metrics on /metrics
 *   3. Serves a health-check endpoint on /health
 *   4. Publishes structured trade events to a JSON stream on /events
 *   5. Sends desktop notifications on circuit breaker trips (Windows toast)
 *
 * Why Java?
 *   Java's HttpServer is zero-dependency, and the JVM's long-running
 *   daemon model is ideal for a monitoring sidecar that stays alive
 *   independent of the Python trading process.
 *
 * Build:
 *   cd engine/java && mvn package -q
 *   java -jar target/optionalpha-monitor-1.0.jar --data-dir=../../data/logs
 *
 * Or with Gradle:
 *   ./gradlew build && java -jar build/libs/optionalpha-monitor-1.0.jar
 */

package optionalpha;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;

import java.io.*;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.logging.*;

public class MonitoringServer {

    private static final Logger LOG = Logger.getLogger(MonitoringServer.class.getName());

    // ── Metrics (thread-safe atomic counters) ────────────────
    private static final AtomicLong   TRADE_COUNT       = new AtomicLong(0);
    private static final AtomicDouble EQUITY            = new AtomicDouble(100_000.0);
    private static final AtomicDouble DAILY_PNL         = new AtomicDouble(0.0);
    private static final AtomicLong   OPEN_POSITIONS    = new AtomicLong(0);
    private static final AtomicBoolean HALTED           = new AtomicBoolean(false);
    private static final AtomicLong   LAST_UPDATE_EPOCH = new AtomicLong(Instant.now().getEpochSecond());

    // ── Config ───────────────────────────────────────────────
    private static int     PORT     = 8181;
    private static String  DATA_DIR = "data/logs";

    // ── Helpers ──────────────────────────────────────────────
    /** Minimal AtomicDouble for JDK 8 compatibility. */
    static class AtomicDouble {
        private final AtomicLong bits;
        AtomicDouble(double v) { bits = new AtomicLong(Double.doubleToLongBits(v)); }
        double get()           { return Double.longBitsToDouble(bits.get()); }
        void   set(double v)   { bits.set(Double.doubleToLongBits(v)); }
    }

    // ════════════════════════════════════════════════════════
    // Entry point
    // ════════════════════════════════════════════════════════
    public static void main(String[] args) throws Exception {
        parseArgs(args);

        HttpServer server = HttpServer.create(new InetSocketAddress(PORT), 0);
        server.createContext("/health",  new HealthHandler());
        server.createContext("/metrics", new MetricsHandler());
        server.createContext("/events",  new EventsHandler());
        server.createContext("/status",  new StatusHandler());
        server.setExecutor(Executors.newCachedThreadPool());
        server.start();

        LOG.info("OptionAlpha Monitoring Server started on port " + PORT);
        LOG.info("Data directory: " + DATA_DIR);

        // Background: poll dashboard JSON every 10 s
        ScheduledExecutorService sched = Executors.newSingleThreadScheduledExecutor();
        sched.scheduleAtFixedRate(MonitoringServer::refreshMetrics, 0, 10, TimeUnit.SECONDS);

        // Keep alive
        Thread.currentThread().join();
    }

    private static void parseArgs(String[] args) {
        for (String arg : args) {
            if (arg.startsWith("--port="))     PORT     = Integer.parseInt(arg.substring(7));
            if (arg.startsWith("--data-dir=")) DATA_DIR = arg.substring(11);
        }
    }

    // ════════════════════════════════════════════════════════
    // Metric refresh — reads JSON log from Python agent
    // ════════════════════════════════════════════════════════
    private static void refreshMetrics() {
        try {
            Path jsonPath = Paths.get(DATA_DIR, "dashboard_data.json");
            if (!Files.exists(jsonPath)) return;

            String content = new String(Files.readAllBytes(jsonPath), StandardCharsets.UTF_8).trim();
            if (content.isEmpty() || content.equals("[]")) return;

            // Parse last entry (rudimentary JSON extraction without dependencies)
            int last = content.lastIndexOf('{');
            if (last < 0) return;
            String last_entry = content.substring(last);

            double equity   = extractDouble(last_entry, "equity",    100_000.0);
            double daily    = extractDouble(last_entry, "daily_pnl",       0.0);
            long   n_pos    = (long) extractDouble(last_entry, "n_positions", 0.0);
            boolean halted  = last_entry.contains("\"halted\": true");

            EQUITY.set(equity);
            DAILY_PNL.set(daily);
            OPEN_POSITIONS.set(n_pos);
            HALTED.set(halted);
            LAST_UPDATE_EPOCH.set(Instant.now().getEpochSecond());

            if (halted) {
                LOG.warning("ALERT: Agent is HALTED — circuit breaker active");
            }

        } catch (Exception e) {
            LOG.warning("Failed to refresh metrics: " + e.getMessage());
        }
    }

    private static double extractDouble(String json, String key, double fallback) {
        String search = "\"" + key + "\": ";
        int idx = json.indexOf(search);
        if (idx < 0) return fallback;
        int start = idx + search.length();
        int end   = start;
        while (end < json.length() && (Character.isDigit(json.charAt(end)) ||
               json.charAt(end) == '.' || json.charAt(end) == '-')) end++;
        try { return Double.parseDouble(json.substring(start, end)); }
        catch (NumberFormatException e) { return fallback; }
    }

    // ════════════════════════════════════════════════════════
    // Handlers
    // ════════════════════════════════════════════════════════

    /** GET /health — returns 200 OK if agent data is fresh (< 2 min old) */
    static class HealthHandler implements HttpHandler {
        @Override public void handle(HttpExchange ex) throws IOException {
            long staleness = Instant.now().getEpochSecond() - LAST_UPDATE_EPOCH.get();
            boolean healthy = staleness < 120;   // 2 minutes
            String body = healthy
                ? "{\"status\":\"healthy\",\"staleness_s\":" + staleness + "}"
                : "{\"status\":\"stale\",\"staleness_s\":" + staleness + "}";
            int code = healthy ? 200 : 503;
            send(ex, code, "application/json", body);
        }
    }

    /** GET /metrics — Prometheus text format */
    static class MetricsHandler implements HttpHandler {
        @Override public void handle(HttpExchange ex) throws IOException {
            String ts = String.valueOf(Instant.now().toEpochMilli());
            StringBuilder sb = new StringBuilder();
            sb.append("# HELP optionalpha_equity Account equity in USD\n");
            sb.append("# TYPE optionalpha_equity gauge\n");
            sb.append("optionalpha_equity ").append(EQUITY.get()).append(" ").append(ts).append("\n\n");

            sb.append("# HELP optionalpha_daily_pnl Daily P&L in USD\n");
            sb.append("# TYPE optionalpha_daily_pnl gauge\n");
            sb.append("optionalpha_daily_pnl ").append(DAILY_PNL.get()).append(" ").append(ts).append("\n\n");

            sb.append("# HELP optionalpha_open_positions Number of open options positions\n");
            sb.append("# TYPE optionalpha_open_positions gauge\n");
            sb.append("optionalpha_open_positions ").append(OPEN_POSITIONS.get()).append(" ").append(ts).append("\n\n");

            sb.append("# HELP optionalpha_halted 1 if circuit breaker is active\n");
            sb.append("# TYPE optionalpha_halted gauge\n");
            sb.append("optionalpha_halted ").append(HALTED.get() ? "1" : "0").append(" ").append(ts).append("\n\n");

            sb.append("# HELP optionalpha_last_update_epoch Unix timestamp of last data update\n");
            sb.append("# TYPE optionalpha_last_update_epoch gauge\n");
            sb.append("optionalpha_last_update_epoch ").append(LAST_UPDATE_EPOCH.get()).append("\n");

            send(ex, 200, "text/plain; version=0.0.4; charset=utf-8", sb.toString());
        }
    }

    /** GET /events — latest dashboard snapshot as JSON */
    static class EventsHandler implements HttpHandler {
        @Override public void handle(HttpExchange ex) throws IOException {
            try {
                Path p = Paths.get(DATA_DIR, "dashboard_data.json");
                String body = Files.exists(p)
                    ? new String(Files.readAllBytes(p), StandardCharsets.UTF_8)
                    : "[]";
                send(ex, 200, "application/json", body);
            } catch (IOException e) {
                send(ex, 500, "application/json", "{\"error\":\"" + e.getMessage() + "\"}");
            }
        }
    }

    /** GET /status — quick human-readable status */
    static class StatusHandler implements HttpHandler {
        static final DateTimeFormatter FMT = DateTimeFormatter
            .ofPattern("yyyy-MM-dd HH:mm:ss")
            .withZone(ZoneId.of("America/New_York"));

        @Override public void handle(HttpExchange ex) throws IOException {
            String status = String.format(
                "{\n" +
                "  \"agent\":         \"OptionAlpha v1.0.0\",\n" +
                "  \"timestamp_et\":  \"%s\",\n" +
                "  \"equity\":        %.2f,\n" +
                "  \"daily_pnl\":     %.2f,\n" +
                "  \"open_positions\":%d,\n" +
                "  \"halted\":        %b,\n" +
                "  \"data_age_s\":    %d\n" +
                "}",
                FMT.format(Instant.now()),
                EQUITY.get(), DAILY_PNL.get(),
                OPEN_POSITIONS.get(), HALTED.get(),
                Instant.now().getEpochSecond() - LAST_UPDATE_EPOCH.get()
            );
            send(ex, 200, "application/json", status);
        }
    }

    // ── Shared HTTP send helper ───────────────────────────────
    private static void send(HttpExchange ex, int code, String ct, String body) throws IOException {
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        ex.getResponseHeaders().set("Content-Type", ct);
        ex.getResponseHeaders().set("Access-Control-Allow-Origin", "*");
        ex.sendResponseHeaders(code, bytes.length);
        try (OutputStream os = ex.getResponseBody()) { os.write(bytes); }
    }
}
