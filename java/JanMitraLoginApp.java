package java_auth;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HashMap;
import java.util.Map;

/**
 * JanMitra AI - Java GUI Login & Registration Application
 * A full working graphical authentication interface built with Java Swing.
 */
public class JanMitraLoginApp extends JFrame {

    // In-memory user database (with default demo user)
    private static final Map<String, UserAccount> userDatabase = new HashMap<>();

    static {
        // Pre-populate with demo citizen
        userDatabase.put("demo@janmitra.gov.in", new UserAccount(
            "Demo Citizen",
            "demo@janmitra.gov.in",
            hashPassword("Password@123"),
            "citizen"
        ));
    }

    private JTextField loginEmailField;
    private JPasswordField loginPasswordField;
    private JTextField regNameField;
    private JTextField regEmailField;
    private JPasswordField regPasswordField;
    private JPasswordField regConfirmPasswordField;
    private JTabbedPane tabbedPane;

    public JanMitraLoginApp() {
        setTitle("JanMitra AI — Citizen Portal Authentication");
        setSize(520, 640);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        setResizable(false);

        // Main background panel
        JPanel mainPanel = new JPanel(new BorderLayout());
        mainPanel.setBackground(new Color(248, 250, 252));
        setContentPane(mainPanel);

        // Header Panel
        JPanel headerPanel = createHeaderPanel();
        mainPanel.add(headerPanel, BorderLayout.NORTH);

        // Tabs (Login / Register)
        tabbedPane = new JTabbedPane();
        tabbedPane.setFont(new Font("Segoe UI", Font.BOLD, 14));
        tabbedPane.addTab("Citizen Login", createLoginPanel());
        tabbedPane.addTab("New Registration", createRegisterPanel());
        mainPanel.add(tabbedPane, BorderLayout.CENTER);

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
        panel.setBorder(new EmptyBorder(24, 20, 24, 20));

        JLabel titleLabel = new JLabel("✦ JanMitra AI");
        titleLabel.setFont(new Font("Segoe UI", Font.BOLD, 24));
        titleLabel.setForeground(Color.WHITE);
        titleLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        JLabel subtitleLabel = new JLabel("Government Schemes & Citizen Welfare Portal");
        subtitleLabel.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        subtitleLabel.setForeground(new Color(219, 234, 254));
        subtitleLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        panel.add(titleLabel);
        panel.add(Box.createVerticalStrut(6));
        panel.add(subtitleLabel);
        return panel;
    }

    private JPanel createLoginPanel() {
        JPanel panel = new JPanel();
        panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
        panel.setBackground(Color.WHITE);
        panel.setBorder(new EmptyBorder(24, 32, 24, 32));

        // Quick Demo Fill Button
        JButton demoBtn = new JButton("⚡ Autofill Demo: demo@janmitra.gov.in");
        demoBtn.setFont(new Font("Segoe UI", Font.BOLD, 12));
        demoBtn.setBackground(new Color(239, 246, 255));
        demoBtn.setForeground(new Color(29, 78, 216));
        demoBtn.setFocusPainted(false);
        demoBtn.setAlignmentX(Component.LEFT_ALIGNMENT);
        demoBtn.setMaximumSize(new Dimension(Integer.MAX_VALUE, 36));
        demoBtn.addActionListener(e -> {
            loginEmailField.setText("demo@janmitra.gov.in");
            loginPasswordField.setText("Password@123");
        });
        panel.add(demoBtn);
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
        panel.add(Box.createVerticalStrut(16));

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
        panel.add(Box.createVerticalStrut(10));

        // Show/hide password
        JCheckBox showPassCheck = new JCheckBox("Show Password");
        showPassCheck.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        showPassCheck.setBackground(Color.WHITE);
        showPassCheck.setAlignmentX(Component.LEFT_ALIGNMENT);
        showPassCheck.addActionListener(e -> {
            if (showPassCheck.isSelected()) {
                loginPasswordField.setEchoChar((char) 0);
            } else {
                loginPasswordField.setEchoChar('•');
            }
        });
        panel.add(showPassCheck);
        panel.add(Box.createVerticalStrut(24));

        // Login Button
        JButton loginBtn = new JButton("Log In to JanMitra");
        loginBtn.setFont(new Font("Segoe UI", Font.BOLD, 15));
        loginBtn.setBackground(new Color(37, 99, 235));
        loginBtn.setForeground(Color.WHITE);
        loginBtn.setFocusPainted(false);
        loginBtn.setAlignmentX(Component.LEFT_ALIGNMENT);
        loginBtn.setMaximumSize(new Dimension(Integer.MAX_VALUE, 44));
        loginBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        loginBtn.addActionListener(e -> handleLogin());
        panel.add(loginBtn);

        return panel;
    }

