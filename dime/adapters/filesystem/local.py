from __future__ import annotations

from pathlib import Path


class LocalFileSystemAdapter:
    """FileSystemAdapter backed by the local filesystem.

    All paths are relative to base_path (the compendium/ root).
    """

    def __init__(self, base_path: str) -> None:
        self._base = Path(base_path)
        self._base.mkdir(parents=True, exist_ok=True)

    def _resolve(self, path: str) -> Path:
        return self._base / path

    def read(self, path: str) -> str:
        return self._resolve(path).read_text(encoding="utf-8")

    def write(self, path: str, content: str) -> None:
        resolved = self._resolve(path)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content, encoding="utf-8")

    def exists(self, path: str) -> bool:
        return self._resolve(path).exists()

    def list(self, prefix: str) -> list[str]:
        base = self._resolve(prefix)
        if not base.exists():
            return []
        return [str(p.relative_to(self._base)) for p in base.rglob("*") if p.is_file()]
