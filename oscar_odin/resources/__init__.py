"""Resources for Oscar Odin."""

from . import address, auth, catalogue, order

from .base import OscarResource

__all__ = ["OscarResource", "address", "catalogue", "order", "auth"]
