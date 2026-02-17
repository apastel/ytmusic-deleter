from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QTextEdit
from PySide6.QtWidgets import QVBoxLayout


class DebugReportPreviewDialog(QDialog):
    def __init__(self, app_log_preview, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preview Debug Report")
        self.confirmed = False

        layout = QVBoxLayout()

        # Title input
        title_label = QLabel("Issue Title: <span style='color: red;'>*</span>")
        layout.addWidget(title_label)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g., 'App says I have no playlists but I do'")
        self.title_input.textChanged.connect(self.clear_title_error)
        layout.addWidget(self.title_input)

        # Error label (hidden by default)
        self.title_error_label = QLabel("Please provide a title for your issue")
        self.title_error_label.setStyleSheet("QLabel { color: red; }")
        self.title_error_label.hide()
        layout.addWidget(self.title_error_label)

        # Add spacing before description
        layout.addSpacing(15)

        # Optional description
        desc_label = QLabel("Describe what happened in more detail:")
        layout.addWidget(desc_label)

        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        self.description_input.setPlaceholderText("Any additional context that might help...")
        layout.addWidget(self.description_input)

        # Add spacing before contact info
        layout.addSpacing(15)

        # Optional contact info
        contact_label = QLabel(
            "Optional: Contact info (email or Discord username) if you wish to be contacted regarding this problem:"
        )
        layout.addWidget(contact_label)

        self.contact_input = QLineEdit()
        self.contact_input.setPlaceholderText("e.g., 'yourname@email.com' or 'YourDiscordName'")
        layout.addWidget(self.contact_input)

        # Add spacing before logs
        layout.addSpacing(15)

        # Log preview (editable so user can redact)
        logs_label = QLabel("Technical logs (you can edit to remove sensitive info):")
        layout.addWidget(logs_label)

        self.log_viewer = QTextEdit()
        self.log_viewer.setPlainText(app_log_preview)
        layout.addWidget(self.log_viewer)

        # Alternative reporting options
        alt_report_label = QLabel(
            "You can also report bugs or check for known issues on "
            "<a href='https://discord.gg/8TCX6Q8hrh'>Discord</a> or "
            "<a href='https://github.com/apastel/ytmusic-deleter/issues'>GitHub</a>."
        )
        alt_report_label.setOpenExternalLinks(True)
        alt_report_label.setWordWrap(True)
        alt_report_label.setStyleSheet(
            "QLabel { color: #666; font-size: 11px; margin-top: 10px; margin-bottom: 10px; }"
        )
        layout.addWidget(alt_report_label)

        # Add a small spacer before buttons
        layout.addSpacing(10)

        # Buttons in horizontal layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # Push buttons to the right

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_cancel.setMaximumWidth(100)
        button_layout.addWidget(btn_cancel)

        btn_send = QPushButton("Send Report")
        btn_send.clicked.connect(self.validate_and_accept)
        btn_send.setMaximumWidth(120)
        button_layout.addWidget(btn_send)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.resize(800, 600)

        # Store original stylesheet
        self.title_input_original_style = self.title_input.styleSheet()

    def validate_and_accept(self):
        """Validate title before accepting"""
        if not self.title_input.text().strip():
            # Show error
            self.title_input.setStyleSheet("QLineEdit { border: 2px solid red; }")
            self.title_error_label.show()
            # Focus on the title field
            self.title_input.setFocus()
        else:
            # Valid, close dialog
            self.accept()

    def clear_title_error(self):
        """Clear error styling when user starts typing"""
        if self.title_input.text().strip():
            self.title_input.setStyleSheet(self.title_input_original_style)
            self.title_error_label.hide()

    def get_edited_logs(self):
        """Return potentially edited logs"""
        return self.log_viewer.toPlainText()

    def get_user_title(self):
        """Return the issue title"""
        return self.title_input.text().strip()

    def get_user_description(self):
        """Return the description"""
        return self.description_input.toPlainText().strip()

    def get_user_contact(self):
        """Return the contact info"""
        return self.contact_input.text().strip()
