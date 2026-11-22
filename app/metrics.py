import contextvars
import hashlib
import json
import threading
import time
from collections import deque
from pathlib import Path

from fastapi import Request
from fastapi.responses import JSONResponse

from app import llm

LOG_PATH = Path("data/requests.jsonl")
MAX_BODY_BYTES = 10_000        # request body limit
MAX_QUESTION_CHARS = 500       # "question" field limit
MAX_QUERY_CHARS = 200          # ?q= limit
CACHE_TTL_SECONDS = 600        # cached LLM answers live 10 minutes
CACHE_MAX_ITEMS = 200

_current = contextvars.ContextVar("current_request", default=None)
_lock = threading.Lock()
_recent = deque(maxlen=500)    # the last 500 requests, for /metrics
_cache = {}
_totals = {"cache_hits": 0, "cache_misses": 0}


def estimate_tokens(text):
    # rough rule: 1 token is about 4 characters of English text
    return max(1, len(text) // 4) if text else 0


def reset():
    with _lock:
        _recent.clear()
        _cache.clear()
        _totals["cache_hits"] = 0
        _totals["cache_misses"] = 0


def new_request_info():
    return {"llm_calls": 0, "cache_hits": 0, "tokens_in": 0, "tokens_out": 0, "llm_ms": 0.0}


def ask_llm(system, user, *args, **kwargs):
    """Same as app.llm.ask_llm, plus a cache and token/latency counting."""
    key = hashlib.sha256(repr((system, user, args, sorted(kwargs.items()))).encode()).hexdigest()
    info = _current.get()
    now = time.time()

    with _lock:
        hit = _cache.get(key)
        if hit and now - hit[0] < CACHE_TTL_SECONDS:
            _totals["cache_hits"] += 1
            if info is not None:
                info["cache_hits"] += 1
            return hit[1]
        _totals["cache_misses"] += 1

    start = time.perf_counter()
    reply = llm.ask_llm(system, user, *args, **kwargs)
    elapsed_ms = (time.perf_counter() - start) * 1000

    if info is not None:
        info["llm_calls"] += 1
        info["llm_ms"] += elapsed_ms
        info["tokens_in"] += estimate_tokens(system) + estimate_tokens(user)
        info["tokens_out"] += estimate_tokens(reply)

    with _lock:
        if len(_cache) >= CACHE_MAX_ITEMS:
            _cache.pop(next(iter(_cache)))   # drop the oldest entry
        _cache[key] = (now, reply)
    return reply


def _too_big(detail):
    return JSONResponse({"detail": detail}, status_code=413)


def _invalid(detail):
    return JSONResponse({"detail": detail}, status_code=422)


async def check_limits(request: Request):
    q = request.query_params.get("q")
    if q is not None and len(q) > MAX_QUERY_CHARS:
        return _invalid("q is too long (max " + str(MAX_QUERY_CHARS) + " characters)")

    if request.method in ("POST", "PUT", "PATCH"):
        length = request.headers.get("content-length")
        if length and length.isdigit() and int(length) > MAX_BODY_BYTES:
            return _too_big("request body too large (max " + str(MAX_BODY_BYTES) + " bytes)")
        body = await request.body()
        if len(body) > MAX_BODY_BYTES:
            return _too_big("request body too large (max " + str(MAX_BODY_BYTES) + " bytes)")
        try:
            data = json.loads(body) if body else None
        except ValueError:
            return None   # let FastAPI report the bad JSON itself
        if isinstance(data, dict) and isinstance(data.get("question"), str):
            text = data["question"].strip()
            if text == "":
                return _invalid("question is empty")
            if len(text) > MAX_QUESTION_CHARS:
                return _invalid("question is too long (max " + str(MAX_QUESTION_CHARS) + " characters)")
    return None


def write_log(entry):
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass   # logging must never break a request


async def guard_and_log(request: Request, call_next):
    start = time.perf_counter()
    info = new_request_info()
    token = _current.set(info)
    try:
        response = await check_limits(request)
        if response is None:
            response = await call_next(request)
    finally:
        _current.reset(token)

    ms = round((time.perf_counter() - start) * 1000, 1)
    entry = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "ms": ms,
        "llm_calls": info["llm_calls"],
        "cache_hits": info["cache_hits"],
        "tokens_in": info["tokens_in"],
        "tokens_out": info["tokens_out"],
        "llm_ms": round(info["llm_ms"], 1),
    }
    with _lock:
        _recent.append(entry)
    write_log(entry)
    response.headers["X-Process-Time-Ms"] = str(ms)
    return response


def _percentile(values, p):
    values = sorted(values)
    return values[int(p * (len(values) - 1))]


def summary():
    with _lock:
        rows = list(_recent)
        hits = _totals["cache_hits"]
        misses = _totals["cache_misses"]
    by_path = {}
    for r in rows:
        by_path.setdefault(r["path"], []).append(r)
    paths = {}
    for path, items in by_path.items():
        times = [r["ms"] for r in items]
        llm_items = [r for r in items if r["llm_calls"] > 0]   # only requests that really called the LLM
        count = len(llm_items)
        paths[path] = {
            "requests": len(items),
            "avg_ms": round(sum(times) / len(times), 1),
            "p50_ms": _percentile(times, 0.5),
            "p95_ms": _percentile(times, 0.95),
            "max_ms": max(times),
            "avg_tokens_in": round(sum(r["tokens_in"] for r in llm_items) / count, 1) if count else 0,
            "avg_tokens_out": round(sum(r["tokens_out"] for r in llm_items) / count, 1) if count else 0,
        }
    total_lookups = hits + misses
    return {
        "requests_logged": len(rows),
        "tokens_are_estimates": True,
        "cache_hits": hits,
        "cache_misses": misses,
        "cache_hit_rate": round(hits / total_lookups, 3) if total_lookups else 0.0,
        "paths": paths,
    }


def install(app):
    app.middleware("http")(guard_and_log)
    app.add_api_route("/metrics", summary, methods=["GET"])