from pathlib import Path


def path_from(local_path) -> Path:
    return Path(str(local_path))
