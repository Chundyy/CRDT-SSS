"""
File Handler for NetGuardian
Manages file upload, download, and storage operations with encryption support
"""

import os
import shutil
import hashlib
import uuid
from datetime import datetime
from typing import Tuple, List, Dict, Any, Optional
import logging

from src.utils.encryption import FileEncryption
from config.settings import Config, UIConstants

logger = logging.getLogger(__name__)

class FileHandler:
    """
    Handles all file operations including upload, download, delete, and storage management.
    
    Features:
    - File upload with duplicate detection
    - Optional encryption support
    - File hash calculation for integrity
    - Storage statistics tracking
    - Orphaned file cleanup
    
    Attributes:
        db_manager: Database manager instance
        user_id: Current user's ID
        storage_path: Base storage directory path
        max_file_size: Maximum allowed file size in bytes
        encryption: FileEncryption instance for file encryption
        user_storage_path: User-specific storage directory
    """
    
    def __init__(self, db_manager, user_id: int) -> None:
        """
        Initialize FileHandler for a specific user.
        
        Args:
            db_manager: DatabaseManager instance
            user_id: User ID for file operations
            
        Raises:
            OSError: If storage directory cannot be created
        """
        self.db_manager = db_manager
        self.user_id: int = user_id
        self.storage_path: str = Config.LOCAL_STORAGE_PATH
        self.max_file_size: int = Config.MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes
        self.encryption = FileEncryption()
        
        # Ensure user storage directory exists
        self.user_storage_path: str = os.path.join(self.storage_path, f"user_{user_id}")
        try:
            if not os.path.exists(self.user_storage_path):
                os.makedirs(self.user_storage_path, exist_ok=True)
                logger.info(f"Created user storage directory: {self.user_storage_path}")
        except OSError as e:
            logger.error(f"Failed to create storage directory: {e}")
            raise
    
    def upload_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Upload a file to user's storage with validation and duplicate detection.
        
        Args:
            file_path: Absolute path to the file to upload
            
        Returns:
            tuple: (success: bool, message: str)
            
        Process:
        1. Validates file existence, size, and emptiness
        2. Generates unique filename with UUID
        3. Calculates SHA-256 hash for duplicate detection
        4. Copies file to user storage
        5. Optionally encrypts the file
        6. Saves metadata to database
        """
        stored_path: Optional[str] = None
        
        try:
            # Validate file existence
            if not os.path.exists(file_path):
                logger.warning(f"Upload attempted for non-existent file: {file_path}")
                return False, "File does not exist"
            
            if not os.path.isfile(file_path):
                return False, "Path is not a file"
            
            # Validate file size
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                logger.warning(f"File too large: {file_size} bytes (limit: {self.max_file_size})")
                return False, UIConstants.ERROR_FILE_SIZE
            
            if file_size == 0:
                return False, "Cannot upload empty files"
            
            # Generate unique filename
            original_name = os.path.basename(file_path)
            unique_id = str(uuid.uuid4())
            file_extension = os.path.splitext(original_name)[1].lower()
            stored_filename = f"{unique_id}{file_extension}"
            stored_path = os.path.join(self.user_storage_path, stored_filename)
            
            # Calculate file hash for duplicate detection
            file_hash = self._calculate_file_hash(file_path)
            if not file_hash:
                return False, "Failed to calculate file hash"
            
            # Check for duplicate files by hash
            existing_file = self.db_manager.execute_query(
                "SELECT id, original_name FROM files WHERE user_id = ? AND file_hash = ? AND is_deleted = 0",
                (self.user_id, file_hash)
            )
            
            if existing_file:
                duplicate_name = existing_file[0]['original_name']
                logger.info(f"Duplicate file detected: {original_name} matches {duplicate_name}")
                return False, f"File already exists as '{duplicate_name}'"
            
            # Copy file to storage
            shutil.copy2(file_path, stored_path)
            logger.debug(f"File copied to storage: {stored_path}")

            # Mirror to CRDT sync folder if configured (copy before optional encryption)
            try:
                if hasattr(Config, 'SYNC_TO_CRDT') and Config.SYNC_TO_CRDT:
                    crdt_base = Config.CRDT_SYNC_FOLDER
                    # If CRDT sync folder already points to 'lww', use it; otherwise use crdt_base/lww
                    if os.path.basename(os.path.normpath(crdt_base)) == 'lww':
                        dest_dir = crdt_base
                    else:
                        dest_dir = os.path.join(crdt_base, 'lww')

                    # Ensure destination exists; exist_ok avoids error if it already exists
                    os.makedirs(dest_dir, exist_ok=True)

                    # Use the original filename but avoid overwriting existing files
                    crdt_dest = os.path.join(dest_dir, original_name)
                    try:
                        if os.path.exists(crdt_dest):
                            base_name, ext = os.path.splitext(original_name)
                            counter = 1
                            while True:
                                new_name = f"{base_name}_{counter}{ext}"
                                candidate = os.path.join(dest_dir, new_name)
                                if not os.path.exists(candidate):
                                    crdt_dest = candidate
                                    break
                                counter += 1

                        shutil.copy2(file_path, crdt_dest)
                        logger.debug(f"Mirrored file to CRDT sync folder: {crdt_dest}")
                    except Exception as crdt_err:
                        logger.error(f"Failed to copy file to CRDT folder: {crdt_err}")
            except Exception:
                # Non-fatal if mirroring fails
                pass

            # Encrypt file if enabled
            if hasattr(Config, 'ENCRYPT_FILES') and Config.ENCRYPT_FILES:
                encrypted_path = stored_path + '.enc'
                try:
                    self.encryption.encrypt_file(stored_path, encrypted_path)
                    os.remove(stored_path)  # Remove unencrypted file
                    stored_path = encrypted_path
                    stored_filename += '.enc'
                    logger.debug(f"File encrypted: {encrypted_path}")
                except Exception as enc_error:
                    logger.error(f"Encryption failed: {enc_error}")
                    # Continue without encryption
            
            # Save file metadata to database
            self.db_manager.execute_query(
                """INSERT INTO files (user_id, filename, original_name, file_path, 
                   file_size, file_hash, upload_date) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (self.user_id, stored_filename, original_name, stored_path, 
                 file_size, file_hash, datetime.now())
            )
            
            logger.info(f"File uploaded: '{original_name}' ({self._format_file_size(file_size)}) -> {stored_filename}")
            return True, UIConstants.SUCCESS_UPLOAD
            
        except PermissionError as e:
            logger.error(f"Permission denied during file upload: {e}")
            self._cleanup_file(stored_path)
            return False, "Permission denied - cannot access file"
        except OSError as e:
            logger.error(f"OS error during file upload: {e}")
            self._cleanup_file(stored_path)
            return False, "Storage error - disk may be full"
        except Exception as e:
            logger.error(f"Unexpected error during file upload: {e}", exc_info=True)
            self._cleanup_file(stored_path)
            return False, UIConstants.ERROR_UPLOAD
    
    def download_file(self, file_id: int, destination_path: str) -> Tuple[bool, str]:
        """
        Download a file from storage to destination path.
        
        Args:
            file_id: Database ID of the file to download
            destination_path: Where to save the downloaded file
            
        Returns:
            tuple: (success: bool, message: str)
            
        Note:
            Automatically decrypts files if they are encrypted
        """
        temp_path: Optional[str] = None
        
        try:
            # Get file metadata
            file_data = self.db_manager.execute_query(
                "SELECT * FROM files WHERE id = ? AND user_id = ? AND is_deleted = 0",
                (file_id, self.user_id)
            )
            
            if not file_data:
                logger.warning(f"Download attempted for non-existent file ID: {file_id}")
                return False, "File not found or access denied"
            
            file_data = file_data[0]
            stored_path = file_data['file_path']
            original_name = file_data['original_name']
            
            if not os.path.exists(stored_path):
                logger.error(f"File exists in DB but not on disk: {stored_path}")
                return False, "File not found in storage"
            
            # Handle encrypted files
            if stored_path.endswith('.enc'):
                # Decrypt to temporary location
                temp_path = stored_path[:-4]  # Remove .enc extension
                try:
                    self.encryption.decrypt_file(stored_path, temp_path)
                    source_path = temp_path
                    cleanup_temp = True
                    logger.debug(f"File decrypted for download: {temp_path}")
                except Exception as dec_error:
                    logger.error(f"Decryption failed: {dec_error}")
                    return False, "Failed to decrypt file"
            else:
                source_path = stored_path
                cleanup_temp = False
            
            # Copy file to destination
            shutil.copy2(source_path, destination_path)
            
            # Cleanup temporary decrypted file
            if cleanup_temp and temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                    logger.debug(f"Cleaned up temporary file: {temp_path}")
                except Exception:
                    pass  # Non-critical error
            
            logger.info(f"File downloaded: '{original_name}' to {destination_path}")
            return True, "File downloaded successfully"
            
        except PermissionError as e:
            logger.error(f"Permission denied during download: {e}")
            self._cleanup_file(temp_path)
            return False, "Permission denied - cannot write to destination"
        except Exception as e:
            logger.error(f"Unexpected error during download: {e}", exc_info=True)
            self._cleanup_file(temp_path)
            return False, "Download failed"
    
    def delete_file(self, file_id: int) -> Tuple[bool, str]:
        """
        Delete a file from storage and mark as deleted in database.
        
        Args:
            file_id: Database ID of the file to delete
            
        Returns:
            tuple: (success: bool, message: str)
            
        Note:
            Soft delete in database, hard delete from disk
        """
        try:
            # Get file metadata
            file_data = self.db_manager.execute_query(
                "SELECT * FROM files WHERE id = ? AND user_id = ? AND is_deleted = 0",
                (file_id, self.user_id)
            )
            
            if not file_data:
                logger.warning(f"Delete attempted for non-existent file ID: {file_id}")
                return False, "File not found or access denied"
            
            file_data = file_data[0]
            stored_path = file_data['file_path']
            original_name = file_data['original_name']
            
            # Mark file as deleted in database (soft delete)
            self.db_manager.execute_query(
                "UPDATE files SET is_deleted = 1 WHERE id = ?",
                (file_id,)
            )
            
            # Remove physical file (hard delete)
            if os.path.exists(stored_path):
                try:
                    os.remove(stored_path)
                    logger.debug(f"Physical file removed: {stored_path}")
                except OSError as e:
                    logger.warning(f"Could not remove physical file: {e}")
                    # Database already marked as deleted, so continue
            
            logger.info(f"File deleted: '{original_name}' (ID: {file_id})")
            return True, UIConstants.SUCCESS_DELETE
            
        except Exception as e:
            logger.error(f"File deletion failed for ID {file_id}: {e}", exc_info=True)
            return False, UIConstants.ERROR_DELETE
    
    def get_user_files(self) -> List[Dict[str, Any]]:
        """
        Get all non-deleted files for the current user.
        
        Returns:
            list: List of file dictionaries with metadata
        """
        try:
            # If configured to use CRDT sync folder as main source, enumerate files there
            if hasattr(Config, 'USE_CRDT_AS_MAIN') and Config.USE_CRDT_AS_MAIN:
                crdt_base = Config.CRDT_SYNC_FOLDER
                crdt_lww = os.path.join(crdt_base, 'lww')
                scan_dir = crdt_lww if os.path.exists(crdt_lww) else crdt_base

                if os.path.exists(scan_dir):
                    result = []
                    for root, dirs, files in os.walk(scan_dir):
                        for fname in files:
                            if fname.startswith('.') or fname.endswith('.swp'):
                                continue
                            fpath = os.path.join(root, fname)
                            try:
                                stat = os.stat(fpath)
                                size = stat.st_size
                                date_str = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                            except Exception:
                                size = 0
                                date_str = ''

                            file_ext = os.path.splitext(fname)[1].lower()

                            result.append({
                                'id': None,
                                'filename': fname,
                                'original_name': fname,
                                'file_size': size,
                                'file_size_formatted': self._format_file_size(size),
                                'file_hash': None,
                                'upload_date': date_str,
                                'file_extension': file_ext,
                                'file_path': fpath
                            })
                    logger.debug(f"Retrieved {len(result)} files from CRDT sync folder: {scan_dir}")
                    return result
                # Fall through to DB if CRDT folder missing

            files = self.db_manager.execute_query(
                """SELECT id, filename, original_name, file_size, file_hash, upload_date 
                   FROM files WHERE user_id = ? AND is_deleted = 0 
                   ORDER BY upload_date DESC""",
                (self.user_id,)
            )
            
            # Convert to enhanced list of dictionaries
            result = []
            for file_data in files:
                # Format upload date
                upload_date = file_data['upload_date']
                if hasattr(upload_date, 'strftime'):
                    date_str = upload_date.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    date_str = str(upload_date)
                
                # Get file extension
                file_ext = os.path.splitext(file_data['original_name'])[1].lower()
                
                result.append({
                    'id': file_data['id'],
                    'filename': file_data['filename'],
                    'original_name': file_data['original_name'],
                    'file_size': file_data['file_size'],
                    'file_size_formatted': self._format_file_size(file_data['file_size']),
                    'file_hash': file_data['file_hash'],
                    'upload_date': date_str,
                    'file_extension': file_ext
                })
            
            logger.debug(f"Retrieved {len(result)} files for user {self.user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get user files: {e}", exc_info=True)
            return []
    
    def get_file_info(self, file_id):
        """Get detailed information about a file"""
        try:
            file_data = self.db_manager.execute_query(
                "SELECT * FROM files WHERE id = ? AND user_id = ? AND is_deleted = 0",
                (file_id, self.user_id)
            )
            
            if not file_data:
                return None
            
            file_data = file_data[0]
            
            # Add additional info
            stored_path = file_data['file_path']
            exists_on_disk = os.path.exists(stored_path)
            
            return {
                'id': file_data['id'],
                'filename': file_data['filename'],
                'original_name': file_data['original_name'],
                'file_size': file_data['file_size'],
                'file_hash': file_data['file_hash'],
                'upload_date': file_data['upload_date'],
                'file_path': stored_path,
                'exists_on_disk': exists_on_disk,
                'size_mb': file_data['file_size'] / (1024 * 1024),
                'is_encrypted': stored_path.endswith('.enc')
            }
            
        except Exception as e:
            logger.error(f"Failed to get file info: {e}")
            return None
    
    def get_storage_stats(self):
        """Get storage statistics for the user"""
        try:
            stats = self.db_manager.execute_query(
                """SELECT 
                   COUNT(*) as total_files,
                   SUM(file_size) as total_size
                   FROM files WHERE user_id = ? AND is_deleted = 0""",
                (self.user_id,)
            )
            
            if stats:
                stats = stats[0]
                total_size_mb = (stats['total_size'] or 0) / (1024 * 1024)
                return {
                    'total_files': stats['total_files'] or 0,
                    'total_size_bytes': stats['total_size'] or 0,
                    'total_size_mb': total_size_mb,
                    'storage_limit_mb': Config.MAX_FILE_SIZE_MB,
                    'available_space_mb': max(0, Config.MAX_FILE_SIZE_MB - total_size_mb)
                }
            
            return {
                'total_files': 0,
                'total_size_bytes': 0,
                'total_size_mb': 0,
                'storage_limit_mb': Config.MAX_FILE_SIZE_MB,
                'available_space_mb': Config.MAX_FILE_SIZE_MB
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return None
    
    def _calculate_file_hash(self, file_path: str) -> Optional[str]:
        """
        Calculate SHA-256 hash of a file for duplicate detection.
        
        Args:
            file_path: Path to file to hash
            
        Returns:
            str or None: Hex digest of SHA-256 hash, or None on error
        """
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                # Read in 64KB chunks for efficiency
                for chunk in iter(lambda: f.read(65536), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except IOError as e:
            logger.error(f"IO error calculating file hash: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calculating file hash: {e}")
            return None
    
    def _cleanup_file(self, file_path: Optional[str]) -> None:
        """
        Safely remove a file, ignoring errors.
        
        Args:
            file_path: Path to file to remove
        """
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.debug(f"Cleaned up file: {file_path}")
            except Exception as e:
                logger.warning(f"Could not cleanup file {file_path}: {e}")
    
    def _format_file_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: File size in bytes
            
        Returns:
            str: Formatted size (e.g., "1.5 MB", "234 KB")
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def cleanup_orphaned_files(self):
        """Clean up files that exist on disk but not in database"""
        try:
            # Get all files in user storage directory
            if not os.path.exists(self.user_storage_path):
                return
            
            disk_files = set(os.listdir(self.user_storage_path))
            
            # Get all files in database
            db_files = self.db_manager.execute_query(
                "SELECT filename FROM files WHERE user_id = ?",
                (self.user_id,)
            )
            
            db_filenames = set(file_data['filename'] for file_data in db_files)
            
            # Find orphaned files
            orphaned_files = disk_files - db_filenames
            
            # Remove orphaned files
            for filename in orphaned_files:
                file_path = os.path.join(self.user_storage_path, filename)
                try:
                    os.remove(file_path)
                    logger.info(f"Removed orphaned file: {filename}")
                except Exception as e:
                    logger.error(f"Failed to remove orphaned file {filename}: {e}")
            
            return len(orphaned_files)
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return 0