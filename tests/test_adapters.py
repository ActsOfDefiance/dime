"""
Tests for pluggable adapters.

Unit tests (default run): protocol compliance, local FS, Hugo, WebSocket,
stubs, factory construction, adapter constructors.

Integration tests (@pytest.mark.integration): real Redis round-trip,
GCS instantiation (skipped unless GCS_TEST_BUCKET env var is set).
"""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from dime.adapters.broker.gcppubsub import GCPPubSubBrokerAdapter
from dime.adapters.broker.rabbitmq import RabbitMQBrokerAdapter
from dime.adapters.broker.redis import RedisBrokerAdapter
from dime.adapters.factory import AdapterSet, build_adapters
from dime.adapters.filesystem.gcs import GCSFileSystemAdapter
from dime.adapters.filesystem.local import LocalFileSystemAdapter
from dime.adapters.notification.websocket import WebSocketNotificationAdapter
from dime.adapters.protocols import (
    BrokerAdapter,
    FileSystemAdapter,
    NotificationAdapter,
    PublishingAdapter,
)
from dime.adapters.publishing.astro import AstroAdapter
from dime.adapters.publishing.hugo import HugoPublishingAdapter
from dime.config.settings import reload_settings


# ---------------------------------------------------------------------------
# Protocol compliance
# ---------------------------------------------------------------------------


class TestProtocolCompliance:
    def test_redis_broker_is_broker_adapter(self) -> None:
        with patch("redis.asyncio.from_url"):
            adapter = RedisBrokerAdapter(url="redis://localhost:6379/0")
        assert isinstance(adapter, BrokerAdapter)

    def test_local_fs_is_filesystem_adapter(self, tmp_path: Path) -> None:
        adapter = LocalFileSystemAdapter(base_path=str(tmp_path))
        assert isinstance(adapter, FileSystemAdapter)

    def test_hugo_is_publishing_adapter(self, tmp_path: Path) -> None:
        adapter = HugoPublishingAdapter(content_dir=str(tmp_path))
        assert isinstance(adapter, PublishingAdapter)

    def test_websocket_is_notification_adapter(self) -> None:
        adapter = WebSocketNotificationAdapter()
        assert isinstance(adapter, NotificationAdapter)


# ---------------------------------------------------------------------------
# RedisBrokerAdapter (unit — no live Redis)
# ---------------------------------------------------------------------------


class TestRedisBrokerAdapterUnit:
    def test_stream_key_format(self) -> None:
        with patch("redis.asyncio.from_url"):
            adapter = RedisBrokerAdapter(url="redis://localhost:6379/0")
        assert adapter._stream_key("research") == "dime:tasks:research"  # type: ignore[reportPrivateUsage]

    def test_stream_key_different_types(self) -> None:
        with patch("redis.asyncio.from_url"):
            adapter = RedisBrokerAdapter(url="redis://localhost:6379/0")
        assert adapter._stream_key("write") == "dime:tasks:write"  # type: ignore[reportPrivateUsage]
        assert adapter._stream_key("publish") == "dime:tasks:publish"  # type: ignore[reportPrivateUsage]

    def test_stores_url(self) -> None:
        url = "redis://testhost:6379/2"
        with patch("redis.asyncio.from_url"):
            adapter = RedisBrokerAdapter(url=url)
        assert adapter._url == url  # type: ignore[reportPrivateUsage]


# ---------------------------------------------------------------------------
# BrokerAdapter stubs
# ---------------------------------------------------------------------------


