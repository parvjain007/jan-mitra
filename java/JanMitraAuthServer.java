package java_auth;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;

import java.io.*;
import java.net.InetSocketAddress;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Standalone Java HTTP Authentication Server for JanMitra AI.
 * Uses built-in Java standard library (com.sun.net.httpserver).
 * Zero external dependencies required.
 */
public class JanMitraAuthServer {

    private static final int PORT = 8080;
    private static final Map<String, User> users = new ConcurrentHashMap<>();

    static {
        // Default demo account
        users.put("demo@janmitra.gov.in", new User("Demo Citizen", "demo@janmitra.gov.in", hashPassword("Password@123"), "citizen"));
    }

    public static void main(String[] args) throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress(PORT), 0);
        System.out.println("=================================================");
        System.out.println("  JanMitra AI — Java Authentication Server");
        System.out.println("  Running on: http://localhost:" + PORT);
        System.out.println("=================================================");

        server.createContext("/", new StaticLoginHandler());
        server.createContext("/api/login", new LoginApiHandler());
        server.createContext("/api/register", new RegisterApiHandler());
        server.setExecutor(null);
        server.start();
    }

    static class StaticLoginHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            File loginFile = new File("login.html");
            byte[] bytes;
            if (loginFile.exists()) {
                bytes = readFile(loginFile);
            } else {
                String fallback = "<html><body><h1>JanMitra Java Server</h1><p>Demo Citizen: demo@janmitra.gov.in / Password@123</p></body></html>";
                bytes = fallback.getBytes(StandardCharsets.UTF_8);
            }

            exchange.getResponseHeaders().set("Content-Type", "text/html; charset=UTF-8");
            exchange.sendResponseHeaders(200, bytes.length);
            OutputStream os = exchange.getResponseBody();
            os.write(bytes);
            os.close();
        }
    }

    static class LoginApiHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!"POST".equalsIgnoreCase(exchange.getRequestMethod())) {
                sendJsonResponse(exchange, 405, "{\"success\":false,\"message\":\"Method not allowed\"}");
                return;
            }

            String body = readRequestBody(exchange);
            Map<String, String> params = parseFormOrJson(body);

            String email = params.getOrDefault("email", "").trim().toLowerCase();
            String password = params.getOrDefault("password", "");

            User user = users.get(email);
            if (user != null && user.passwordHash.equals(hashPassword(password))) {
                String json = String.format("{\"success\":true,\"message\":\"Login successful\",\"user\":{\"name\":\"%s\",\"email\":\"%s\",\"role\":\"%s\"}}",
                        user.name, user.email, user.role);
                sendJsonResponse(exchange, 200, json);
            } else {
                sendJsonResponse(exchange, 401, "{\"success\":false,\"message\":\"Invalid email or password.\"}");
            }
        }
    }

    static class RegisterApiHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!"POST".equalsIgnoreCase(exchange.getRequestMethod())) {
                sendJsonResponse(exchange, 405, "{\"success\":false,\"message\":\"Method not allowed\"}");
                return;
            }

            String body = readRequestBody(exchange);
            Map<String, String> params = parseFormOrJson(body);

            String name = params.getOrDefault("name", "").trim();
            String email = params.getOrDefault("email", "").trim().toLowerCase();
            String password = params.getOrDefault("password", "");
            String confirm = params.getOrDefault("confirm_password", "");

            if (name.isEmpty() || email.isEmpty() || password.isEmpty()) {
                sendJsonResponse(exchange, 400, "{\"success\":false,\"message\":\"All fields are required.\"}");
                return;
            }
            if (password.length() < 6) {
                sendJsonResponse(exchange, 400, "{\"success\":false,\"message\":\"Password must be at least 6 characters.\"}");
                return;
            }
            if (!confirm.isEmpty() && !password.equals(confirm)) {
                sendJsonResponse(exchange, 400, "{\"success\":false,\"message\":\"Passwords do not match.\"}");
                return;
            }
            if (users.containsKey(email)) {
                sendJsonResponse(exchange, 400, "{\"success\":false,\"message\":\"An account with this email already exists.\"}");
                return;
            }

            User newUser = new User(name, email, hashPassword(password), "citizen");
            users.put(email, newUser);

            String json = String.format("{\"success\":true,\"message\":\"Account registered successfully\",\"user\":{\"name\":\"%s\",\"email\":\"%s\",\"role\":\"citizen\"}}",
                    name, email);
            sendJsonResponse(exchange, 200, json);
        }
    }

    private static String hashPassword(String password) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] hash = md.digest(password.getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder();
            for (byte b : hash) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (NoSuchAlgorithmException e) {
            return String.valueOf(password.hashCode());
        }
    }

    private static String readRequestBody(HttpExchange exchange) throws IOException {
        InputStream is = exchange.getRequestBody();
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        byte[] buffer = new byte[1024];
        int length;
        while ((length = is.read(buffer)) != -1) {
            baos.write(buffer, 0, length);
        }
        return baos.toString(StandardCharsets.UTF_8);
    }

    private static Map<String, String> parseFormOrJson(String body) {
        Map<String, String> map = new HashMap<>();
        if (body.startsWith("{") && body.endsWith("}")) {
            // Simple JSON parser for basic keys
            String stripped = body.substring(1, body.length() - 1);
            String[] pairs = stripped.split(",");
            for (String pair : pairs) {
                String[] kv = pair.split(":", 2);
                if (kv.length == 2) {
                    String k = kv[0].replaceAll("[\"\\s]", "");
                    String v = kv[1].replaceAll("[\"\\s]", "");
                    map.put(k, v);
                }
            }
        } else {
            // URL Encoded form
            String[] pairs = body.split("&");
            for (String pair : pairs) {
                String[] kv = pair.split("=", 2);
                if (kv.length == 2) {
                    try {
                        map.put(URLDecoder.decode(kv[0], StandardCharsets.UTF_8),
                                URLDecoder.decode(kv[1], StandardCharsets.UTF_8));
                    } catch (Exception ignored) {}
                }
            }
        }
        return map;
    }

    private static void sendJsonResponse(HttpExchange exchange, int statusCode, String responseJson) throws IOException {
        byte[] bytes = responseJson.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "application/json; charset=UTF-8");
        exchange.sendResponseHeaders(statusCode, bytes.length);
        OutputStream os = exchange.getResponseBody();
        os.write(bytes);
        os.close();
    }

    private static byte[] readFile(File file) throws IOException {
        FileInputStream fis = new FileInputStream(file);
        byte[] data = new byte[(int) file.length()];
        fis.read(data);
        fis.close();
        return data;
    }

    static class User {
        String name;
        String email;
        String passwordHash;
        String role;

        User(String name, String email, String passwordHash, String role) {
            this.name = name;
            this.email = email;
            this.passwordHash = passwordHash;
            this.role = role;
        }
    }
}
