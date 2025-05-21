from pathlib import Path

current_dir = Path(__file__)
src_dir = current_dir.parent.parent.parent
backup_dir = src_dir / "backup"
media_dir = src_dir / "media"