class TestBrokerStubs:
    @pytest.mark.asyncio
    async def test_rabbitmq_dispatch_raises(self) -> None:
        adapter = RabbitMQBrokerAdapter(url="amqp://localhost")
        with pytest.raises(NotImplementedError):
            await adapter.dispatch_task("test", {})

    @pytest.mark.asyncio
    async def test_rabbitmq_consume_raises(self) -> None:
        adapter = RabbitMQBrokerAdapter(url="amqp://localhost")
        with pytest.raises(NotImplementedError):
            await adapter.consume("test", AsyncMock())

    @pytest.mark.asyncio
    async def test_gcppubsub_dispatch_raises(self) -> None:
        adapter = GCPPubSubBrokerAdapter(project_id="test-project")
        with pytest.raises(NotImplementedError):
            await adapter.dispatch_task("test", {})

    @pytest.mark.asyncio
    async def test_gcppubsub_consume_raises(self) -> None:
        adapter = GCPPubSubBrokerAdapter(project_id="test-project")
        with pytest.raises(NotImplementedError):
            await adapter.consume("test", AsyncMock())

    def test_gcppubsub_stores_config(self) -> None:
        adapter = GCPPubSubBrokerAdapter(project_id="my-proj", topic_prefix="myapp")
        assert adapter._project_id == "my-proj"  # type: ignore[reportPrivateUsage]
        assert adapter._topic_prefix == "myapp"  # type: ignore[reportPrivateUsage]

    def test_rabbitmq_stores_url(self) -> None:
        adapter = RabbitMQBrokerAdapter(url="amqp://user:pass@host/vhost")
        assert adapter._url == "amqp://user:pass@host/vhost"  # type: ignore[reportPrivateUsage]


# ---------------------------------------------------------------------------
# LocalFileSystemAdapter
# ---------------------------------------------------------------------------


class TestLocalFileSystemAdapter:
    def test_write_and_read(self, tmp_path: Path) -> None:
        adapter = LocalFileSystemAdapter(base_path=str(tmp_path))
        adapter.write("articles/test.md", "# Hello")
        assert adapter.read("articles/test.md") == "# Hello"

    def test_exists_true(self, tmp_path: Path) -> None:
        adapter = LocalFileSystemAdapter(base_path=str(tmp_path))
        adapter.write("file.txt", "content")
        assert adapter.exists("file.txt") is True

    def test_exists_false(self, tmp_path: Path) -> None:
        adapter = LocalFileSystemAdapter(base_path=str(tmp_path))
        assert adapter.exists("nonexistent.txt") is False

    def test_list_returns_files(self, tmp_path: Path) -> None:
        adapter = LocalFileSystemAdapter(base_path=str(tmp_path))
        adapter.write("subdir/a.md", "a")
        adapter.write("subdir/b.md", "b")
        files = adapter.list("subdir")
        assert len(files) == 2
        assert all(f.startswith("subdir/") for f in files)

    def test_list_empty_prefix(self, tmp_path: Path) -> None:
        adapter = LocalFileSystemAdapter(base_path=str(tmp_path))
        result = adapter.list("nonexistent")
        assert result == []

    def test_write_creates_nested_dirs(self, tmp_path: Path) -> None:
        adapter = LocalFileSystemAdapter(base_path=str(tmp_path))
        adapter.write("deep/nested/dir/file.txt", "hello")
        assert adapter.exists("deep/nested/dir/file.txt")

    def test_base_dir_created_on_init(self, tmp_path: Path) -> None:
        new_dir = str(tmp_path / "new_base")
        adapter = LocalFileSystemAdapter(base_path=new_dir)
        assert Path(new_dir).exists()
        assert adapter._base == Path(new_dir)  # type: ignore[reportPrivateUsage]


# ---------------------------------------------------------------------------
# GCSFileSystemAdapter (unit — mocked client)
# ---------------------------------------------------------------------------