    private JPanel createRegisterPanel() {
        JPanel panel = new JPanel();
        panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
        panel.setBackground(Color.WHITE);
        panel.setBorder(new EmptyBorder(20, 32, 20, 32));

        // Name
        JLabel nameLabel = new JLabel("Full Name (as per ID):");
        nameLabel.setFont(new Font("Segoe UI", Font.BOLD, 13));
        nameLabel.setAlignmentX(Component.LEFT_ALIGNMENT);
        panel.add(nameLabel);
        panel.add(Box.createVerticalStrut(5));

        regNameField = new JTextField();
        regNameField.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        regNameField.setMaximumSize(new Dimension(Integer.MAX_VALUE, 36));
        regNameField.setAlignmentX(Component.LEFT_ALIGNMENT);
        panel.add(regNameField);
        panel.add(Box.createVerticalStrut(12));

        // Email
        JLabel emailLabel = new JLabel("Email Address:");
        emailLabel.setFont(new Font("Segoe UI", Font.BOLD, 13));
        emailLabel.setAlignmentX(Component.LEFT_ALIGNMENT);
        panel.add(emailLabel);
        panel.add(Box.createVerticalStrut(5));

        regEmailField = new JTextField();
        regEmailField.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        regEmailField.setMaximumSize(new Dimension(Integer.MAX_VALUE, 36));
        regEmailField.setAlignmentX(Component.LEFT_ALIGNMENT);
        panel.add(regEmailField);
        panel.add(Box.createVerticalStrut(12));

        // Password
        JLabel passLabel = new JLabel("Password (min 6 characters):");
        passLabel.setFont(new Font("Segoe UI", Font.BOLD, 13));
        passLabel.setAlignmentX(Component.LEFT_ALIGNMENT);
        panel.add(passLabel);
        panel.add(Box.createVerticalStrut(5));

        regPasswordField = new JPasswordField();
        regPasswordField.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        regPasswordField.setMaximumSize(new Dimension(Integer.MAX_VALUE, 36));
        regPasswordField.setAlignmentX(Component.LEFT_ALIGNMENT);
        panel.add(regPasswordField);
        panel.add(Box.createVerticalStrut(12));

        // Confirm Password
        JLabel confirmLabel = new JLabel("Confirm Password:");
        confirmLabel.setFont(new Font("Segoe UI", Font.BOLD, 13));
        confirmLabel.setAlignmentX(Component.LEFT_ALIGNMENT);
        panel.add(confirmLabel);
        panel.add(Box.createVerticalStrut(5));

        regConfirmPasswordField = new JPasswordField();
        regConfirmPasswordField.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        regConfirmPasswordField.setMaximumSize(new Dimension(Integer.MAX_VALUE, 36));
        regConfirmPasswordField.setAlignmentX(Component.LEFT_ALIGNMENT);
        panel.add(regConfirmPasswordField);
        panel.add(Box.createVerticalStrut(20));

        // Register Button
        JButton regBtn = new JButton("Create Citizen Account");
        regBtn.setFont(new Font("Segoe UI", Font.BOLD, 15));
        regBtn.setBackground(new Color(16, 185, 129));
        regBtn.setForeground(Color.WHITE);
        regBtn.setFocusPainted(false);
        regBtn.setAlignmentX(Component.LEFT_ALIGNMENT);
        regBtn.setMaximumSize(new Dimension(Integer.MAX_VALUE, 44));
        regBtn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        regBtn.addActionListener(e -> handleRegister());
        panel.add(regBtn);

        return panel;
    }

