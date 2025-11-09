"""Web project generators."""

from .atlas import AtlasWebProjectInitGenerator
from .init import WebProjectInitGenerator

__all__ = [
    "WebProjectInitGenerator",
    "AtlasWebProjectInitGenerator",
]
