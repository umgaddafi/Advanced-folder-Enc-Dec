import os
from PyQt6.QtWidgets import (
    QFrame, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QMessageBox, QLineEdit, QToolButton
)
from PyQt6.QtGui import QIcon, QPixmap, QDragEnterEvent, QDropEvent, QFont, QMovie
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject

class DragDropWidget(QFrame):
    """
    A custom QFrame widget that supports drag-and-drop for files or folders,
    and also provides a browse button.
    """
    def __init__(self, callback=None, is_file_mode=False):
        """
        Initializes the DragDropWidget.

        Args:
            callback (callable, optional): Function to call when a path is selected/dropped.
            is_file_mode (bool): If True, accepts only files; otherwise, accepts only folders.
        """
        super().__init__()
        self.callback = callback
        self.is_file_mode = is_file_mode
        self.setAcceptDrops(True)
        self.setFixedSize(600, 200)
        self.original_text = "Drag & Drop folder here" if not is_file_mode else "Drag & Drop encrypted file here"
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #aaa;
                border-radius: 10px;
                background-color: #f8f8f8;
            }
        """)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QPixmap("./images/cloud.jpeg").scaled(90, 70, Qt.AspectRatioMode.KeepAspectRatio))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.text_label = QLabel(self.original_text)
        self.text_label.setStyleSheet("color: #666; font-size: 18px;")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.or_label = QLabel("Or")
        self.or_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.browse_button = QPushButton("Browse")
        self.browse_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browse_button.setStyleSheet("""
            QPushButton {
                background-color: #0078D4;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005ea6;
            }
        """)
        self.browse_button.clicked.connect(self.browse)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        layout.addWidget(self.or_label)
        layout.addWidget(self.browse_button)
        self.setLayout(layout)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handles drag enter events, accepting if URLs are present."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """Handles drop events, processing the dropped file/folder."""
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if self.is_file_mode:
                if os.path.isfile(path) and path.lower().endswith(".enc"):
                    if self.callback:
                        self.text_label.setText(path)
                        self.callback(path)
                    event.acceptProposedAction()
                    return
                else:
                    QMessageBox.warning(self, "Invalid File", "Only .enc files are allowed.")
            else:  # Folder mode
                if os.path.isdir(path):
                    self.text_label.setText(path)
                    if self.callback:
                        self.callback(path)
                    event.acceptProposedAction()
                    return
                else:
                    QMessageBox.warning(self, "Invalid Input", "Please drop a folder, not a file.")
        event.ignore()

    def browse(self):
        """Opens a file or folder dialog for selection."""
        if self.is_file_mode:
            file, _ = QFileDialog.getOpenFileName(self, "Select Encrypted File", filter="Encrypted Files (*.enc)")
            if file:
                self.text_label.setText(file)
                if self.callback:
                    self.callback(file)
        else:
            folder = QFileDialog.getExistingDirectory(self, "Select Folder")
            if folder:
                self.text_label.setText(folder)
                if self.callback:
                    self.callback(folder)
    
    def reset(self):
        """Resets the widget's text label to its original state."""
        self.text_label.setText(self.original_text)

class PasswordInput(QHBoxLayout):
    """
    A custom layout for a password input field with a show/hide toggle button.
    """
    def __init__(self, placeholder_text="Password"):
        super().__init__()
        self.line_edit = QLineEdit()
        self.line_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.line_edit.setPlaceholderText(placeholder_text)

        self.toggle_button = QToolButton()
        self.toggle_button.setCheckable(True)
        self.toggle_button.setText("🙈")
        self.toggle_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_button.setToolTip("Show/Hide Password")
        self.toggle_button.setStyleSheet("font-size: 16px;")

        self.toggle_button.clicked.connect(self._toggle_visibility)
        self.addWidget(self.line_edit)
        self.addWidget(self.toggle_button)

    def _toggle_visibility(self):
        """Toggles the visibility of the password in the line edit."""
        if self.toggle_button.isChecked():
            self.line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_button.setText("👁️")
        else:
            self.line_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_button.setText("🙈")

    def text(self):
        """Returns the current text in the password input."""
        return self.line_edit.text()

    def clear(self):
        """Clears the text in the password input."""
        self.line_edit.clear()

    def setPlaceholderText(self, text):
        """Sets the placeholder text for the password input."""
        self.line_edit.setPlaceholderText(text)