    private void handleLogin() {
        String email = loginEmailField.getText().trim();
        String password = new String(loginPasswordField.getPassword());

        if (email.isEmpty() || password.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Please enter both email and password.", "Missing Fields", JOptionPane.WARNING_MESSAGE);
            return;
        }

        UserAccount user = userDatabase.get(email.toLowerCase());
        if (user != null && user.passwordHash.equals(hashPassword(password))) {
            JOptionPane.showMessageDialog(this, "Login successful!\nWelcome back, " + user.name + "!", "Authentication Successful", JOptionPane.INFORMATION_MESSAGE);
            openDashboardWindow(user);
        } else {
            JOptionPane.showMessageDialog(this, "Invalid email or password. Please try again.", "Authentication Failed", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void handleRegister() {
        String name = regNameField.getText().trim();
        String email = regEmailField.getText().trim().toLowerCase();
        String password = new String(regPasswordField.getPassword());
        String confirm = new String(regConfirmPasswordField.getPassword());

        if (name.isEmpty() || email.isEmpty() || password.isEmpty()) {
            JOptionPane.showMessageDialog(this, "All fields are required.", "Missing Fields", JOptionPane.WARNING_MESSAGE);
            return;
        }
        if (!email.contains("@") || !email.contains(".")) {
            JOptionPane.showMessageDialog(this, "Please enter a valid email address.", "Invalid Email", JOptionPane.WARNING_MESSAGE);
            return;
        }
        if (password.length() < 6) {
            JOptionPane.showMessageDialog(this, "Password must be at least 6 characters.", "Weak Password", JOptionPane.WARNING_MESSAGE);
            return;
        }
        if (!password.equals(confirm)) {
            JOptionPane.showMessageDialog(this, "Passwords do not match.", "Password Mismatch", JOptionPane.WARNING_MESSAGE);
            return;
        }
        if (userDatabase.containsKey(email)) {
            JOptionPane.showMessageDialog(this, "An account with this email already exists. Please log in.", "Duplicate Account", JOptionPane.ERROR_MESSAGE);
            return;
        }

        UserAccount newUser = new UserAccount(name, email, hashPassword(password), "citizen");
        userDatabase.put(email, newUser);

        JOptionPane.showMessageDialog(this, "Account created successfully!\nYou can now log in with your credentials.", "Registration Success", JOptionPane.INFORMATION_MESSAGE);
        loginEmailField.setText(email);
        loginPasswordField.setText(password);
        tabbedPane.setSelectedIndex(0);
    }

    private void openDashboardWindow(UserAccount user) {
        JFrame dash = new JFrame("JanMitra AI — Citizen Dashboard");
        dash.setSize(600, 480);
        dash.setLocationRelativeTo(this);

        JPanel p = new JPanel(new BorderLayout(16, 16));
        p.setBorder(new EmptyBorder(24, 24, 24, 24));
        p.setBackground(new Color(248, 250, 252));

        JLabel welcome = new JLabel("<html><h2>Welcome, " + user.name + " 👋</h2><p style='color:#475569;'>Email: " + user.email + " | Role: " + user.role + "</p></html>");
        p.add(welcome, BorderLayout.NORTH);

        String[] columnNames = {"Scheme Name", "Category", "Benefit"};
        String[][] data = {
            {"PM-KISAN", "Agriculture", "₹6,000 / year income support"},
            {"NMMS Scholarship", "Education", "₹12,000 / year scholarship"},
            {"PMMY Mudra Loan", "Business", "Loans up to ₹10 Lakh collateral-free"},
            {"Ayushman Bharat", "Healthcare", "₹5 Lakh family health cover"}
        };
        JTable table = new JTable(data, columnNames);
        table.setRowHeight(28);
        table.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        table.getTableHeader().setFont(new Font("Segoe UI", Font.BOLD, 13));
        p.add(new JScrollPane(table), BorderLayout.CENTER);

        JButton logoutBtn = new JButton("Logout");
        logoutBtn.addActionListener(e -> dash.dispose());
        p.add(logoutBtn, BorderLayout.SOUTH);

        dash.setContentPane(p);
        dash.setVisible(true);
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

        UserAccount(String name, String email, String passwordHash, String role) {
            this.name = name;
            this.email = email;
            this.passwordHash = passwordHash;
            this.role = role;
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
