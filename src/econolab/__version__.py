"""Defines the package-level __version__ attribute for runtime access."""

from importlib.metadata import version


try:
    __version__ = version("econolab")
except Exception:
    __version__ = "0.0.0-dev"
