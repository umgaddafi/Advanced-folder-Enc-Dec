import os
import zipfile
import shutil

def zip_folder(folder_path: str, zip_path: str, progress_callback=None):
    """
    Creates a zip archive of a folder and reports progress.

    Args:
        folder_path (str): The path to the folder to zip.
        zip_path (str): The path to save the new zip file.
        progress_callback (callable, optional): A function to call with
                                                 (current_bytes, total_bytes).
    """
    total_size = 0
    for root, _, files in os.walk(folder_path):
        for file in files:
            total_size += os.path.getsize(os.path.join(root, file))

    bytes_written = 0
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, folder_path)
                zipf.write(full_path, arcname)
                bytes_written += os.path.getsize(full_path)
                if progress_callback:
                    progress_callback(bytes_written, total_size)

def unzip_folder(zip_path: str, extract_to: str, progress_callback=None):
    """
    Extracts a zip archive and reports progress.

    Args:
        zip_path (str): The path to the zip file.
        extract_to (str): The path to extract the contents to.
        progress_callback (callable, optional): A function to call with
                                                 (current_bytes, total_bytes).
    """
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        total_size = sum(file.file_size for file in zipf.infolist())
        bytes_extracted = 0
        for file in zipf.infolist():
            zipf.extract(file, extract_to)
            bytes_extracted += file.file_size
            if progress_callback:
                progress_callback(bytes_extracted, total_size)

def delete_path(path: str):
    """Deletes a file or directory."""
    if os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)