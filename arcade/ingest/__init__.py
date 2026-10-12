"""Ingest adapters. This slice is ChatSim only; Twitch EventSub is later."""

from .chatsim import ChatSim

__all__ = ["ChatSim"]
