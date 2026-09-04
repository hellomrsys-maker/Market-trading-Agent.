package optionalpha;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

/**
 * OptionAlpha Agent — Java Prometheus Cognitive & Telemetry Sidecar Daemon
 * Polyglot Pillar 6: Java Industrial Sidecar
 */
public class CognitiveMetricsDaemon {
    private static final int PORT = 8282;
    private static final AtomicLong buyDecisions = new AtomicLong(0);
    private static final AtomicLong sellDecisions = new AtomicLong(0);
    private static final AtomicLong holdDecisions = new AtomicLong(0);
    private static final ConcurrentHashMap<String, Double> attentionWeights = new ConcurrentHashMap<>();

    public static void recordDecision(String action) {
        if ("BUY".equalsIgnoreCase(action)) {
            buyDecisions.incrementAndGet();
        } else if ("SELL".equalsIgnoreCase(action)) {
            sellDecisions.incrementAndGet();
        } else {
            holdDecisions.incrementAndGet();
        }
    }

    public static void setAttention(String symbol, double weight) {
        attentionWeights.put(symbol, weight);
    }

    public static void main(String[] args) throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress(PORT), 0);
        server.createContext("/health", new HealthHandler());
        server.createContext("/metrics", new MetricsHandler());
        server.setExecutor(null);
        server.start();
        System.out.println("[JAVA-DAEMON] CognitiveMetricsDaemon listening on http://localhost:" + PORT + "/metrics");
    }

    static class HealthHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            String resp = "{\"status\":\"healthy\",\"daemon\":\"CognitiveMetricsDaemon\",\"port\":" + PORT + "}";
            send(exchange, 200, "application/json", resp);
        }
    }

    static class MetricsHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            StringBuilder sb = new StringBuilder();
            sb.append("# HELP optionalpha_tristate_buy_total Total BUY decisions emitted\n");
            sb.append("# TYPE optionalpha_tristate_buy_total counter\n");
            sb.append("optionalpha_tristate_buy_total ").append(buyDecisions.get()).append("\n");

            sb.append("# HELP optionalpha_tristate_sell_total Total SELL decisions emitted\n");
            sb.append("# TYPE optionalpha_tristate_sell_total counter\n");
            sb.append("optionalpha_tristate_sell_total ").append(sellDecisions.get()).append("\n");

            sb.append("# HELP optionalpha_tristate_hold_total Total HOLD decisions emitted\n");
            sb.append("# TYPE optionalpha_tristate_hold_total counter\n");
            sb.append("optionalpha_tristate_hold_total ").append(holdDecisions.get()).append("\n");

            sb.append("# HELP optionalpha_contract_multiplier Equity options standard multiplier\n");
            sb.append("# TYPE optionalpha_contract_multiplier gauge\n");
            sb.append("optionalpha_contract_multiplier 100\n");

            for (var entry : attentionWeights.entrySet()) {
                sb.append("optionalpha_cognitive_attention{symbol=\"").append(entry.getKey()).append("\"} ")
                  .append(entry.getValue()).append("\n");
            }

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
