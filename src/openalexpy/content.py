from __future__ import annotations

from pathlib import Path

from openalexpy.config import config
from openalexpy.exceptions import ContentUnavailableError


class ContentDownloader:
    def __init__(self, work_id: str, extension: str) -> None:
        self._work_id = work_id
        self._extension = extension
        self._client_type = "async"

    @property
    def url(self) -> str:
        base = config.content_base_url.rstrip("/")
        return f"{base}/works/{self._work_id}{self._extension}"

    async def async_get(self) -> bytes:
        from openalexpy.client import AsyncOpenAlexClient

        client = AsyncOpenAlexClient()
        try:
            content, _ = await client.get_raw(self.url)
            return content
        except Exception as exc:
            raise ContentUnavailableError(f"Failed to download content: {exc}") from exc

    async def async_download(self, path: str | Path) -> None:
        content = await self.async_get()
        Path(path).write_bytes(content)

    def sync_get(self) -> bytes:
        from openalexpy.client import SyncOpenAlexClient

        client = SyncOpenAlexClient()
        try:
            content, _ = client.get_raw(self.url)
            return content
        except Exception as exc:
            raise ContentUnavailableError(f"Failed to download content: {exc}") from exc

    def sync_download(self, path: str | Path) -> None:
        content = self.sync_get()
        Path(path).write_bytes(content)


class PDF:
    def __init__(self, work_id: str) -> None:
        self._downloader = ContentDownloader(work_id, ".pdf")

    @property
    def url(self) -> str:
        return self._downloader.url

    async def get(self) -> bytes:
        return await self._downloader.async_get()

    async def download(self, path: str | Path) -> None:
        await self._downloader.async_download(path)

    def sync_get(self) -> bytes:
        return self._downloader.sync_get()

    def sync_download(self, path: str | Path) -> None:
        self._downloader.sync_download(path)


class TEI:
    def __init__(self, work_id: str) -> None:
        self._downloader = ContentDownloader(work_id, ".grobid-xml")

    @property
    def url(self) -> str:
        return self._downloader.url

    async def get(self) -> bytes:
        return await self._downloader.async_get()

    async def download(self, path: str | Path) -> None:
        await self._downloader.async_download(path)

    def sync_get(self) -> bytes:
        return self._downloader.sync_get()

    def sync_download(self, path: str | Path) -> None:
        self._downloader.sync_download(path)
