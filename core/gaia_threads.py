"""Domain-agnostic Gaia threads.

Layers match JuniorHome / JuniorLLM: who, spine, dash, view, walk, mesh.
Compute stays local. Handshake envelope matches GAIA_WIRE without importing
JuniorLLM ports (optional handshake if ports.gaia_proto is on PYTHONPATH).

Stdlib only. Thread pool fans notes across named layers.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable

from .trit_unpack import pack_note, unpack, flip_packed_all_signs, unpack_i2s

LAYERS = ("who", "spine", "dash", "view", "walk", "mesh")
AREAS = (
    "home",
    "climbs",
    "poker",
    "quant",
    "coach",
    "omega",
    "mesh",
    "field",
)
JOBS = ("dash-viewport", "gaia-spine", "terrain-obj", "agi-capsule", "trit-flip")
PROTO = "goldend-osai-omega/1"


def _load_who() -> dict:
    path = Path.home() / ".juniorhome" / "gaia.json"
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            name = data.get("name") or data.get("who", {}).get("name")
            pronouns = data.get("pronouns") or data.get("who", {}).get("pronouns")
            if name and pronouns:
                return {"name": str(name), "pronouns": str(pronouns), "source": str(path)}
        except (OSError, json.JSONDecodeError, TypeError):
            pass
    return {"name": os.environ.get("JUNIOR_WHO", "operator"), "pronouns": os.environ.get("JUNIOR_PRONOUNS", "they"), "source": "env-or-default"}


def _area_for(note: str) -> str:
    low = (note or "").lower()
    for area in AREAS:
        if area in low:
            return area
    return "home"


def _port_for(area: str) -> str:
    mapping = {
        "home": "JuniorHome",
        "climbs": "JuniorClimbs",
        "poker": "JuniorPoker",
        "quant": "JuniorQuant",
        "coach": "JuniorCoach",
        "omega": "JuniorOmega",
        "mesh": "JuniorMemSys",
        "field": "JuniorField",
    }
    return mapping.get(area, "JuniorHome")


def handshake(
    note: str = "home dash",
    *,
    orient: str = "landscape",
    scale: float = 1.0,
    job: str | None = None,
    area: str | None = None,
    mode: str = "raw",
) -> dict:
    try:
        remote = importlib.import_module("ports.gaia_proto")
        remote_hs = getattr(remote, "handshake", None)
        if callable(remote_hs):
            env = remote_hs(note, job=job or "dash-viewport")
            if env.get("schema_ok"):
                return env
    except Exception:
        pass

    who = _load_who()
    resolved_area = area or _area_for(note)
    packed = pack_note(note, mode=mode)
    trits = unpack(packed)
    ident_ok = bool(who.get("name") and who.get("pronouns"))
    env = {
        "system": "JuniorGaia",
        "layers": list(LAYERS),
        "who": {"name": who["name"], "pronouns": who["pronouns"]},
        "view": {"orient": orient if orient in ("portrait", "landscape") else "landscape", "px": None, "scale": float(scale)},
        "note": {
            "area": resolved_area,
            "port": _port_for(resolved_area),
            "gamma": packed["gamma"],
            "trit": trits,
            "i2s_hex": packed["i2s_hex"],
            "mode": packed["mode"],
        },
        "identity": {
            "issuer": "local-gaia.json",
            "verified": ident_ok,
            "source": who.get("source"),
        },
        "omega": {"job": job or "dash-viewport", "launch": False},
        "protocol": PROTO,
        "schema_ok": True,
        "schema_bad": [],
        "ue5_launch": False,
        "download": False,
        "jobs_allowed": list(JOBS),
    }
    return env


def witness(env: dict) -> str:
    payload = json.dumps(
        {
            "system": env.get("system"),
            "note": (env.get("note") or {}).get("i2s_hex"),
            "area": (env.get("note") or {}).get("area"),
            "job": (env.get("omega") or {}).get("job"),
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _layer_work(layer: str, env: dict) -> dict:
    note = env.get("note") or {}
    bits = int(note.get("i2s_hex") or "0", 16)
    n = int(len(note.get("trit") or []))
    started = time.perf_counter()
    if layer == "who":
        body = {"who": env.get("who")}
    elif layer == "spine":
        body = {"gamma": note.get("gamma"), "n": n}
    elif layer == "dash":
        body = {"i2s_hex": note.get("i2s_hex"), "area": note.get("area"), "port": note.get("port")}
    elif layer == "view":
        body = {"view": env.get("view"), "job": (env.get("omega") or {}).get("job")}
    elif layer == "walk":
        flipped = flip_packed_all_signs(bits, n) if n else 0
        body = {
            "walk": "delta-or-flip",
            "flipped_hex": format(flipped, "x"),
            "flipped_trits": unpack_i2s(flipped, n) if n else [],
        }
    else:
        body = {"mesh": False, "terrain": note.get("area") == "omega"}
    return {
        "layer": layer,
        "ms": round((time.perf_counter() - started) * 1000.0, 4),
        "ok": True,
        **body,
    }


class GaiaPool:
    def __init__(self, max_workers: int | None = None) -> None:
        self.max_workers = max_workers or len(LAYERS)
        self._lock = threading.Lock()
        self.pulses: list[dict] = []

    def pulse(self, note: str = "home dash", **kw) -> dict:
        env = handshake(note, **kw)
        env["witness"] = witness(env)
        layers = list(LAYERS)
        results: dict[str, dict] = {}
        with ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="gaia") as pool:
            futs = {pool.submit(_layer_work, layer, env): layer for layer in layers}
            for fut in as_completed(futs):
                layer = futs[fut]
                try:
                    results[layer] = fut.result()
                except Exception as exc:
                    results[layer] = {"layer": layer, "ok": False, "error": type(exc).__name__}
        pulse = {
            "ok": env.get("schema_ok") and all(v.get("ok") for v in results.values()),
            "envelope": env,
            "layers": results,
            "witness": env["witness"],
        }
        with self._lock:
            self.pulses.append({"witness": env["witness"], "area": (env.get("note") or {}).get("area")})
        return pulse

    def map_notes(self, notes: list[str], fn: Callable[[str], dict] | None = None) -> list[dict]:
        worker = fn or (lambda n: self.pulse(n))
        out: list[dict] = []
        with ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="gaia-map") as pool:
            futs = [pool.submit(worker, note) for note in notes]
            for fut in as_completed(futs):
                out.append(fut.result())
        return out
