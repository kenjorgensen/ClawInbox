from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import time

from imapclient import IMAPClient

from .logging import get_logger
from .settings import Settings

logger = get_logger(__name__)


@dataclass
class ImapMessage:
    uid: int
    raw: bytes


class ImapSync:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client: IMAPClient | None = None

    def connect(self) -> IMAPClient:
        if not self.settings.imap_host or not self.settings.imap_user:
            raise ValueError("IMAP host and user must be configured.")
        attempts = self.settings.imap_retry_count
        last_error: Exception | None = None
        for attempt in range(1, attempts + 1):
            try:
                client = IMAPClient(self.settings.imap_host, port=self.settings.imap_port, ssl=self.settings.imap_ssl)
                client.login(self.settings.imap_user, self.settings.imap_password or "")
                self._client = client
                return client
            except Exception as exc:  # pragma: no cover - depends on network
                last_error = exc
                logger.warning("IMAP connect failed (attempt %s/%s): %s", attempt, attempts, exc)
                time.sleep(self.settings.imap_retry_delay_seconds)
        raise RuntimeError("IMAP connection failed after retries.") from last_error

    def disconnect(self) -> None:
        if self._client is not None:
            try:
                self._client.logout()
            finally:
                self._client = None

    def list_mailboxes(self) -> list[str]:
        client = self._client or self.connect()
        mailboxes = []
        for flags, delimiter, name in client.list_folders():
            _ = flags, delimiter
            mailboxes.append(name)
        return mailboxes

    def list_uids(self, mailbox: str) -> list[int]:
        client = self._client or self.connect()
        client.select_folder(mailbox, readonly=True)
        return [int(uid) for uid in client.search("ALL")]

    def fetch_messages(
        self,
        mailbox: str,
        limit: int = 50,
        since_uid: int | None = None,
        since_date: str | None = None,
        before_date: str | None = None,
    ) -> Iterable[ImapMessage]:
        client = self._client or self.connect()
        client.select_folder(mailbox, readonly=True)
        search_criteria = []
        if since_uid:
            search_criteria.extend(["UID", f"{since_uid + 1}:*"])
        if since_date:
            search_criteria.extend(["SINCE", since_date])
        if before_date:
            search_criteria.extend(["BEFORE", before_date])
        if not search_criteria:
            search_criteria = ["ALL"]
        uids = client.search(search_criteria)
        uids = uids[-limit:]
        if not uids:
            return []
        fetched = client.fetch(uids, ["RFC822"])
        messages: list[ImapMessage] = []
        for uid, data in fetched.items():
            raw = data.get(b"RFC822") or data.get("RFC822")
            if raw:
                messages.append(ImapMessage(uid=int(uid), raw=raw))
        logger.info("Fetched %s messages from %s", len(messages), mailbox)
        return messages
