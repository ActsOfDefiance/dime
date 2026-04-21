"""Tests for AstroAdapter."""

from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from dime.adapters.protocols import PublishingAdapter
from dime.adapters.publishing.astro import AstroAdapter


def _make_adapter(
    tmp_path: Path,
    preview_host: str = "",
) -> tuple[AstroAdapter, Path, Path, Path]:
    """Return (adapter, art_dir, public_dir, signal_file)."""
    art_dir = tmp_path / "art"
    art_dir.mkdir()
    public_dir = tmp_path / "public" / "images" / "articles"
    public_dir.mkdir(parents=True)
    signal_file = tmp_path / ".rebuild-signal"

    adapter = AstroAdapter(
        art_dir=str(art_dir),
        acts_of_defiance_public_dir=str(public_dir),
        signal_file_path=str(signal_file),
        content_base=str(tmp_path / "compendium"),
        preview_host=preview_host,
    )
    return adapter, art_dir, public_dir, signal_file


# ---------------------------------------------------------------------------
# Protocol compliance
# ---------------------------------------------------------------------------


class TestProtocolCompliance:
    def test_astro_is_publishing_adapter(self, tmp_path: Path) -> None:
        adapter, *_ = _make_adapter(tmp_path)
        assert isinstance(adapter, PublishingAdapter)


# ---------------------------------------------------------------------------
# emit()
# ---------------------------------------------------------------------------


class TestEmit:
    @pytest.mark.asyncio
    async def test_emit_copies_hero_image(self, tmp_path: Path) -> None:
        adapter, art_dir, public_dir, _ = _make_adapter(tmp_path)

        slug = "frantz-fanon"
        (art_dir / slug).mkdir()
        src_img = art_dir / slug / "hero.jpg"
        src_img.write_bytes(b"fake-image-data")

        await adapter.emit(
            article_id=uuid.uuid4(),
            content="# Frantz Fanon",
            frontmatter={"slug": slug, "images": {"hero": "hero.jpg"}},
        )

        dest = public_dir / slug / "hero.jpg"
        assert dest.exists()
        assert dest.read_bytes() == b"fake-image-data"

    @pytest.mark.asyncio
    async def test_emit_creates_dest_dir(self, tmp_path: Path) -> None:
        adapter, art_dir, public_dir, _ = _make_adapter(tmp_path)

        slug = "new-article"
        (art_dir / slug).mkdir()
        (art_dir / slug / "hero.png").write_bytes(b"img")

        await adapter.emit(
            article_id=uuid.uuid4(),
            content="",
            frontmatter={"slug": slug, "images": {"hero": "hero.png"}},
        )

        assert (public_dir / slug).is_dir()
        assert (public_dir / slug / "hero.png").exists()

    @pytest.mark.asyncio
    async def test_emit_is_idempotent(self, tmp_path: Path) -> None:
        adapter, art_dir, public_dir, _ = _make_adapter(tmp_path)

        slug = "idempotent-article"
        (art_dir / slug).mkdir()
        src = art_dir / slug / "hero.jpg"
        src.write_bytes(b"version-1")

        article_id = uuid.uuid4()
        fm = {"slug": slug, "images": {"hero": "hero.jpg"}}

        await adapter.emit(article_id=article_id, content="", frontmatter=fm)
        # Overwrite source with different content
        src.write_bytes(b"version-2")
        await adapter.emit(article_id=article_id, content="", frontmatter=fm)

        dest = public_dir / slug / "hero.jpg"
        assert dest.exists()
        assert dest.read_bytes() == b"version-2"

    @pytest.mark.asyncio
    async def test_emit_no_images_is_safe(self, tmp_path: Path) -> None:
        adapter, *_ = _make_adapter(tmp_path)
        # Should not raise even with empty images dict
        await adapter.emit(
            article_id=uuid.uuid4(),
            content="",
            frontmatter={"slug": "no-images"},
        )

    @pytest.mark.asyncio
    async def test_emit_missing_image_logs_warning_does_not_raise(
        self, tmp_path: Path
    ) -> None:
        adapter, art_dir, public_dir, _ = _make_adapter(tmp_path)
        slug = "missing-img"
        (art_dir / slug).mkdir()
        # Do NOT create the source image

        await adapter.emit(
            article_id=uuid.uuid4(),
            content="",
            frontmatter={"slug": slug, "images": {"hero": "nonexistent.jpg"}},
        )

        assert not (public_dir / slug / "nonexistent.jpg").exists()

    @pytest.mark.asyncio
    async def test_emit_uses_article_id_as_slug_fallback(self, tmp_path: Path) -> None:
        adapter, art_dir, public_dir, _ = _make_adapter(tmp_path)
        article_id = uuid.uuid4()
        slug_fallback = str(article_id)
        (art_dir / slug_fallback).mkdir()
        (art_dir / slug_fallback / "hero.jpg").write_bytes(b"data")

        await adapter.emit(
            article_id=article_id,
            content="",
            frontmatter={"images": {"hero": "hero.jpg"}},  # no slug key
        )

        assert (public_dir / slug_fallback / "hero.jpg").exists()

    @pytest.mark.asyncio
    async def test_emit_copies_multiple_images(self, tmp_path: Path) -> None:
        adapter, art_dir, public_dir, _ = _make_adapter(tmp_path)
        slug = "multi-img"
        (art_dir / slug).mkdir()
        (art_dir / slug / "hero.jpg").write_bytes(b"hero")
        (art_dir / slug / "thumb.png").write_bytes(b"thumb")

        await adapter.emit(
            article_id=uuid.uuid4(),
            content="",
            frontmatter={
                "slug": slug,
                "images": {"hero": "hero.jpg", "thumb": "thumb.png"},
            },
        )

        assert (public_dir / slug / "hero.jpg").exists()
        assert (public_dir / slug / "thumb.png").exists()

    @pytest.mark.asyncio
    async def test_emit_skips_empty_image_filename(self, tmp_path: Path) -> None:
        adapter, art_dir, public_dir, _ = _make_adapter(tmp_path)
        slug = "empty-filename"
        (art_dir / slug).mkdir()

        await adapter.emit(
            article_id=uuid.uuid4(),
            content="",
            frontmatter={"slug": slug, "images": {"hero": ""}},
        )

        # No files should be created for empty filename
        assert (
            not list((public_dir / slug).glob("*"))
            if (public_dir / slug).exists()
            else True
        )


