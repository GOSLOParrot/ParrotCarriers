"""tail_obs_log.py — 实时追尾 GOSLO 的观测日志和 L0 事件流.

用法:
    # 追尾 obs_log (Context Injector 决策 + Supervisor 档位变化 + Ingest 入库):
    python src/scripts/tail_obs_log.py

    # 追尾 L0 事件流 (Reflex/Intent/Task 三层原始事件):
    python src/scripts/tail_obs_log.py --stream events

    # 两流同时看 (并排输出):
    python src/scripts/tail_obs_log.py --stream both

    # 只看特定 kind (支持 glob 风格子串匹配):
    python src/scripts/tail_obs_log.py --kind tier_change
    python src/scripts/tail_obs_log.py --kind ingest

    # 回看最近 N 条 (不持续追尾):
    python src/scripts/tail_obs_log.py --last 50

验证时间轴是否有效工作的典型模式:
    1. 启动本脚本
    2. 手机执行动作 (说"视频全开" / 遮住摄像头 / identify_object)
    3. 观察日志中的因果链:
         obs_log:   bb_change(session/video_tier=VIDEO_FULL) → layer=3 → C4
         events.log: intent.tier_change from=GEMINI_ONLY to=FULL cause=user_override
         obs_log:   ingest_upsert(label=杯子 source=gemini_oral conf=0.4)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from typing import Any

# ANSI colour codes — disable with NO_COLOR env var
_USE_COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")

_COLORS = {
    "reset": "\033[0m" if _USE_COLOR else "",
    "dim": "\033[2m" if _USE_COLOR else "",
    "bold": "\033[1m" if _USE_COLOR else "",
    "cyan": "\033[36m" if _USE_COLOR else "",
    "yellow": "\033[33m" if _USE_COLOR else "",
    "green": "\033[32m" if _USE_COLOR else "",
    "red": "\033[31m" if _USE_COLOR else "",
    "magenta": "\033[35m" if _USE_COLOR else "",
    "blue": "\033[34m" if _USE_COLOR else "",
}

# Colour per stream
_STREAM_COLOR = {
    "obs": _COLORS["cyan"],
    "events": _COLORS["yellow"],
}

# Colour per consciousness layer (obs_log)
_LAYER_COLOR = {
    "1": _COLORS["dim"],      # subconscious — grey
    "2": _COLORS["magenta"],  # autonomous action — purple
    "3": _COLORS["green"],    # reported to Gemini — green
}

# Highlight for high-signal event kinds
_KIND_HIGHLIGHTS = {
    "tier_change": _COLORS["bold"] + _COLORS["yellow"],
    "intent_decision": _COLORS["bold"] + _COLORS["magenta"],
    "ingest_upsert": _COLORS["green"],
    "ingest_mode_dropped": _COLORS["red"],
    "c2_rebuild": _COLORS["bold"] + _COLORS["blue"],
    "c4_dispatch": _COLORS["bold"] + _COLORS["green"],
}


def _c(color: str, text: str) -> str:
    return f"{_COLORS.get(color, '')}{text}{_COLORS['reset']}"


def _format_ts(ts_str: str) -> str:
    try:
        t = float(ts_str)
        return time.strftime("%H:%M:%S", time.localtime(t)) + f".{int((t % 1) * 1000):03d}"
    except (ValueError, TypeError):
        return ts_str


def _truncate(s: str, n: int = 120) -> str:
    return s if len(s) <= n else s[: n - 3] + "..."


def _format_payload(raw: str) -> str:
    try:
        d = json.loads(raw)
        parts = []
        for k, v in d.items():
            if isinstance(v, dict):
                inner = " ".join(f"{kk}={vv}" for kk, vv in list(v.items())[:4])
                parts.append(f"{k}={{{inner}}}")
            else:
                parts.append(f"{k}={v}")
        return " ".join(parts)
    except Exception:
        return raw


def _format_obs_entry(entry: dict[str, Any]) -> str | None:
    fields = entry.get("fields", {})
    kind = fields.get("kind", "?")
    layer = fields.get("layer", "?")
    actor = fields.get("actor", "?")
    ts = _format_ts(fields.get("ts", ""))
    payload_str = _truncate(_format_payload(fields.get("payload", "{}")))

    layer_color = _LAYER_COLOR.get(layer, "")
    kind_color = next(
        (v for k, v in _KIND_HIGHLIGHTS.items() if k in kind), _COLORS["cyan"]
    )

    actor_short = actor.replace("brain.", "").replace("parrot.", "")
    layer_tag = f"L{layer}"

    return (
        f"{_COLORS['dim']}{ts}{_COLORS['reset']} "
        f"{_STREAM_COLOR['obs']}obs{_COLORS['reset']} "
        f"{layer_color}{layer_tag}{_COLORS['reset']} "
        f"{kind_color}{kind:<28}{_COLORS['reset']} "
        f"{_COLORS['dim']}{actor_short:<24}{_COLORS['reset']} "
        f"{payload_str}"
    )


def _format_event_entry(entry: dict[str, Any]) -> str | None:
    fields = entry.get("fields", {})
    kind = fields.get("kind", "?")
    layer = fields.get("layer", "?")
    actor = fields.get("actor", "?")
    ts = _format_ts(fields.get("ts", ""))
    payload_str = _truncate(_format_payload(fields.get("payload", "{}")))

    kind_color = next(
        (v for k, v in _KIND_HIGHLIGHTS.items() if k in kind), _COLORS["yellow"]
    )

    layer_map = {"reflex": "REF", "intent": "INT", "task": "TSK"}
    layer_tag = layer_map.get(layer, layer[:3].upper())

    actor_short = actor.replace("brain.", "").replace("parrot.", "")

    return (
        f"{_COLORS['dim']}{ts}{_COLORS['reset']} "
        f"{_STREAM_COLOR['events']}evt{_COLORS['reset']} "
        f"{_COLORS['yellow']}{layer_tag}{_COLORS['reset']} "
        f"{kind_color}{kind:<28}{_COLORS['reset']} "
        f"{_COLORS['dim']}{actor_short:<24}{_COLORS['reset']} "
        f"{payload_str}"
    )


async def _read_last(redis: Any, stream_key: str, count: int) -> list[dict]:
    entries = await redis.xrevrange(stream_key, count=count)
    return list(reversed(entries))


async def _tail_stream(
    redis: Any,
    stream_key: str,
    formatter,
    kind_filter: str | None,
    last_id: str,
    queue: asyncio.Queue,
    label: str,
) -> None:
    current_id = last_id
    while True:
        try:
            results = await redis.xread({stream_key: current_id}, count=50, block=500)
            for _, entries in (results or []):
                for entry_id, fields in entries:
                    current_id = entry_id
                    entry = {"id": entry_id, "fields": fields}
                    kind = fields.get("kind", "")
                    if kind_filter and kind_filter.lower() not in kind.lower():
                        continue
                    line = formatter(entry)
                    if line:
                        await queue.put((entry_id, line))
        except asyncio.CancelledError:
            return
        except Exception as e:
            await queue.put(("ERR", f"{_c('red', f'[{label} error]')} {e}"))
            await asyncio.sleep(2)


async def main(args: argparse.Namespace) -> None:
    try:
        import redis.asyncio as aioredis
    except ImportError:
        print("ERROR: redis package not installed. Run: pip install redis", file=sys.stderr)
        sys.exit(1)

    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")

    print(
        f"{_c('bold', 'GOSLO obs-tail')} | stream={args.stream} | "
        f"filter={args.kind or 'all'} | redis={redis_url}",
        flush=True,
    )
    print(_c("dim", "─" * 80), flush=True)

    r = await aioredis.from_url(redis_url, decode_responses=True)

    # Resolve stream keys
    obs_key = "parrot.obs_log"
    evt_key = "parrot.events.log"

    streams: list[tuple[str, Any, str]] = []
    if args.stream in ("obs", "both"):
        streams.append((obs_key, _format_obs_entry, "obs"))
    if args.stream in ("events", "both"):
        streams.append((evt_key, _format_event_entry, "events"))

    if args.last > 0:
        # One-shot mode: show last N entries then exit
        for key, formatter, label in streams:
            entries = await _read_last(r, key, args.last)
            for e_id, fields in entries:
                entry = {"id": e_id, "fields": fields}
                kind = fields.get("kind", "")
                if args.kind and args.kind.lower() not in kind.lower():
                    continue
                line = formatter(entry)
                if line:
                    print(line, flush=True)
        await r.aclose()
        return

    # Tail mode: get current tail id and then block-read going forward
    queue: asyncio.Queue = asyncio.Queue()
    tasks = []
    for key, formatter, label in streams:
        # Start from latest entry
        info = await r.xinfo_stream(key)
        last_id = info.get("last-generated-id", "0-0") if info else "0-0"

        task = asyncio.create_task(
            _tail_stream(r, key, formatter, args.kind, last_id, queue, label)
        )
        tasks.append(task)

    print(_c("dim", f"Tailing from current tail… (Ctrl-C to stop)"), flush=True)

    try:
        while True:
            try:
                _entry_id, line = await asyncio.wait_for(queue.get(), timeout=30)
                print(line, flush=True)
            except asyncio.TimeoutError:
                # Print a heartbeat so operator knows the script is alive
                print(_c("dim", f"  … {time.strftime('%H:%M:%S')} (waiting)"), flush=True)
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        for t in tasks:
            t.cancel()
        await r.aclose()
        print(_c("dim", "\ntail stopped."), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Real-time tail of GOSLO's internal observation log and L0 event stream."
    )
    parser.add_argument(
        "--stream",
        choices=["obs", "events", "both"],
        default="both",
        help="Which stream to tail. 'obs'=consciousness decisions, 'events'=L0 raw events, 'both'=interleaved.",
    )
    parser.add_argument(
        "--kind",
        default="",
        help="Filter by event kind substring (e.g. 'tier_change', 'ingest').",
    )
    parser.add_argument(
        "--last",
        type=int,
        default=0,
        metavar="N",
        help="One-shot: show last N entries and exit (no tailing).",
    )
    asyncio.run(main(parser.parse_args()))
