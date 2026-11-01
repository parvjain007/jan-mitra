package java_auth;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HashMap;
import java.util.Map;

/**
 * JanMitra AI - Java GUI Citizen Login Application
 * Focused authentication interface: Citizen Login with personal dashboard display.
 * Registration is routed to the official Check Eligibility form.
 */
public class JanMitraLoginApp extends JFrame {

    // User Accounts Database
    private static final Map<String, UserAccount> userDatabase = new HashMap<>();

    static {
        // Pre-populate with demo citizen and admin
        userDatabase.put("demo@janmitra.gov.in", new UserAccount(
            "Demo Citizen",
            "demo@janmitra.gov.in",
            hashPassword("Password@123"),
            "citizen",
            "Rajasthan",
            150000,
            "Education & Learning"
        ));

        userDatabase.put("admin@janmitra.gov.in", new UserAccount(
            "System Administrator",
            "admin@janmitra.gov.in",
            hashPassword("Admin@123"),
            "admin",
            "National HQ",
            0,
            "Admin Management"
        ));
    }

    private JTextField loginEmailField;
    private JPasswordField loginPasswordField;

    public JanMitraLoginApp() {
        setTitle("JanMitra AI — Citizen Portal Login");
        setSize(480, 580);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        setResizable(false);

        JPanel mainPanel = new JPanel(new BorderLayout());
        mainPanel.setBackground(new Color(248, 250, 252));
        setContentPane(mainPanel);

        // Header
        mainPanel.add(createHeaderPanel(), BorderLayout.NORTH);

        // Center Login Panel
        mainPanel.add(createLoginPanel(), BorderLayout.CENTER);

        // Footer
        JLabel footerLabel = new JLabel("© 2026 JanMitra AI — AI Citizen Welfare Portal", SwingConstants.CENTER);
        footerLabel.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        footerLabel.setForeground(new Color(148, 163, 184));
        footerLabel.setBorder(new EmptyBorder(12, 0, 16, 0));
        mainPanel.add(footerLabel, BorderLayout.SOUTH);
    }

    private JPanel createHeaderPanel() {
        JPanel panel = new JPanel();
        panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
        panel.setBackground(new Color(37, 99, 235));
        panel.setBorder(new EmptyBorder(22, 20, 22, 20));

        JLabel titleLabel = new JLabel("✦ JanMitra AI");
        titleLabel.setFont(new Font("Segoe UI", Font.BOLD, 22));
        titleLabel.setForeground(Color.WHITE);
        titleLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        JLabel subtitleLabel = new JLabel("Citizen Welfare & Scheme Matching Portal");
        subtitleLabel.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        subtitleLabel.setForeground(new Color(219, 234, 254));
        subtitleLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        panel.add(titleLabel);
        panel.add(Box.createVerticalStrut(4));
        panel.add(subtitleLabel);
        return panel;
    }

