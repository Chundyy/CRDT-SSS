"""
File Encryption Utilities for NetGuardian
Handles file encryption and decryption for secure storage
"""

import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import logging

logger = logging.getLogger(__name__)

class FileEncryption:
    def __init__(self, password=None):
        """Initialize encryption with password or default key"""
        if password:
            self.key = self._derive_key_from_password(password)
        else:
            # Use default key for development (in production, use proper key management)
            self.key = self._get_or_create_default_key()
        
        try:
            self.fernet = Fernet(self.key)
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            # Fallback to simple XOR encryption
            self.fernet = None
            self.xor_key = b"NetGuardianDefaultKey2024"
    
    def _derive_key_from_password(self, password):
        """Derive encryption key from password"""
        try:
            password_bytes = password.encode()
            salt = b'NetGuardianSalt2024'  # In production, use random salt per user
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
            return key
        except Exception as e:
            logger.error(f"Key derivation failed: {e}")
            return self._get_fallback_key()
    
    def _get_or_create_default_key(self):
        """Get or create default encryption key"""
        key_file = "encryption.key"
        
        try:
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    return f.read()
            else:
                # Generate new key
                key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(key)
                logger.info("Generated new encryption key")
                return key
        except Exception as e:
            logger.error(f"Key file handling failed: {e}")
            return self._get_fallback_key()
    
    def _get_fallback_key(self):
        """Get fallback key when Fernet is not available"""
        fallback_key = "NetGuardianDefaultEncryptionKey2024!@#"
        return base64.urlsafe_b64encode(fallback_key.encode()[:32].ljust(32, b'0'))
    
    def encrypt_file(self, input_path, output_path):
        """Encrypt a file"""
        try:
            with open(input_path, 'rb') as infile:
                data = infile.read()
            
            if self.fernet:
                encrypted_data = self.fernet.encrypt(data)
            else:
                # Fallback XOR encryption
                encrypted_data = self._xor_encrypt_decrypt(data)
            
            with open(output_path, 'wb') as outfile:
                outfile.write(encrypted_data)
            
            logger.info(f"File encrypted: {input_path} -> {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"File encryption failed: {e}")
            return False
    
    def decrypt_file(self, input_path, output_path):
        """Decrypt a file"""
        try:
            with open(input_path, 'rb') as infile:
                encrypted_data = infile.read()
            
            if self.fernet:
                decrypted_data = self.fernet.decrypt(encrypted_data)
            else:
                # Fallback XOR decryption
                decrypted_data = self._xor_encrypt_decrypt(encrypted_data)
            
            with open(output_path, 'wb') as outfile:
                outfile.write(decrypted_data)
            
            logger.info(f"File decrypted: {input_path} -> {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"File decryption failed: {e}")
            return False
    
    def encrypt_data(self, data):
        """Encrypt raw data"""
        try:
            if isinstance(data, str):
                data = data.encode()
            
            if self.fernet:
                return self.fernet.encrypt(data)
            else:
                return self._xor_encrypt_decrypt(data)
                
        except Exception as e:
            logger.error(f"Data encryption failed: {e}")
            return data
    
    def decrypt_data(self, encrypted_data):
        """Decrypt raw data"""
        try:
            if self.fernet:
                return self.fernet.decrypt(encrypted_data)
            else:
                return self._xor_encrypt_decrypt(encrypted_data)
                
        except Exception as e:
            logger.error(f"Data decryption failed: {e}")
            return encrypted_data
    
    def _xor_encrypt_decrypt(self, data):
        """Simple XOR encryption/decryption fallback"""
        try:
            result = bytearray()
            key_len = len(self.xor_key)
            
            for i, byte in enumerate(data):
                result.append(byte ^ self.xor_key[i % key_len])
            
            return bytes(result)
            
        except Exception as e:
            logger.error(f"XOR encryption failed: {e}")
            return data
    
    def is_encryption_available(self):
        """Check if strong encryption is available"""
        return self.fernet is not None


class PasswordManager:
    """Simple password hashing utilities"""
    
    @staticmethod
    def hash_password(password):
        """Hash a password (fallback implementation)"""
        try:
            import hashlib
            import secrets
            
            salt = secrets.token_hex(16)
            password_hash = hashlib.pbkdf2_hmac('sha256', 
                                               password.encode(), 
                                               salt.encode(), 
                                               100000)
            return salt + ':' + password_hash.hex()
            
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            # Simple fallback
            import hashlib
            return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password, hashed_password):
        """Verify a password against its hash"""
        try:
            if ':' in hashed_password:
                # PBKDF2 format
                import hashlib
                salt, stored_hash = hashed_password.split(':')
                password_hash = hashlib.pbkdf2_hmac('sha256',
                                                   password.encode(),
                                                   salt.encode(),
                                                   100000)
                return stored_hash == password_hash.hex()
            else:
                # Simple SHA256 fallback
                import hashlib
                return hashlib.sha256(password.encode()).hexdigest() == hashed_password
                
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False