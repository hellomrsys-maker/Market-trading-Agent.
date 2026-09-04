package optionalpha;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;

/**
 * OptionAlpha Agent — Java Prometheus Risk Gate & Circuit Breaker Telemetry Daemon
 * Polyglot Pillar 6: Java Industrial Sidecar
 */
public class RiskMetricsDaemon {
    private static final int PORT = 8383;
    private static final AtomicBoolean isHalted = new AtomicBoolean(false);
    private static final AtomicLong dailyPnlCents = new AtomicLong(0);
    private static final AtomicReference<Double> currentVix = new AtomicReference<>(16.0);
    private static final AtomicReference<Double> portfolioVar99Pct = new AtomicReference<>(1.25);
    private static final AtomicLong activePositions = new AtomicLong(0);

    public static void updateRiskState(boolean halted, long pnlCents, double vix, double varPct, long positions) {
        isHalted.set(halted);
        dailyPnlCents.set(pnlCents);
        currentVix.set(vix);
        portfolioVar99Pct.set(varPct);
        activePositions.set(positions);
    }

    public static void main(String[] args) throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress(PORT), 0);
        server.createContext("/health", ex -> send(ex, 200, "application/json", "{\"status\":\"healthy\",\"daemon\":\"RiskMetricsDaemon\"}"));
        server.createContext("/metrics", new MetricsHandler());
        server.start();
        System.out.println("[JAVA-DAEMON] RiskMetricsDaemon listening on http://localhost:" + PORT + "/metrics");
    }

    static class MetricsHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            StringBuilder sb = new StringBuilder();
            sb.append("# HELP optionalpha_circuit_breaker_halted 1 if trading halted, 0 otherwise\n");
            sb.append("# TYPE optionalpha_circuit_breaker_halted gauge\n");
            sb.append("optionalpha_circuit_breaker_halted ").append(isHalted.get() ? 1 : 0).append("\n");

            sb.append("# HELP optionalpha_daily_pnl_dollars Current daily profit/loss\n");
            sb.append("# TYPE optionalpha_daily_pnl_dollars gauge\n");
            sb.append("optionalpha_daily_pnl_dollars ").append(dailyPnlCents.get() / 100.0).append("\n");

            sb.append("# HELP optionalpha_spot_vix Spot VIX index level\n");
            sb.append("# TYPE optionalpha_spot_vix gauge\n");
            sb.append("optionalpha_spot_vix ").append(currentVix.get()).append("\n");

            sb.append("# HELP optionalpha_var_99_pct 99% 1-Day Delta-Gamma VaR Percentage\n");
            sb.append("# TYPE optionalpha_var_99_pct gauge\n");
            sb.append("optionalpha_var_99_pct ").append(portfolioVar99Pct.get()).append("\n");

            sb.append("# HELP optionalpha_active_positions Active portfolio position count\n");
            sb.append("# TYPE optionalpha_active_positions gauge\n");
            sb.append("optionalpha_active_positions ").append(activePositions.get()).append("\n");

            send(exchange, 200, "text/plain; version=0.0.4; charset=utf-8", sb.toString());
        }
    }

    private static void send(HttpExchange ex, int code, String contentType, String body) throws IOException {
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        ex.getResponseHeaders().set("Content-Type", contentType);
        ex.sendResponseHeaders(code, bytes.length);
        try (OutputStream os = ex.getResponseBody()) {
            os.write(bytes);
        }
    }
}
