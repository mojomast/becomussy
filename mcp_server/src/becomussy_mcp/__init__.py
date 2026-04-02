"""
becomussy MCP Server - Governed continuity system for agent self-development.

This MCP server exposes becomussy's API as tools for Hermes and other MCP clients.
"""

__version__ = "0.1.0"

from .server import main

__all__ = ["main"]
