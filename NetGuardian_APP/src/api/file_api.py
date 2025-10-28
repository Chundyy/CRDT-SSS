from fastapi import APIRouter, UploadFile, File, HTTPException, Header
from fastapi.responses import FileResponse
import os
from typing import List, Optional
import io
import tempfile

# Robust import for DatabaseManager: support running as package or standalone
try:
    from database.db_manager import DatabaseManager
except Exception:
    try:
        from src.database.db_manager import DatabaseManager
    except Exception:
        # Fallback: load module directly by path
        import importlib.util
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'db_manager.py'))
        spec = importlib.util.spec_from_file_location('database.db_manager', db_path)
        db_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(db_mod)  # type: ignore
        DatabaseManager = db_mod.DatabaseManager

# Optional SFTP support
try:
    import paramiko
    _HAS_PARAMIKO = True
except Exception:
    _HAS_PARAMIKO = False

# Configuration: choose mode 'local' (direct filesystem) or 'sftp' (upload to remote server)
SYNC_MODE = os.getenv('CRDT_SYNC_MODE', 'local')  # 'local' or 'sftp'
SYNC_FOLDER = os.getenv('CRDT_SYNC_FOLDER', '/opt/crdt-cluster/sync_folder/lww')

# SFTP configuration (used when SYNC_MODE == 'sftp')
SFTP_HOST = os.getenv('CRDT_SYNC_SFTP_HOST', '161.230.48.199')
SFTP_PORT = int(os.getenv('CRDT_SYNC_SFTP_PORT', '22'))
SFTP_USER = os.getenv('CRDT_SYNC_SFTP_USER', '')
SFTP_PASSWORD = os.getenv('CRDT_SYNC_SFTP_PASSWORD', '')
SFTP_KEY_PATH = os.getenv('CRDT_SYNC_SFTP_KEY_PATH', '')  # optional private key file
SFTP_REMOTE_PATH = os.getenv('CRDT_SYNC_SFTP_REMOTE_PATH', SYNC_FOLDER)

# Per-region node overrides (useful for Porto/Lisbon)
NODE_PORTO_HOST = os.getenv('NODE_PORTO_HOST', SFTP_HOST)
NODE_PORTO_PORT = int(os.getenv('NODE_PORTO_PORT', '51230'))
NODE_LISBON_HOST = os.getenv('NODE_LISBON_HOST', SFTP_HOST)
NODE_LISBON_PORT = int(os.getenv('NODE_LISBON_PORT', '51231'))

router = APIRouter()


def _get_port_from_session(session_token: Optional[str]) -> Optional[int]:
    """Query DB using session_token to determine user's group/region and map to port."""
    if not session_token:
        return None
    try:
        db = DatabaseManager()
        # find user row linked to session
        row = db.execute_query(
            "SELECT u.* FROM sessions s JOIN users u ON s.user_id = u.id WHERE s.session_token = ? AND s.is_active = 1",
            (session_token,)
        )
        if not row:
            return None
        user = row[0]
        # check common field names that might indicate region/group
        for key in ('region', 'group', 'group_name', 'office', 'location'):
            val = user.get(key)
            if val:
                v = str(val).strip().lower()
                if 'porto' in v:
                    return NODE_PORTO_PORT
                if 'lisbon' in v or 'lisboa' in v:
                    return NODE_LISBON_PORT
        return None
    except Exception:
        return None


def _select_node_for_region(region: Optional[str], session_token: Optional[str]):
    """Return (host, port) using explicit region header, or session->group mapping, else fallback."""
    # explicit header wins
    if region:
        r = region.strip().lower()
        if r == 'porto' or r == 'port':
            return NODE_PORTO_HOST or SFTP_HOST, NODE_PORTO_PORT
        if r == 'lisbon' or r == 'lisboa' or r == 'l':
            return NODE_LISBON_HOST or SFTP_HOST, NODE_LISBON_PORT
    # try session-based mapping
    port = _get_port_from_session(session_token)
    if port:
        return SFTP_HOST, port
    # fallback
    return SFTP_HOST, SFTP_PORT


