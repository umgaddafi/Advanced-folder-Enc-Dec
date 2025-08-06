import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def generate_salt():
    """Generates a random salt for key derivation."""
    return os.urandom(16)

def derive_key(password: str, salt: bytes) -> bytes:
    """
    Derives a cryptographic key from a password and salt using PBKDF2HMAC.

    Args:
        password (str): The user's password.
        salt (bytes): The salt generated for key derivation.

    Returns:
        bytes: The derived cryptographic key.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def encrypt_file_aes(input_path: str, output_path: str, password: str, export_hashes: bool = False, progress_callback=None):
    """
    Encrypts a file using AES in CBC mode with PBKDF2 key derivation.

    Args:
        input_path (str): Path to the file to encrypt.
        output_path (str): Path where the encrypted file will be saved.
        password (str): The password for encryption.
        export_hashes (bool): If True, exports the salt to a .salt file.
        progress_callback (callable, optional): A function to call with
                                                 (current_progress_percentage).
        
    """
    salt = generate_salt()
    key = derive_key(password, salt)
    iv = os.urandom(16)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(algorithms.AES.block_size).padder()

    file_size = os.path.getsize(input_path)
    chunk_size = 65536
    processed_bytes = 0

    with open(input_path, 'rb') as infile, open(output_path, 'wb') as outfile:
        outfile.write(salt)
        outfile.write(iv)

        while True:
            chunk = infile.read(chunk_size)
            if not chunk:
                break
            padded_chunk = padder.update(chunk)
            if padded_chunk:
                outfile.write(encryptor.update(padded_chunk))
            processed_bytes += len(chunk)
            if progress_callback:
                progress_callback(processed_bytes, file_size)

        final_data = padder.finalize()
        outfile.write(encryptor.update(final_data) + encryptor.finalize())

    if export_hashes:
        with open(output_path + ".salt", 'wb') as hash_file:
            hash_file.write(salt)

def decrypt_file_aes(input_path: str, output_path: str, password: str, import_hashes: bool = False, progress_callback=None):
    """
    Decrypts a file using AES in CBC mode with PBKDF2 key derivation.

    Args:
        input_path (str): Path to the encrypted file.
        output_path (str): Path where the decrypted file will be saved.
        password (str): The password for decryption.
        import_hashes (bool): If True, imports the salt from a .salt file.
        progress_callback (callable, optional): A function to call with
                                                 (current_progress_percentage).
    """
    with open(input_path, 'rb') as infile:
        if import_hashes:
            hash_file_path = input_path + ".salt"
            if not os.path.exists(hash_file_path):
                raise FileNotFoundError(f"Salt file not found: {hash_file_path}")
            with open(hash_file_path, 'rb') as hf:
                salt = hf.read()
            iv = infile.read(16)
        else:
            salt = infile.read(16)
            iv = infile.read(16)

        if len(salt) != 16 or len(iv) != 16:
            raise ValueError("Invalid salt or IV length in encrypted file.")

        key = derive_key(password, salt)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()

        file_size = os.path.getsize(input_path) - 32 # Account for salt and IV
        processed_bytes = 0

        with open(output_path, 'wb') as outfile:
            while True:
                chunk = infile.read(65536)
                if not chunk:
                    break
                decrypted_chunk = decryptor.update(chunk)
                if decrypted_chunk:
                    outfile.write(unpadder.update(decrypted_chunk))
                processed_bytes += len(chunk)
                if progress_callback:
                    progress_callback(processed_bytes, file_size)

            try:
                final_data = decryptor.finalize()
                unpadded_data = unpadder.update(final_data)
                unpadded_data += unpadder.finalize()
                outfile.write(unpadded_data)
            except ValueError:
                raise ValueError("Incorrect password or corrupted file.")