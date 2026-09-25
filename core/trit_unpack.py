"""Domain-agnostic Winsor trit pack + efficient I2_S unpack/flips.

Pollinated from JuniorPoker trit_felt (pack / pack_centered / pack_delta)
and JuniorHome / JuniorLLM Gaia wire (gamma, trit, i2s_hex).

Not a hash. SHA3 stays identity. Trit Hamming stays neighbor.
Stdlib only. No numpy. No BitNet replacement.
"""
from __future__ import annotations

from typing import Iterable


TRIT = (-1, 0, 1)


def note_ids(note: str, width: int = 32) -> list[int]:
    text = note or "gaia"
    return [ord(c) for c in text[:width]] or [0]


def _winsor_gamma(xs: list[float]) -> tuple[list[float], float]:
    vals = list(xs) or [0.0]
    abs_sorted = sorted(abs(x) for x in vals)
    tau = abs_sorted[max(0, int(0.95 * (len(abs_sorted) - 1)))] or 1.0
    clipped = [min(max(x, -tau), tau) for x in vals]
    gamma = (sum(abs(x) for x in clipped) / len(clipped)) or 1.0
    return clipped, gamma


def _quantize(clipped: list[float], gamma: float) -> list[int]:
    trits: list[int] = []
    for x in clipped:
        q = round(x / gamma)
        if q > 0:
            trits.append(1)
        elif q < 0:
            trits.append(-1)
        else:
            trits.append(0)
    return trits


def pack_i2s(trits: Iterable[int]) -> tuple[int, int]:
    bits = 0
    n = 0
    for t in trits:
        tt = int(t)
        if tt > 0:
            tt = 1
        elif tt < 0:
            tt = -1
        else:
            tt = 0
        bits = (bits << 2) | (tt + 1)
        n += 1
    return bits, n


def unpack_i2s(bits: int, n: int) -> list[int]:
    if n <= 0:
        return []
    codes = [0] * n
    tmp = int(bits)
    for i in range(n - 1, -1, -1):
        codes[i] = (tmp & 3) - 1
        tmp >>= 2
    return codes


def flip_packed(bits: int, n: int, index: int) -> int:
    if n <= 0 or index < 0 or index >= n:
        return int(bits)
    shift = 2 * (n - 1 - index)
    code = (int(bits) >> shift) & 3
    if code == 1:
        return int(bits)
    new_code = 2 if code == 0 else 0
    mask = ~(3 << shift)
    return (int(bits) & mask) | (new_code << shift)


def flip_packed_all_signs(bits: int, n: int) -> int:
    out = int(bits)
    for i in range(n):
        out = flip_packed(out, n, i)
    return out


def flip_trit(trits: list[int], index: int) -> list[int]:
    out = list(trits)
    if 0 <= index < len(out):
        out[index] = -out[index]
    return out


def pack(ids: list[int] | list[float]) -> dict:
    xs = [float(i) for i in ids] or [0.0]
    clipped, gamma = _winsor_gamma(xs)
    trits = _quantize(clipped, gamma)
    bits, n = pack_i2s(trits)
    return {
        "gamma": round(gamma, 6),
        "trits": trits,
        "i2s_hex": format(bits, "x"),
        "i2s_bits": bits,
        "n": n,
        "mode": "raw",
        "collision_resistant": False,
    }


def unpack(blob: dict | None = None, *, i2s_hex: str | None = None, n: int | None = None) -> list[int]:
    if blob is not None:
        if "trits" in blob and blob.get("trits") is not None and i2s_hex is None:
            if blob.get("i2s_hex"):
                return unpack_i2s(int(blob["i2s_hex"], 16), int(blob.get("n") or len(blob["trits"])))
            return [int(t) for t in blob["trits"]]
        i2s_hex = i2s_hex or blob.get("i2s_hex")
        n = n if n is not None else blob.get("n")
        if blob.get("i2s_bits") is not None and n is not None:
            return unpack_i2s(int(blob["i2s_bits"]), int(n))
    if not i2s_hex:
        return []
    count = int(n or 0)
    if count <= 0:
        raw = int(i2s_hex, 16)
        count = max(1, (raw.bit_length() + 1) // 2)
    return unpack_i2s(int(i2s_hex, 16), count)


def pack_centered(ids: list[int] | list[float]) -> dict:
    xs = [float(i) for i in ids] or [0.0]
    mu = sum(xs) / len(xs)
    out = pack([x - mu for x in xs])
    out["mean"] = round(mu, 6)
    out["mode"] = "centered"
    return out


def pack_delta(ids: list[int] | list[float]) -> dict:
    if not ids:
        return pack([])
    walk: list[float] = [0.0]
    for i in range(1, len(ids)):
        walk.append(float(ids[i]) - float(ids[i - 1]))
    out = pack(walk)
    out["mode"] = "delta"
    return out


def trit_ham(a: list[int], b: list[int]) -> int:
    n = min(len(a), len(b))
    return sum(x != y for x, y in zip(a[:n], b[:n])) + abs(len(a) - len(b))


def pack_note(note: str, mode: str = "raw") -> dict:
    ids = note_ids(note)
    if mode == "centered":
        out = pack_centered(ids)
    elif mode == "delta":
        out = pack_delta(ids)
    else:
        out = pack(ids)
    out["note"] = note
    return out
