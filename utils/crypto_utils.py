from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import base64
import os
from config import SECRET_KEY

# 使用环境变量或默认值设置密钥和IV
CRYPTO_KEY = os.environ.get('CRYPTO_KEY', SECRET_KEY).encode()[:32]
CRYPTO_IV = os.environ.get('CRYPTO_IV', 'JPY0IbolqwiPFpKC').encode()[:16]

def encrypt_data(data):
    cipher = Cipher(algorithms.AES(CRYPTO_KEY), modes.CBC(CRYPTO_IV), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    if isinstance(data, str):
        data = data.encode()
    padded_data = padder.update(data) + padder.finalize()
    encrypted = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(encrypted).decode('utf-8')

def decrypt_data(encrypted_data):
    cipher = Cipher(algorithms.AES(CRYPTO_KEY), modes.CBC(CRYPTO_IV), backend=default_backend())
    decryptor = cipher.decryptor()
    encrypted = base64.b64decode(encrypted_data.encode())
    decrypted_padded = decryptor.update(encrypted) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()
    return decrypted.decode()
