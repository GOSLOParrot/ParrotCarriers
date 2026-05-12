"""Start the Parrot Web Console BFF and static frontend."""

from __future__ import annotations

import argparse
import os

import uvicorn
from dotenv import load_dotenv

from parrot.web_console import build_app


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7893)
    parser.add_argument(
        "--orch-url",
        default="",
        help="Override PARROT_WEB_CONSOLE_ORCH_URL for this process.",
    )
    parser.add_argument(
        "--orch-secret",
        default="",
        help="Override PARROT_ORCH_SECRET for this process.",
    )
    parser.add_argument(
        "--refresh-s",
        type=float,
        default=None,
        help="Override PARROT_WEB_CONSOLE_REFRESH_S for this process.",
    )
    args = parser.parse_args()
    if args.orch_url:
        os.environ["PARROT_WEB_CONSOLE_ORCH_URL"] = args.orch_url
    if args.orch_secret:
        os.environ["PARROT_ORCH_SECRET"] = args.orch_secret
    if args.refresh_s is not None:
        os.environ["PARROT_WEB_CONSOLE_REFRESH_S"] = str(args.refresh_s)
    uvicorn.run(build_app(), host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