def _sftp_client(host: str, port: int):
    """Create and return an SFTP client connected to host:port. Caller must close transport/client."""
    if not _HAS_PARAMIKO:
        raise RuntimeError("paramiko is required for SFTP mode. Install with: pip install paramiko")

    transport = paramiko.Transport((host, port))
    if SFTP_KEY_PATH:
        private_key = paramiko.RSAKey.from_private_key_file(SFTP_KEY_PATH)
        transport.connect(username=SFTP_USER, pkey=private_key)
    else:
        transport.connect(username=SFTP_USER, password=SFTP_PASSWORD)

    sftp = paramiko.SFTPClient.from_transport(transport)
    return transport, sftp


@router.post("/upload/")
async def upload_file(file: UploadFile = File(...), x_client_region: Optional[str] = Header(None), x_session_token: Optional[str] = Header(None)):
    try:
        content = await file.read()

        if SYNC_MODE == 'sftp':
            host, port = _select_node_for_region(x_client_region, x_session_token)
            transport, sftp = _sftp_client(host, port)
            try:
                # Ensure remote directory exists (try to create, ignore errors)
                try:
                    sftp.chdir(SFTP_REMOTE_PATH)
                except IOError:
                    # attempt to create directories recursively
                    parts = SFTP_REMOTE_PATH.strip('/').split('/')
                    cur = ''
                    for p in parts:
                        cur = cur + '/' + p
                        try:
                            sftp.mkdir(cur)
                        except Exception:
                            pass
                    sftp.chdir(SFTP_REMOTE_PATH)

                remote_path = os.path.join(SFTP_REMOTE_PATH, file.filename)
                # Use putfo with BytesIO
                bio = io.BytesIO(content)
                sftp.putfo(bio, remote_path)
            finally:
                try:
                    sftp.close()
                except Exception:
                    pass
                try:
                    transport.close()
                except Exception:
                    pass

        else:
            # local filesystem mode
            os.makedirs(SYNC_FOLDER, exist_ok=True)
            file_location = os.path.join(SYNC_FOLDER, file.filename)
            with open(file_location, "wb") as f:
                f.write(content)

        return {"filename": file.filename}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/", response_model=List[str])
def list_files(x_client_region: Optional[str] = Header(None), x_session_token: Optional[str] = Header(None)):
    try:
        if SYNC_MODE == 'sftp':
            host, port = _select_node_for_region(x_client_region, x_session_token)
            transport, sftp = _sftp_client(host, port)
            try:
                files = sftp.listdir(SFTP_REMOTE_PATH)
                return files
            finally:
                try:
                    sftp.close()
                except Exception:
                    pass
                try:
                    transport.close()
                except Exception:
                    pass
        else:
            return os.listdir(SYNC_FOLDER)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{filename}")
def download_file(filename: str, x_client_region: Optional[str] = Header(None), x_session_token: Optional[str] = Header(None)):
    try:
        if SYNC_MODE == 'sftp':
            host, port = _select_node_for_region(x_client_region, x_session_token)
            transport, sftp = _sftp_client(host, port)
            try:
                remote_path = os.path.join(SFTP_REMOTE_PATH, filename)
                # Download to temporary file and return
                tmp = tempfile.NamedTemporaryFile(delete=False)
                try:
                    sftp.get(remote_path, tmp.name)
                    return FileResponse(tmp.name, filename=filename)
                finally:
                    # do not delete tmp immediately; OS will clean up later
                    pass
            finally:
                try:
                    sftp.close()
                except Exception:
                    pass
                try:
                    transport.close()
                except Exception:
                    pass

        else:
            file_path = os.path.join(SYNC_FOLDER, filename)
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found")
            return FileResponse(file_path, filename=filename)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
