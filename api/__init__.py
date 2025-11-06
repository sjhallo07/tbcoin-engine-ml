"""API package initializer for the TB Coin project.

Making `api` a proper package (with __init__) ensures uvicorn can import
`api.main:app` reliably when running from the repository root.
"""

__all__ = ["main", "autonomous_routes"]
