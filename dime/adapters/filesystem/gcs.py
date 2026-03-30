from __future__ import annotations

from google.cloud import storage  # type: ignore[import-untyped]


class GCSFileSystemAdapter:
    """FileSystemAdapter backed by Google Cloud Storage.

    Used for images only — markdown content always lives on the local filesystem.
    """

    def __init__(self, bucket_name: str, prefix: str = "") -> None:
        self._bucket_name = bucket_name
        self._prefix = prefix.rstrip("/")
        self._client: storage.Client = storage.Client()  # type: ignore[reportUnknownMemberType]
        self._bucket = self._client.bucket(bucket_name)  # type: ignore[reportUnknownMemberType]

    def _blob_name(self, path: str) -> str:
        if self._prefix:
            return f"{self._prefix}/{path}"
        return path

    def read(self, path: str) -> str:
        blob = self._bucket.blob(self._blob_name(path))  # type: ignore[reportUnknownMemberType]
        return blob.download_as_text(encoding="utf-8")  # type: ignore[reportUnknownMemberType]

    def write(self, path: str, content: str) -> None:
        blob = self._bucket.blob(self._blob_name(path))  # type: ignore[reportUnknownMemberType]
        blob.upload_from_string(content, content_type="text/plain; charset=utf-8")  # type: ignore[reportUnknownMemberType]

    def exists(self, path: str) -> bool:
        blob = self._bucket.blob(self._blob_name(path))  # type: ignore[reportUnknownMemberType]
        return blob.exists()  # type: ignore[reportUnknownMemberType]

    def list(self, prefix: str) -> list[str]:
        full_prefix = self._blob_name(prefix) if prefix else self._prefix
        blobs = self._client.list_blobs(self._bucket_name, prefix=full_prefix)  # type: ignore[reportUnknownMemberType]
        strip = f"{self._prefix}/" if self._prefix else ""
        return [
            b.name[len(strip) :] if strip and b.name.startswith(strip) else b.name  # type: ignore[reportUnknownMemberType,reportUnknownVariableType]
            for b in blobs  # type: ignore[reportUnknownVariableType]
        ]
