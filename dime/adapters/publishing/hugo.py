from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any


class HugoPublishingAdapter:
    """PublishingAdapter that writes content to a Hugo site content directory.

    Emits a markdown file with JSON frontmatter and touches a signal file
    to trigger a Hugo rebuild watcher.
    """

    _SIGNAL_FILE = ".rebuild-signal"

    def __init__(self, content_dir: str) -> None:
        self._content_dir = Path(content_dir)
        self._content_dir.mkdir(parents=True, exist_ok=True)

    async def emit(
        self,
        article_id: uuid.UUID,
        content: str,
        frontmatter: dict[str, Any],
    ) -> None:
        fm_json = json.dumps(frontmatter, indent=2, default=str)
        doc = f"{fm_json}\n\n{content}"
        dest = self._content_dir / f"{article_id}.md"
        dest.write_text(doc, encoding="utf-8")

    def signal(self) -> None:
        signal_path = self._content_dir / self._SIGNAL_FILE
        signal_path.touch()

    def preview_url(self) -> str | None:
        return None
