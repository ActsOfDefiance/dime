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
from dime.adapters.publishing.astro import AstroAdapter
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
    publishing: PublishingAdapter = AstroAdapter(
        art_dir=settings.ASTRO_ART_DIR,
        acts_of_defiance_public_dir=settings.ASTRO_PUBLIC_DIR,
        signal_file_path=settings.ASTRO_SIGNAL_FILE,
        content_base=settings.ASTRO_CONTENT_BASE,
        preview_host=settings.ASTRO_PREVIEW_HOST,
    )
    notification: NotificationAdapter = WebSocketNotificationAdapter()
    return AdapterSet(
        broker=broker,
        filesystem=filesystem,
        publishing=publishing,
        notification=notification,
    )