class TestGCSFileSystemAdapterUnit:
    def _make_adapter(
        self, bucket_name: str = "test-bucket", prefix: str = ""
    ) -> GCSFileSystemAdapter:
        with patch("google.cloud.storage.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value = mock_client
            mock_client.bucket.return_value = MagicMock()
            adapter = GCSFileSystemAdapter(bucket_name=bucket_name, prefix=prefix)
            adapter._client = mock_client  # type: ignore[reportPrivateUsage]
            return adapter

    def test_blob_name_no_prefix(self) -> None:
        adapter = self._make_adapter(prefix="")
        assert adapter._blob_name("art/hero.jpg") == "art/hero.jpg"  # type: ignore[reportPrivateUsage]

    def test_blob_name_with_prefix(self) -> None:
        adapter = self._make_adapter(prefix="images")
        assert adapter._blob_name("hero.jpg") == "images/hero.jpg"  # type: ignore[reportPrivateUsage]

    def test_stores_bucket_name(self) -> None:
        adapter = self._make_adapter(bucket_name="my-bucket")
        assert adapter._bucket_name == "my-bucket"  # type: ignore[reportPrivateUsage]


# ---------------------------------------------------------------------------
# HugoPublishingAdapter
# ---------------------------------------------------------------------------


class TestHugoPublishingAdapter:
    @pytest.mark.asyncio
    async def test_emit_creates_file(self, tmp_path: Path) -> None:
        adapter = HugoPublishingAdapter(content_dir=str(tmp_path))
        article_id = uuid.uuid4()
        await adapter.emit(
            article_id=article_id,
            content="## Body text",
            frontmatter={"title": "Test Article", "draft": False},
        )
        dest = tmp_path / f"{article_id}.md"
        assert dest.exists()

    @pytest.mark.asyncio
    async def test_emit_includes_frontmatter(self, tmp_path: Path) -> None:
        adapter = HugoPublishingAdapter(content_dir=str(tmp_path))
        article_id = uuid.uuid4()
        await adapter.emit(
            article_id=article_id,
            content="body",
            frontmatter={"title": "My Title"},
        )
        content = (tmp_path / f"{article_id}.md").read_text()
        assert "My Title" in content
        assert "body" in content

    @pytest.mark.asyncio
    async def test_emit_valid_json_frontmatter(self, tmp_path: Path) -> None:
        adapter = HugoPublishingAdapter(content_dir=str(tmp_path))
        article_id = uuid.uuid4()
        fm = {"title": "T", "tags": ["a", "b"], "draft": True}
        await adapter.emit(article_id=article_id, content="x", frontmatter=fm)
        raw = (tmp_path / f"{article_id}.md").read_text()
        json_part = raw.split("\n\n")[0]
        parsed = json.loads(json_part)
        assert parsed["title"] == "T"
        assert parsed["tags"] == ["a", "b"]

    def test_signal_creates_file(self, tmp_path: Path) -> None:
        adapter = HugoPublishingAdapter(content_dir=str(tmp_path))
        adapter.signal()
        assert (tmp_path / ".rebuild-signal").exists()

    def test_preview_url_returns_none(self, tmp_path: Path) -> None:
        adapter = HugoPublishingAdapter(content_dir=str(tmp_path))
        assert adapter.preview_url() is None

    def test_content_dir_created_on_init(self, tmp_path: Path) -> None:
        new_dir = str(tmp_path / "hugo" / "content")
        adapter = HugoPublishingAdapter(content_dir=new_dir)
        assert Path(new_dir).exists()
        assert adapter._content_dir == Path(new_dir)  # type: ignore[reportPrivateUsage]


# ---------------------------------------------------------------------------
# WebSocketNotificationAdapter
# ---------------------------------------------------------------------------


class TestWebSocketNotificationAdapter:
    def test_initially_no_connections(self) -> None:
        adapter = WebSocketNotificationAdapter()
        assert adapter.connected_users == []

    def test_register_adds_connection(self) -> None:
        adapter = WebSocketNotificationAdapter()
        user_id = uuid.uuid4()
        ws = MagicMock()
        adapter.register(user_id, ws)
        assert user_id in adapter.connected_users

    def test_unregister_removes_connection(self) -> None:
        adapter = WebSocketNotificationAdapter()
        user_id = uuid.uuid4()
        ws = MagicMock()
        adapter.register(user_id, ws)
        adapter.unregister(user_id)
        assert user_id not in adapter.connected_users

    def test_unregister_nonexistent_is_noop(self) -> None:
        adapter = WebSocketNotificationAdapter()
        adapter.unregister(uuid.uuid4())  # should not raise

    @pytest.mark.asyncio
    async def test_notify_sends_to_connected_user(self) -> None:
        adapter = WebSocketNotificationAdapter()
        user_id = uuid.uuid4()
        ws = AsyncMock()
        adapter.register(user_id, ws)
        await adapter.notify("draft_ready", user_id, "Your draft is ready")
        ws.send_text.assert_called_once()
        sent = ws.send_text.call_args[0][0]
        payload = json.loads(sent)
        assert payload["event"] == "draft_ready"
        assert payload["message"] == "Your draft is ready"

    @pytest.mark.asyncio
    async def test_notify_unknown_user_is_noop(self) -> None:
        adapter = WebSocketNotificationAdapter()
        await adapter.notify("event", uuid.uuid4(), "msg")

    @pytest.mark.asyncio
    async def test_notify_only_sends_to_target_user(self) -> None:
        adapter = WebSocketNotificationAdapter()
        user1, user2 = uuid.uuid4(), uuid.uuid4()
        ws1, ws2 = AsyncMock(), AsyncMock()
        adapter.register(user1, ws1)
        adapter.register(user2, ws2)
        await adapter.notify("event", user1, "msg")
        ws1.send_text.assert_called_once()
        ws2.send_text.assert_not_called()


# ---------------------------------------------------------------------------
# AdapterSet factory
# ---------------------------------------------------------------------------


class TestAdapterFactory:
    def test_build_adapters_returns_adapter_set(self, test_env: Any) -> None:
        settings = reload_settings()
        with patch("redis.asyncio.from_url"):
            result = build_adapters(settings)
        assert isinstance(result, AdapterSet)

    def test_build_adapters_broker_is_redis(self, test_env: Any) -> None:
        settings = reload_settings()
        with patch("redis.asyncio.from_url"):
            result = build_adapters(settings)
        assert isinstance(result.broker, RedisBrokerAdapter)

    def test_build_adapters_filesystem_is_local(self, test_env: Any) -> None:
        settings = reload_settings()
        with patch("redis.asyncio.from_url"):
            result = build_adapters(settings)
        assert isinstance(result.filesystem, LocalFileSystemAdapter)

    def test_build_adapters_publishing_is_astro(self, test_env: Any) -> None:
        settings = reload_settings()
        with patch("redis.asyncio.from_url"):
            result = build_adapters(settings)
        assert isinstance(result.publishing, AstroAdapter)

    def test_build_adapters_notification_is_websocket(self, test_env: Any) -> None:
        settings = reload_settings()
        with patch("redis.asyncio.from_url"):
            result = build_adapters(settings)
        assert isinstance(result.notification, WebSocketNotificationAdapter)


# ---------------------------------------------------------------------------
# Integration: Redis round-trip (real Redis required)
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestRedisBrokerIntegration:
    @pytest.mark.asyncio
    async def test_dispatch_consume_round_trip(self) -> None:
        from dime.config.settings import get_settings

        settings = get_settings()
        adapter = RedisBrokerAdapter(url=str(settings.REDIS_URL))
        task_type = f"test-{uuid.uuid4().hex[:8]}"
        sent_payload: dict[str, Any] = {"key": "value", "num": 42}

        await adapter.dispatch_task(task_type, sent_payload)

        received: list[dict[str, Any]] = []

        async def handler(payload: dict[str, Any]) -> None:
            received.append(payload)

        await adapter.consume(task_type, handler, max_count=1, block_ms=2000)
        await adapter.close()

        assert len(received) == 1
        assert received[0] == sent_payload


# ---------------------------------------------------------------------------
# Integration: GCS (skipped unless GCS_TEST_BUCKET is set)
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestGCSFileSystemIntegration:
    @pytest.fixture(autouse=True)
    def require_gcs_bucket(self) -> None:
        if not os.environ.get("GCS_TEST_BUCKET"):
            pytest.skip("GCS_TEST_BUCKET env var not set")

    def test_gcs_instantiation(self) -> None:
        bucket = os.environ["GCS_TEST_BUCKET"]
        adapter = GCSFileSystemAdapter(bucket_name=bucket, prefix="dime-test")
        assert adapter._bucket_name == bucket  # type: ignore[reportPrivateUsage]
