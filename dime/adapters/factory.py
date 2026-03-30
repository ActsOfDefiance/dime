from __future__ import annotations

from dataclasses import dataclass

from dime.adapters.broker.redis import RedisBrokerAdapter
from dime.adapters.filesystem.local import LocalFileSystemAdapter
from dime.adapters.notification.websocket import WebSocketNotificationAdapter
from dime.adapters.protocols import (
    BrokerAdapter,
    FileSystemAdapter,
    NotificationAdapter,
    PublishingAdapter,
)
from dime.adapters.publishing.hugo import HugoPublishingAdapter
from dime.config.settings import DimeSettings


@dataclass
class AdapterSet:
    broker: BrokerAdapter
    filesystem: FileSystemAdapter
    publishing: PublishingAdapter
    notification: NotificationAdapter


def build_adapters(settings: DimeSettings) -> AdapterSet:
    """Construct and return all adapters from application settings.

    No concrete adapter type should be imported outside of this factory
    or the adapter package itself.
    """
    broker: BrokerAdapter = RedisBrokerAdapter(url=str(settings.REDIS_URL))
    filesystem: FileSystemAdapter = LocalFileSystemAdapter(
        base_path=settings.STORAGE_BASE_PATH
    )
    publishing: PublishingAdapter = HugoPublishingAdapter(
        content_dir=settings.HUGO_CONTENT_DIR
    )
    notification: NotificationAdapter = WebSocketNotificationAdapter()
    return AdapterSet(
        broker=broker,
        filesystem=filesystem,
        publishing=publishing,
        notification=notification,
    )
