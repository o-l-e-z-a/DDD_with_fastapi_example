from __future__ import annotations

from pathlib import Path

from libcloud.storage.drivers.local import LocalStorageDriver
from sqlalchemy_file.storage import StorageManager

from src.infrastructure.db.utils import media_dir

mail_files_dir = media_dir / Path("mail_files")

mail_files_dir.mkdir(parents=True, exist_ok=True, mode=0o777)
container = LocalStorageDriver(str(media_dir)).get_container("mail_files")
StorageManager.add_storage("mail_files", container)
