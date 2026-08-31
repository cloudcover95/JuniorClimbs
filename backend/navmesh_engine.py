"""JuniorNavMesh engine — offline geo math, NMEA, GPX. Stdlib only."""
from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone
from typing import Any, Iterable
from xml.etree.ElementTree import Element, SubElement, tostring, fromstring

OFFLINE = os.getenv("JUNIOR_OFFLINE", "1") != "0"


def haversine_mi(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 3958.8
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(min(1.0, a)))


def bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    x = math.sin(dl) * math.cos(p2)
    y = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    brng = (math.degrees(math.atan2(x, y)) + 360.0) % 360.0
    return brng


def compass(brng: float) -> str:
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    return dirs[int((brng + 11.25) // 22.5) % 16]


def goto(from_lat: float, from_lon: float, to_lat: float, to_lon: float) -> dict[str, Any]:
    dist = haversine_mi(from_lat, from_lon, to_lat, to_lon)
    brng = bearing_deg(from_lat, from_lon, to_lat, to_lon)
    return {
        "distance_mi": round(dist, 3),
        "distance_ft": round(dist * 5280.0, 1),
        "bearing_deg": round(brng, 1),
        "compass": compass(brng),
        "from": [from_lat, from_lon],
        "to": [to_lat, to_lon],
        "offline": OFFLINE,
    }


def point_in_bbox(lat: float, lon: float, s: float, w: float, n: float, e: float) -> bool:
    return s <= lat <= n and w <= lon <= e


def nmea_coord(raw: str, hemi: str) -> float | None:
    """Parse ddmm.mmmm + hemisphere into decimal degrees."""
    if not raw:
        return None
    try:
        val = float(raw)
    except ValueError:
        return None
    deg = int(val // 100)
    minutes = val - deg * 100
    dec = deg + minutes / 60.0
    if hemi in ("S", "W"):
        dec = -dec
    return dec


def parse_nmea(sentence: str) -> dict[str, Any] | None:
    """Parse GGA or RMC. Returns lat/lon/elev/sats or None."""
    s = sentence.strip()
    if s.startswith("$"):
        s = s[1:]
    if "*" in s:
        s = s.split("*", 1)[0]
    parts = s.split(",")
    if not parts:
        return None
    talker = parts[0]
    if talker.endswith("GGA") and len(parts) >= 10:
        lat = nmea_coord(parts[2], parts[3] if len(parts) > 3 else "N")
        lon = nmea_coord(parts[4], parts[5] if len(parts) > 5 else "W")
        if lat is None or lon is None:
            return None
        try:
            sats = int(parts[7]) if parts[7] else None
        except ValueError:
            sats = None
        try:
            elev = float(parts[9]) if parts[9] else None
        except ValueError:
            elev = None
        try:
            hdop = float(parts[8]) if parts[8] else None
        except ValueError:
            hdop = None
        return {"lat": lat, "lon": lon, "elev_m": elev, "sats": sats, "hdop": hdop, "source": "nmea-gga"}
    if talker.endswith("RMC") and len(parts) >= 7:
        if parts[2] != "A":
            return None
        lat = nmea_coord(parts[3], parts[4])
        lon = nmea_coord(parts[5], parts[6])
        if lat is None or lon is None:
            return None
        return {"lat": lat, "lon": lon, "elev_m": None, "sats": None, "hdop": None, "source": "nmea-rmc"}
    return None


def tracks_to_gpx(name: str, points: Iterable[list]) -> str:
    gpx = Element("gpx", attrib={"version": "1.1", "creator": "JuniorNavMesh"})
    trk = SubElement(gpx, "trk")
    SubElement(trk, "name").text = name
    seg = SubElement(trk, "trkseg")
    for p in points:
        if len(p) < 2:
            continue
        attrs = {"lat": f"{p[0]:.7f}", "lon": f"{p[1]:.7f}"}
        trkpt = SubElement(seg, "trkpt", attrib=attrs)
        if len(p) > 2 and p[2] is not None:
            SubElement(trkpt, "ele").text = str(p[2])
    xml = tostring(gpx, encoding="unicode")
    return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" + xml


def waypoints_to_gpx(name: str, wps: Iterable[dict]) -> str:
    gpx = Element("gpx", attrib={"version": "1.1", "creator": "JuniorNavMesh"})
    SubElement(gpx, "name").text = name
    for w in wps:
        wpt = SubElement(gpx, "wpt", attrib={"lat": f"{w['lat']:.7f}", "lon": f"{w['lon']:.7f}"})
        SubElement(wpt, "name").text = w.get("name") or "wp"
        if w.get("elev_ft") is not None:
            SubElement(wpt, "ele").text = str(float(w["elev_ft"]) * 0.3048)
    return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" + tostring(gpx, encoding="unicode")


def parse_gpx(xml_text: str) -> dict[str, Any]:
    root = fromstring(xml_text.encode("utf-8") if isinstance(xml_text, str) else xml_text)
    ns = ""
    if root.tag.startswith("{ "):
        pass
    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0][1:]
    def tag(name: str) -> str:
        return f"{{{ns}}}{name}" if ns else name

    waypoints = []
    tracks = []
    for wpt in root.iter(tag("wpt")):
        try:
            lat = float(wpt.attrib["lat"])
            lon = float(wpt.attrib["lon"])
        except (KeyError, ValueError):
            continue
        nm = wpt.find(tag("name"))
        waypoints.append({"name": (nm.text if nm is not None else "wp"), "lat": lat, "lon": lon})
    for trk in root.iter(tag("trk")):
        nm = trk.find(tag("name"))
        pts = []
        for trkpt in trk.iter(tag("trkpt")):
            try:
                pts.append([float(trkpt.attrib["lat"]), float(trkpt.attrib["lon"])])
            except (KeyError, ValueError):
                continue
        tracks.append({"name": (nm.text if nm is not None else "track"), "points": pts})
    return {"waypoints": waypoints, "tracks": tracks}


def dump_points(points: list) -> str:
    return json.dumps(points)


def load_points(raw: str) -> list:
    try:
        return json.loads(raw or "[]")
    except json.JSONDecodeError:
        return []


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)
