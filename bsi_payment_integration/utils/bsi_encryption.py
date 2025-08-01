import base64
import hashlib
import json
from cryptography.hazmat.primitives import padding as aes_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class BSIEncryption:
    @staticmethod
    def _get_key(client_id, secret_key):
        return hashlib.md5((client_id + secret_key).encode()).digest()

    @staticmethod
    def encrypt(data_dict, client_id, secret_key):
        key = BSIEncryption._get_key(client_id, secret_key)

        # JSON to string
        json_data = json.dumps(data_dict, separators=(',', ':')).encode()

        # Padding
        padder = aes_padding.PKCS7(128).padder()
        padded_data = padder.update(json_data) + padder.finalize()

        # AES-128-ECB
        cipher = Cipher(algorithms.AES(key), modes.ECB())
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(padded_data) + encryptor.finalize()

        return base64.b64encode(encrypted).decode()

    @staticmethod
    def decrypt(encoded_data, client_id, secret_key):
        key = BSIEncryption._get_key(client_id, secret_key)

        encrypted = base64.b64decode(encoded_data)

        # AES-128-ECB decrypt
        cipher = Cipher(algorithms.AES(key), modes.ECB())
        decryptor = cipher.decryptor()
        decrypted_padded = decryptor.update(encrypted) + decryptor.finalize()

        # Unpad
        unpadder = aes_padding.PKCS7(128).unpadder()
        decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()

        return json.loads(decrypted.decode())
