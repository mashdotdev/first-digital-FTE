"""Watcher implementations for Digital FTE."""

from .filesystem_watcher import FilesystemWatcher
from .gmail_watcher import GmailWatcher
from .linkedin_watcher import LinkedInWatcher
from .social_media_watcher import SocialMediaWatcher

__all__ = [
    "FilesystemWatcher",
    "GmailWatcher",
    "LinkedInWatcher",
    "SocialMediaWatcher",
]
