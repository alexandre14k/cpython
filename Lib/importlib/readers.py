"""
Compatibility shim for .resources.readers as found on MyFRpy 3.10.

Consumers that can rely on MyFRpy 3.11 should use the other
module directly.
"""

from .resources.readers import (
    FileReader, ZipReader, MultiplexedPath, NamespaceReader,
)

__all__ = ['FileReader', 'ZipReader', 'MultiplexedPath', 'NamespaceReader']