# ---------------------------------------------------------------------------
# signal()
# ---------------------------------------------------------------------------


class TestSignal:
    def test_signal_creates_file(self, tmp_path: Path) -> None:
        adapter, _, _, signal_file = _make_adapter(tmp_path)
        assert not signal_file.exists()
        adapter.signal()
        assert signal_file.exists()

    def test_signal_is_idempotent(self, tmp_path: Path) -> None:
        adapter, _, _, signal_file = _make_adapter(tmp_path)
        adapter.signal()
        adapter.signal()
        assert signal_file.exists()

    def test_signal_creates_parent_dirs(self, tmp_path: Path) -> None:
        signal_file = tmp_path / "deep" / "nested" / ".signal"
        adapter = AstroAdapter(
            art_dir=str(tmp_path),
            acts_of_defiance_public_dir=str(tmp_path),
            signal_file_path=str(signal_file),
        )
        adapter.signal()
        assert signal_file.exists()


# ---------------------------------------------------------------------------
# preview_url()
# ---------------------------------------------------------------------------


class TestPreviewUrl:
    def test_preview_url_with_host(self, tmp_path: Path) -> None:
        adapter, *_ = _make_adapter(tmp_path, preview_host="localhost:4321")
        url = adapter.preview_url()
        assert url == "http://localhost:4321"

    def test_preview_url_none_when_no_host(self, tmp_path: Path) -> None:
        adapter, *_ = _make_adapter(tmp_path, preview_host="")
        assert adapter.preview_url() is None