    private JPanel createLoginPanel() {
        JPanel panel = new JPanel();
        panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
        panel.setBackground(Color.WHITE);
        panel.setBorder(new EmptyBorder(24, 32, 24, 32));

        // Quick Demo Fill Buttons
        JPanel demoBox = new JPanel(new GridLayout(2, 1, 6, 6));
        demoBox.setBackground(Color.WHITE);
        demoBox.setMaximumSize(new Dimension(Integer.MAX_VALUE, 76));
        demoBox.setAlignmentX(Component.LEFT_ALIGNMENT);

        JButton demoCitizenBtn = new JButton("⚡ Citizen Demo: demo@janmitra.gov.in");
        demoCitizenBtn.setFont(new Font("Segoe UI", Font.BOLD, 11));
        demoCitizenBtn.setBackground(new Color(239, 246, 255));
        demoCitizenBtn.setForeground(new Color(29, 78, 216));
        demoCitizenBtn.addActionListener(e -> {
            loginEmailField.setText("demo@janmitra.gov.in");
            loginPasswordField.setText("Password@123");
        });

        JButton demoAdminBtn = new JButton("🛡️ Admin Demo: admin@janmitra.gov.in");
        demoAdminBtn.setFont(new Font("Segoe UI", Font.BOLD, 11));
        demoAdminBtn.setBackground(new Color(245, 243, 255));
        demoAdminBtn.setForeground(new Color(124, 58, 237));
        demoAdminBtn.addActionListener(e -> {
            loginEmailField.setText("admin@janmitra.gov.in");
            loginPasswordField.setText("Admin@123");
        });

        demoBox.add(demoCitizenBtn);
        demoBox.add(demoAdminBtn);
        panel.add(demoBox);
        panel.add(Box.createVerticalStrut(18));

        // Email field
        JLabel emailLabel = new JLabel("Email Address:");
        emailLabel.setFont(new Font("Segoe UI", Font.BOLD, 13));
        emailLabel.setAlignmentX(Component.LEFT_ALIGNMENT);
        panel.add(emailLabel);
        panel.add(Box.createVerticalStrut(6));

        loginEmailField = new JTextField();
        loginEmailField.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        loginEmailField.setMaximumSize(new Dimension(Integer.MAX_VALUE, 38));
        loginEmailField.setAlignmentX(Component.LEFT_ALIGNMENT);
        panel.add(loginEmailField);
        panel.add(Box.createVerticalStrut(14));

        // Password field
        JLabel passLabel = new JLabel("Password:");
        passLabel.setFont(new Font("Segoe UI", Font.BOLD, 13));
        passLabel.setAlignmentX(Component.LEFT_ALIGNMENT);
        panel.add(passLabel);
        panel.add(Box.createVerticalStrut(6));

        loginPasswordField = new JPasswordField();
        loginPasswordField.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        loginPasswordField.setMaximumSize(new Dimension(Integer.MAX_VALUE, 38));
        loginPasswordField.setAlignmentX(Component.LEFT_ALIGNMENT);
        panel.add(loginPasswordField);
        panel.add(Box.createVerticalStrut(8));

        // Show password checkbox
        JCheckBox showPassCheck = new JCheckBox("Show Password");
        showPassCheck.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        showPassCheck.setBackground(Color.WHITE);
        showPassCheck.setAlignmentX(Component.LEFT_ALIGNMENT);
        showPassCheck.addActionListener(e -> {
            loginPasswordField.setEchoChar(showPassCheck.isSelected() ? (char) 0 : '•');
        });
        panel.add(showPassCheck);
        panel.add(Box.createVerticalStrut(20));

        // Login Button
        JButton loginBtn = new JButton("Log In to JanMitra");
        loginBtn.setFont(new Font("Segoe UI", Font.BOLD, 14));
        loginBtn.setBackground(new Color(37, 99, 235));
        loginBtn.setForeground(Color.WHITE);
        loginBtn.setFocusPainted(false);
        loginBtn.setAlignmentX(Component.LEFT_ALIGNMENT);
        loginBtn.setMaximumSize(new Dimension(Integer.MAX_VALUE, 42));
        loginBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        loginBtn.addActionListener(e -> handleLogin());
        panel.add(loginBtn);
        panel.add(Box.createVerticalStrut(20));

        // Registration Callout
        JPanel regBox = new JPanel();
        regBox.setLayout(new BoxLayout(regBox, BoxLayout.Y_AXIS));
        regBox.setBackground(new Color(240, 253, 244));
        regBox.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createLineBorder(new Color(187, 247, 208)),
            new EmptyBorder(12, 12, 12, 12)
        ));
        regBox.setAlignmentX(Component.LEFT_ALIGNMENT);
        regBox.setMaximumSize(new Dimension(Integer.MAX_VALUE, 80));

        JLabel regMsg = new JLabel("New Citizen? Register via Check Eligibility");
        regMsg.setFont(new Font("Segoe UI", Font.BOLD, 12));
        regMsg.setForeground(new Color(22, 101, 52));
        regMsg.setAlignmentX(Component.CENTER_ALIGNMENT);

        JButton openCheckBtn = new JButton("Open Eligibility Form & Register →");
        openCheckBtn.setFont(new Font("Segoe UI", Font.BOLD, 12));
        openCheckBtn.setBackground(new Color(16, 185, 129));
        openCheckBtn.setForeground(Color.WHITE);
        openCheckBtn.setFocusPainted(false);
        openCheckBtn.setAlignmentX(Component.CENTER_ALIGNMENT);
        openCheckBtn.addActionListener(e -> openWebEligibility());

        regBox.add(regMsg);
        regBox.add(Box.createVerticalStrut(6));
        regBox.add(openCheckBtn);
        panel.add(regBox);

        return panel;
    }

    private void handleLogin() {
        String email = loginEmailField.getText().trim().toLowerCase();
        String password = new String(loginPasswordField.getPassword());

        if (email.isEmpty() || password.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Please enter both email and password.", "Missing Fields", JOptionPane.WARNING_MESSAGE);
            return;
        }

        UserAccount user = userDatabase.get(email);
        if (user != null && user.passwordHash.equals(hashPassword(password))) {
            if ("admin".equals(user.role)) {
                JOptionPane.showMessageDialog(this, "Admin Login Verified!\nOpening Portal Admin Control Center...", "Admin Access", JOptionPane.INFORMATION_MESSAGE);
                openAdminWindow(user);
            } else {
                JOptionPane.showMessageDialog(this, "Login Successful!\nWelcome back, " + user.name + "!", "Authentication Successful", JOptionPane.INFORMATION_MESSAGE);
                openCitizenDashboardWindow(user);
            }
        } else {
            JOptionPane.showMessageDialog(this, "Invalid email or password.\nIf you are a new citizen, please register by checking scheme eligibility.", "Authentication Failed", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void openCitizenDashboardWindow(UserAccount user) {
        JFrame dash = new JFrame("JanMitra AI — Citizen Dashboard");
        dash.setSize(620, 520);
        dash.setLocationRelativeTo(this);

        JPanel p = new JPanel(new BorderLayout(16, 16));
        p.setBorder(new EmptyBorder(24, 24, 24, 24));
        p.setBackground(new Color(248, 250, 252));

        JLabel welcome = new JLabel("<html><h2 style='color:#1E3A8A;margin:0;'>Welcome, " + user.name + " 👋</h2>" +
                "<p style='color:#475569;margin-top:4px;'>Email: <b>" + user.email + "</b> | State: <b>" + user.state + "</b> | Category: <b>" + user.category + "</b></p></html>");
        p.add(welcome, BorderLayout.NORTH);

        // Citizen's personal schemes
        String[] columnNames = {"Scheme Name", "Category", "Eligibility & Benefit"};
        String[][] data = {
            {"National Merit Scholarship", user.category, "₹12,000 / year scholarship for students"},
            {"State Higher Education Fee Waiver", user.category, "Full tuition waiver for family income under ₹2.5L"},
            {"Pradhan Mantri Student Loan Scheme", user.category, "Collateral-free low interest education loan"}
        };
        JTable table = new JTable(data, columnNames);
        table.setRowHeight(30);
        table.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        table.getTableHeader().setFont(new Font("Segoe UI", Font.BOLD, 13));
        p.add(new JScrollPane(table), BorderLayout.CENTER);

        JButton logoutBtn = new JButton("Close Dashboard");
        logoutBtn.addActionListener(e -> dash.dispose());
        p.add(logoutBtn, BorderLayout.SOUTH);

        dash.setContentPane(p);
        dash.setVisible(true);
    }

    private void openAdminWindow(UserAccount user) {
        JFrame dash = new JFrame("JanMitra AI — Admin Control Center");
        dash.setSize(680, 520);
        dash.setLocationRelativeTo(this);

        JPanel p = new JPanel(new BorderLayout(16, 16));
        p.setBorder(new EmptyBorder(24, 24, 24, 24));
        p.setBackground(new Color(248, 250, 252));

        JLabel welcome = new JLabel("<html><h2 style='color:#7C3AED;margin:0;'>Portal Admin Control Center 🛡️</h2>" +
                "<p style='color:#475569;'>Master database view of all registered citizens and scheme submissions.</p></html>");
        p.add(welcome, BorderLayout.NORTH);

        String[] cols = {"ID", "Citizen Name", "Email", "State", "Income", "Category"};
        String[][] allApps = {
            {"#1", "Aditi Sharma", "aditi@example.com", "Rajasthan", "₹180,000", "Education"},
            {"#2", "Unit Test Citizen", "unittest@example.com", "Rajasthan", "₹200,000", "Education"},
            {"#3", "Parv Jain", "parvjain248@gmail.com", "Rajasthan", "₹100,000", "Social Welfare"}
        };
        JTable table = new JTable(allApps, cols);
        table.setRowHeight(28);
        p.add(new JScrollPane(table), BorderLayout.CENTER);

        JButton closeBtn = new JButton("Close Admin View");
        closeBtn.addActionListener(e -> dash.dispose());
        p.add(closeBtn, BorderLayout.SOUTH);

        dash.setContentPane(p);
        dash.setVisible(true);
    }

    private void openWebEligibility() {
        try {
            Desktop.getDesktop().browse(new URI("http://127.0.0.1:5000/check-eligibility"));
        } catch (Exception ex) {
            JOptionPane.showMessageDialog(this, "Please open http://127.0.0.1:5000/check-eligibility in your web browser.", "Open Browser", JOptionPane.INFORMATION_MESSAGE);
        }
    }

    private static String hashPassword(String password) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] hash = md.digest(password.getBytes(StandardCharsets.UTF_8));
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) hexString.append('0');
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (NoSuchAlgorithmException e) {
            return Integer.toString(password.hashCode());
        }
    }

    static class UserAccount {
        String name;
        String email;
        String passwordHash;
        String role;
        String state;
        int income;
        String category;

        UserAccount(String name, String email, String passwordHash, String role, String state, int income, String category) {
            this.name = name;
            this.email = email;
            this.passwordHash = passwordHash;
            this.role = role;
            this.state = state;
            this.income = income;
            this.category = category;
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            try {
                UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
            } catch (Exception ignored) {}
            new JanMitraLoginApp().setVisible(true);
        });
    }
}
