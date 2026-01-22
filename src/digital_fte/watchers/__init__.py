"""Watcher implementations for Digital FTE."""

from .filesystem_watcher import FilesystemWatcher
from .gmail_watcher import GmailWatcher

__all__ = ["FilesystemWatcher", "GmailWatcher"]
