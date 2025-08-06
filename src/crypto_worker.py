import os
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
import sys
import subprocess

from .core_crypto import encrypt_file_aes, decrypt_file_aes
from .file_operations import zip_folder, unzip_folder, delete_path

class CryptoWorker(QObject):
    """
    Worker class to perform encryption and decryption in a separate thread.
    Emits signals for progress, completion, and errors.
    """
    progress_updated = pyqtSignal(int)
    encryption_finished = pyqtSignal(str, str)
    decryption_finished = pyqtSignal(str, str)
    error_occurred = pyqtSignal(str)

    def __init__(self, mode: str, path: str, password: str, output_path: str = None,
                 delete_source: bool = False, export_hashes: bool = False,
                 import_hashes: bool = False):
        """
        Initializes the CryptoWorker.

        Args:
            mode (str): "encrypt" or "decrypt".
            path (str): Input file or folder path.
            password (str): Password for the operation.
            output_path (str, optional): Output path for encrypted/decrypted file.
            delete_source (bool): Whether to delete the source after operation.
            export_hashes (bool): Whether to export salt file during encryption.
            import_hashes (bool): Whether to import salt file during decryption.
        """
        super().__init__()
        self.mode = mode
        self.path = path
        self.password = password
        self.output_path = output_path
        self.delete_source = delete_source
        self.export_hashes = export_hashes
        self.import_hashes = import_hashes
        
    def run(self):
        """Executes the encryption or decryption operation based on the mode."""
        try:
            if self.mode == "encrypt":
                out_path = self._encrypt_folder_threaded()
                self.encryption_finished.emit("Encryption complete.", out_path)
            elif self.mode == "decrypt":
                out_path = self._decrypt_folder_threaded()
                self.decryption_finished.emit("Decryption complete.", out_path)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def _zip_progress(self, current_bytes, total_bytes):
        """Callback for zip progress, mapping to 0-10% of overall progress."""
        progress = int((current_bytes / total_bytes) * 10)
        self.progress_updated.emit(progress)

    def _encryption_file_progress(self, current_bytes, total_bytes):
        """Callback for file encryption progress, mapping to 10-90% of overall progress."""
        # Scale encryption progress from 10 to 90%
        progress = 10 + int((current_bytes / total_bytes) * 80)
        self.progress_updated.emit(progress)

    def _decryption_file_progress(self, current_bytes, total_bytes):
        """Callback for file decryption progress, mapping to 0-90% of overall progress."""
        # Scale decryption progress from 0 to 90%
        progress = int((current_bytes / total_bytes) * 90)
        self.progress_updated.emit(progress)

    def _unzip_progress(self, current_bytes, total_bytes):
        """Callback for unzip progress, mapping to 90-100% of overall progress."""
        progress = 90 + int((current_bytes / total_bytes) * 10)
        self.progress_updated.emit(progress)

    def _encrypt_folder_threaded(self):
        """Handles the multi-step encryption process for a folder."""
        self.progress_updated.emit(0)
        temp_zip = self.path + ".zip"
        
        zip_folder(self.path, temp_zip, progress_callback=self._zip_progress)
        
        encrypt_file_aes(temp_zip, self.output_path, self.password,
                         self.export_hashes, progress_callback=self._encryption_file_progress)
        
        self.progress_updated.emit(95)
        delete_path(temp_zip)
        
        if self.delete_source:
            delete_path(self.path)
        self.progress_updated.emit(100)
        return self.output_path

    def _decrypt_folder_threaded(self):
        """Handles the multi-step decryption process for an encrypted file."""
        self.progress_updated.emit(0)
        file_dir = os.path.dirname(self.path)
        base_name_enc = os.path.basename(self.path)
        base_name_zip = os.path.splitext(base_name_enc)[0]

        output_folder_path = os.path.join(file_dir, base_name_zip)
        os.makedirs(output_folder_path, exist_ok=True)
        temp_zip = os.path.join(output_folder_path, f"{base_name_zip}_temp.zip")

        decrypt_file_aes(self.path, temp_zip, self.password,
                         self.import_hashes, progress_callback=self._decryption_file_progress)
        
        unzip_folder(temp_zip, output_folder_path, progress_callback=self._unzip_progress)
        
        self.progress_updated.emit(95)
        delete_path(temp_zip)

        delete_path(self.path)
        if self.import_hashes and os.path.exists(self.path + ".salt"):
            delete_path(self.path + ".salt")

        self.progress_updated.emit(100)
        return output_folder_path

    def open_explorer_and_highlight(self, file_path):
        """Opens file explorer and highlights the given file/folder."""
        if os.name == 'nt':  # For Windows
            subprocess.Popen(f'explorer /select,"{os.path.normpath(file_path)}"')
        elif os.name == 'posix': # For macOS and Linux
            if sys.platform == 'darwin':
                subprocess.Popen(['open', '-R', file_path])
            else:
                subprocess.Popen(['xdg-open', os.path.dirname(file_path)])