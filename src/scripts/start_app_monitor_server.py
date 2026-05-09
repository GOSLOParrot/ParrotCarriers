"""Start the local read-only App v1 smoke monitor."""

from __future__ import annotations

import argparse

import uvicorn

from parrot.brain.app_monitor_server import build_app


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7892)
    args = parser.parse_args()
    uvicorn.run(build_app(), host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
