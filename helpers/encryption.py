def aes_encrypt(in_file, out_file):
    """
    Standard AES encryption (non-chunked, no HMAC).
    Format: IV || Encrypted Data
    """
    iv = os.urandom(IV_SIZE)
    out_file.write(iv)
    data = in_file.read()
    cipher = Cipher(algorithms.AES(aes_key), modes.CTR(iv), backend=backend)
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data) + encryptor.finalize()
    out_file.write(encrypted_data)

def aes_decrypt(in_file, out_file):
    """
    Standard AES decryption (non-chunked, no HMAC).
    Expects: IV || Encrypted Data
    """
    iv = in_file.read(IV_SIZE)
    ciphertext = in_file.read()
    cipher = Cipher(algorithms.AES(aes_key), modes.CTR(iv), backend=backend)
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
    out_file.write(decrypted_data)
def decrypt_non_chunked(in_file, out_file):
    """
    Decrypts a file-like object (in_file) and writes the result to out_file.
    Non-chunked mode: reads all ciphertext at once.
    Verifies the HMAC tag before returning.
    Raises ValueError if the tag is invalid.
    """
    in_file.seek(0, os.SEEK_END)
    total_size = in_file.tell()
    in_file.seek(0)

    if total_size < IV_SIZE + TAG_SIZE:
        raise ValueError("Invalid encrypted file: file is too small.")

    iv = in_file.read(IV_SIZE)
    ciphertext_size = total_size - IV_SIZE - TAG_SIZE
    ciphertext = in_file.read(ciphertext_size)
    tag = in_file.read(TAG_SIZE)

    h = hmac.HMAC(hmac_key, hashes.SHA256(), backend=backend)
    h.update(iv)
    h.update(ciphertext)
    try:
        h.verify(tag)
    except InvalidTag:
        raise ValueError("HMAC verification failed: file is corrupt or has been tampered with.")

    cipher = Cipher(algorithms.AES(aes_key), modes.CTR(iv), backend=backend)
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
    out_file.write(decrypted_data)
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidTag

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, 'data')
os.makedirs(DATA_PATH, exist_ok=True)
AES_KEY_PATH = os.path.join(DATA_PATH, 'aes_encryption.key')
HMAC_KEY_PATH = os.path.join(DATA_PATH, 'aes_hmac.key')

def load_or_generate_key(path):
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return f.read()
    else:
        key = os.urandom(32)
        with open(path, 'wb') as f:
            f.write(key)
        return key

aes_key = load_or_generate_key(AES_KEY_PATH)
hmac_key = load_or_generate_key(HMAC_KEY_PATH)

backend = default_backend()
IV_SIZE = 16  # AES block size
CHUNK_SIZE = 65536  # 64KB
TAG_SIZE = 32  # HMAC-SHA256 output size

def encrypt_chunked(in_file, out_file):
    """
    Encrypts a file-like object (in_file) and writes the result to another
    file-like object (out_file) using AES-CTR with HMAC-SHA256 for authentication.
    Format: IV || Encrypted Data || HMAC Tag
    Chunked mode: processes file in chunks.
    """
    iv = os.urandom(IV_SIZE)
    out_file.write(iv)

    cipher = Cipher(algorithms.AES(aes_key), modes.CTR(iv), backend=backend)
    encryptor = cipher.encryptor()
    h = hmac.HMAC(hmac_key, hashes.SHA256(), backend=backend)
    h.update(iv)

    while True:
        chunk = in_file.read(CHUNK_SIZE)
        if not chunk:
            break
        encrypted_chunk = encryptor.update(chunk)
        h.update(encrypted_chunk)
        out_file.write(encrypted_chunk)

    encrypted_chunk = encryptor.finalize()
    if encrypted_chunk:
        h.update(encrypted_chunk)
        out_file.write(encrypted_chunk)

    tag = h.finalize()
    out_file.write(tag)

def encrypt_non_chunked(in_file, out_file):
    """
    Encrypts the entire file in memory (non-chunked mode).
    Format: IV || Encrypted Data || HMAC Tag
    """
    iv = os.urandom(IV_SIZE)
    out_file.write(iv)

    data = in_file.read()
    cipher = Cipher(algorithms.AES(aes_key), modes.CTR(iv), backend=backend)
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data) + encryptor.finalize()

    h = hmac.HMAC(hmac_key, hashes.SHA256(), backend=backend)
    h.update(iv)
    h.update(encrypted_data)
    tag = h.finalize()

    out_file.write(encrypted_data)
    out_file.write(tag)
    """
    Decrypts a file-like object (in_file) and writes the result to out_file.
    Verifies the HMAC tag before returning.
    Raises ValueError if the tag is invalid.
    """
    in_file.seek(0, os.SEEK_END)
    total_size = in_file.tell()
    in_file.seek(0)

    if total_size < IV_SIZE + TAG_SIZE:
        raise ValueError("Invalid encrypted file: file is too small.")

    iv = in_file.read(IV_SIZE)
    
    in_file.seek(total_size - TAG_SIZE)
    tag = in_file.read(TAG_SIZE)
    
    in_file.seek(IV_SIZE)
    
    h = hmac.HMAC(hmac_key, hashes.SHA256(), backend=backend)
    h.update(iv)

    cipher = Cipher(algorithms.AES(aes_key), modes.CTR(iv), backend=backend)
    decryptor = cipher.decryptor()

    ciphertext_size = total_size - IV_SIZE - TAG_SIZE
    bytes_read = 0
    while bytes_read < ciphertext_size:
        chunk_size = min(CHUNK_SIZE, ciphertext_size - bytes_read)
        chunk = in_file.read(chunk_size)
        if not chunk:
            break
        h.update(chunk)
        decrypted_chunk = decryptor.update(chunk)
        out_file.write(decrypted_chunk)
        bytes_read += len(chunk)

    decrypted_chunk = decryptor.finalize()
    if decrypted_chunk:
        out_file.write(decrypted_chunk)
    
    try:
        h.verify(tag)
    except InvalidTag:
        raise ValueError("HMAC verification failed: file is corrupt or has been tampered with.")