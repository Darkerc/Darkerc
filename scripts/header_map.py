#!/usr/bin/env python3
"""Generates the profile header (assets/header-light.svg and assets/header-dark.svg).

A map of Villahermosa's rivers, lagoons and main roads (OpenStreetMap data) with a
GPS track that drives into the city along real roads, plus the title block set in
Overpass (a typeface derived from Highway Gothic, the road-sign face). All text is
converted to outlines so the SVG renders the same everywhere, including GitHub.

Requirements:  pip install fonttools uharfbuzz
Usage:         python scripts/header_map.py [--osm cache.json] [--font Overpass.ttf] [--out assets]

The OSM extract and the font are downloaded once and cached in the system temp folder.
Map data © OpenStreetMap contributors (ODbL); the attribution is drawn in the image.
"""
import argparse, heapq, json, math, os, random, sys, tempfile, time, urllib.parse, urllib.request

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

# ---------------------------------------------------------------- content
NAME_LINES = ("Eder Reyes", "Castellanos")
SUBTITLE = "Backend developer in Villahermosa, Tabasco"
ATTRIBUTION = "© OpenStreetMap contributors"

THEMES = {
    "light": dict(bg="#ffffff", ink="#1f2328", muted="#59636e", faint="#8c959f",
                  wfill="#dcebf6", wline="#93bcdb", road="#d0d7de", route="#cf1d7e"),
    "dark":  dict(bg="#0d1117", ink="#f0f6fc", muted="#9198a1", faint="#6e7681",
                  wfill="#0f2a40", wline="#2c628a", road="#2a313a", route="#ff52aa"),
}

# ---------------------------------------------------------------- map frame
W, H = 1280, 420
LON_MIN, LON_MAX, LAT_C = -93.10, -92.78, 17.99
C = math.cos(math.radians(LAT_C))
K = W / ((LON_MAX - LON_MIN) * C)
LAT_MAX, LAT_MIN = LAT_C + H / K / 2, LAT_C - H / K / 2
PX_PER_M = K / 111_320
EPS = 0.85                                   # simplification tolerance in px

# Route: enters on the Escárcega highway, crosses the Grijalva on Ruiz Cortines, ends near La Venta.
ROUTE_ROAD = "Carretera Villahermosa - Francisco Escárcega"
ROUTE_START = (LAT_MIN - 0.004, -92.805)
ROUTE_VIA = (17.9976, -92.9125)
ROUTE_END = (17.998, -92.937)
SPACING = {"motorway": 640, "trunk": 600, "primary": 380, "secondary": 300}   # metres between fixes

OVERPASS_QUERY = """[out:json][timeout:90];
(
  way["natural"="water"](17.90,-93.12,18.08,-92.74);
  relation["natural"="water"](17.90,-93.12,18.08,-92.74);
  way["waterway"~"^(river|canal|stream)$"](17.90,-93.12,18.08,-92.74);
  way["highway"~"^(motorway|trunk|primary|secondary)$"](17.90,-93.12,18.08,-92.74);
);
out geom;"""
OVERPASS_ENDPOINTS = ("https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter")
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/overpass/Overpass%5Bwght%5D.ttf"


# ---------------------------------------------------------------- downloads
def fetch_osm(path):
    if os.path.exists(path):
        return json.load(open(path))["elements"]
    body = urllib.parse.urlencode({"data": OVERPASS_QUERY}).encode()
    for attempt in range(3):
        for url in OVERPASS_ENDPOINTS:
            try:
                req = urllib.request.Request(url, body, {"User-Agent": "profile-header-map/1.0"})
                data = urllib.request.urlopen(req, timeout=150).read()
                open(path, "wb").write(data)
                return json.loads(data)["elements"]
            except Exception as err:  # busy servers answer 429/502/504
                print(f"overpass {url}: {err}", file=sys.stderr)
        time.sleep(20 * (attempt + 1))
    sys.exit("Could not download the OpenStreetMap extract; try again later or pass --osm.")


def fetch_font(path):
    if not os.path.exists(path):
        urllib.request.urlretrieve(FONT_URL, path)
    return path


# ---------------------------------------------------------------- geometry
def proj(lat, lon):
    return (lon - LON_MIN) * C * K, (LAT_MAX - lat) * K


def inside(pts, margin=30):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return max(xs) > -margin and min(xs) < W + margin and max(ys) > -margin and min(ys) < H + margin


def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    dmax, idx = 0, 0
    for i in range(1, len(pts) - 1):
        x, y = pts[i]
        d = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / length if length > 1e-9 else math.hypot(x - x1, y - y1)
        if d > dmax:
            dmax, idx = d, i
    if dmax > eps:
        return rdp(pts[:idx + 1], eps)[:-1] + rdp(pts[idx:], eps)
    return [pts[0], pts[-1]]


def pathd(pts, close=False):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + ("Z" if close else "")


def geom(e):
    return [(p["lat"], p["lon"]) for p in e.get("geometry", [])]


def stitch(ways):
    """Joins multipolygon member ways that share endpoints into rings."""
    ways, out = [list(w) for w in ways if len(w) > 1], []
    while ways:
        cur, changed = ways.pop(0), True
        while changed and cur[0] != cur[-1]:
            changed = False
            for i, w in enumerate(ways):
                if w[0] == cur[-1]: cur += w[1:]
                elif w[-1] == cur[-1]: cur += w[::-1][1:]
                elif w[-1] == cur[0]: cur = w + cur[1:]
                elif w[0] == cur[0]: cur = w[::-1] + cur[1:]
                else: continue
                ways.pop(i)
                changed = True
                break
        out.append(cur)
    return out


def hav(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(h))


# ---------------------------------------------------------------- type
def _ntos(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def text_path(fontfile, text, wght, size, x, y, tracking=0.0):
    """Shapes text with HarfBuzz (kerning) and returns its outlines as SVG path data."""
    face = hb.Face(hb.Blob.from_file_path(fontfile))
    font = hb.Font(face)
    font.set_variations({"wght": wght})
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": True})
    s, tr, pen_x, parts = size / face.upem, tracking * face.upem, 0.0, []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        sp = SVGPathPen(None, ntos=_ntos)
        font.draw_glyph_with_pen(info.codepoint, TransformPen(sp, (s, 0, 0, -s, x + (pen_x + pos.x_offset) * s, y - pos.y_offset * s)))
        if sp.getCommands():
            parts.append(sp.getCommands())
        pen_x += pos.x_advance + tr
    return " ".join(parts)


# ---------------------------------------------------------------- build
def build_layers(els):
    water, rivers, roads = [], [], []
    for e in els:
        t = e.get("tags", {})
        if t.get("natural") == "water":
            rings = [geom(e)] if e["type"] == "way" else stitch(
                [[(p["lat"], p["lon"]) for p in m["geometry"]] for m in e["members"] if m["type"] == "way" and "geometry" in m])
            ds = []
            for r in rings:
                pts = [proj(*q) for q in r]
                if len(pts) > 2 and inside(pts):
                    span = max(p[0] for p in pts) - min(p[0] for p in pts) + max(p[1] for p in pts) - min(p[1] for p in pts)
                    pts = rdp(pts, EPS) if span > 3 else []
                    if len(pts) > 2:
                        ds.append(pathd(pts, True))
            if ds:
                water.append(" ".join(ds))
        elif "waterway" in t:
            pts = [proj(*q) for q in geom(e)]
            if inside(pts):
                rivers.append((t["waterway"], pathd(rdp(pts, EPS))))
        elif "highway" in t:
            pts = [proj(*q) for q in geom(e)]
            if inside(pts):
                roads.append((t["highway"], pathd(rdp(pts, EPS))))
    return water, rivers, roads


def build_route(els):
    pos, adj = {}, {}
    for e in els:
        t = e.get("tags", {})
        if e["type"] != "way" or "highway" not in t:
            continue
        for i, (n, q) in enumerate(zip(e["nodes"], geom(e))):
            pos[n] = q
            if i:
                m = e["nodes"][i - 1]
                d = hav(pos[m], q)
                adj.setdefault(m, []).append((n, d, t["highway"]))
                adj.setdefault(n, []).append((m, d, t["highway"]))
    # Ramps (*_link) are not in the extract: join nodes closer than 60 m so the graph stays connected.
    cells = {}
    for n, (la, lo) in pos.items():
        cells.setdefault((round(la / 0.0006), round(lo / 0.0006)), []).append(n)
    for (ci, cj), ns in cells.items():
        near = [m for di in (-1, 0, 1) for dj in (-1, 0, 1) for m in cells.get((ci + di, cj + dj), [])]
        for n in ns:
            linked = {m for m, _, _ in adj.get(n, [])}
            for m in near:
                if m != n and m not in linked and hav(pos[n], pos[m]) < 60:
                    adj.setdefault(n, []).append((m, hav(pos[n], pos[m]), "link"))

    def dijkstra(a, b):
        dist, prev, pq = {a: 0}, {}, [(0, a)]
        while pq:
            d, n = heapq.heappop(pq)
            if n == b:
                break
            if d > dist[n]:
                continue
            for m, w, hw in adj.get(n, []):
                if d + w < dist.get(m, 1e18):
                    dist[m], prev[m] = d + w, (n, hw)
                    heapq.heappush(pq, (d + w, m))
        seq, n = [], b
        while n != a:
            seq.append((n, prev[n][1]))
            n = prev[n][0]
        return seq[::-1]

    road = [n for e in els if e.get("tags", {}).get("name") == ROUTE_ROAD for n in e["nodes"]]
    start = min(road, key=lambda n: hav(pos[n], ROUTE_START))
    via = min(pos, key=lambda n: hav(pos[n], ROUTE_VIA))
    goal = min(pos, key=lambda n: hav(pos[n], ROUTE_END))
    path = [(start, None)] + dijkstra(start, via) + dijkstra(via, goal)

    # GPS fixes: spacing by road class (faster roads, sparser fixes) plus a little lateral jitter.
    rnd = random.Random(7)
    fixes, carry = [proj(*pos[start])], 0.0
    for (a, _), (b, hw) in zip(path, path[1:]):
        pa, pb = pos[a], pos[b]
        seg, sp = hav(pa, pb), SPACING.get(hw or "", 320)
        s = sp - carry
        while s <= seg:
            f = s / seg
            x, y = proj(pa[0] + (pb[0] - pa[0]) * f, pa[1] + (pb[1] - pa[1]) * f)
            (ax, ay), (bx, by) = proj(*pa), proj(*pb)
            length, j = math.hypot(bx - ax, by - ay) or 1, rnd.gauss(0, 9) * PX_PER_M
            fixes.append((x - (by - ay) / length * j, y + (bx - ax) / length * j))
            s += sp
        carry = seg - (s - sp)
    end = proj(*pos[goal])
    fixes.append(end)
    fixes = [p for i, p in enumerate(fixes) if i == 0 or math.dist(p, fixes[i - 1]) > 2.5]
    cum = [0.0]
    for a, b in zip(fixes, fixes[1:]):
        cum.append(cum[-1] + math.dist(a, b))
    return fixes, cum, end


def render(c, layers, route, text):
    water, rivers, roads = layers
    fixes, cum, end = route
    total, draw, t0 = cum[-1], 2.8, 0.35
    rw = {"motorway": 1.5, "trunk": 1.5, "primary": 1.1, "secondary": 0.7}
    vw = {"river": 1.4, "canal": 0.8, "stream": 0.7}
    name1, name2, sub, attr = text
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img">',
        f'<title>{" ".join(NAME_LINES)}, {SUBTITLE[0].lower() + SUBTITLE[1:]}</title>',
        f'''<style>
.trk{{stroke-dasharray:{total:.0f};stroke-dashoffset:0;animation:draw {draw}s linear {t0}s both}}
.fx{{animation:pop .25s ease-out both}}
.pin{{animation:pop .3s ease-out {t0 + draw:.2f}s both}}
.ring{{transform-box:fill-box;transform-origin:center;opacity:0;animation:ping 1.8s ease-out {t0 + draw + .2:.2f}s 3}}
@keyframes draw{{from{{stroke-dashoffset:{total:.0f}}}to{{stroke-dashoffset:0}}}}
@keyframes pop{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes ping{{0%{{opacity:.55;transform:scale(1)}}100%{{opacity:0;transform:scale(3.4)}}}}
@media (prefers-reduced-motion:reduce){{.trk,.fx,.pin{{animation:none}}.ring{{display:none}}}}
</style>''',
        '<defs>',
        '<linearGradient id="fx" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity=".18"/>'
        '<stop offset=".36" stop-color="#fff" stop-opacity=".45"/><stop offset=".55" stop-color="#fff"/>'
        '<stop offset=".97" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>',
        '<linearGradient id="fy" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset=".08" stop-color="#fff"/><stop offset=".92" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>',
        f'<mask id="mx" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="url(#fx)"/></mask>',
        f'<mask id="my" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="url(#fy)"/></mask>',
        f'<clipPath id="cp"><rect width="{W}" height="{H}"/></clipPath>',
        '</defs>',
        '<g clip-path="url(#cp)"><g mask="url(#mx)"><g mask="url(#my)">',
        f'<g fill="none" stroke="{c["road"]}" stroke-linecap="round" stroke-linejoin="round">'
        + "".join(f'<path d="{d}" stroke-width="{rw.get(h, .7)}"/>' for h, d in roads) + '</g>',
        f'<path fill="{c["wfill"]}" fill-rule="evenodd" d="{" ".join(water)}"/>',
        f'<g fill="none" stroke="{c["wline"]}" stroke-linecap="round" stroke-linejoin="round">'
        + "".join(f'<path d="{d}" stroke-width="{vw.get(k, .7)}"/>' for k, d in rivers) + '</g>',
        '</g></g>',
        '<g mask="url(#my)">',
        f'<path class="trk" fill="none" stroke="{c["route"]}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" d="{pathd(fixes)}"/>',
        f'<g fill="{c["route"]}">' + "".join(
            f'<circle class="fx" cx="{x:.1f}" cy="{y:.1f}" r="3.1" style="animation-delay:{t0 + draw * cum[i] / total:.2f}s"/>'
            for i, (x, y) in enumerate(fixes[:-1])) + '</g>',
        f'<circle class="ring" cx="{end[0]:.1f}" cy="{end[1]:.1f}" r="7" fill="none" stroke="{c["route"]}" stroke-width="2"/>',
        '</g>',
        f'<circle class="pin" cx="{end[0]:.1f}" cy="{end[1]:.1f}" r="7.5" fill="{c["route"]}" stroke="{c["bg"]}" stroke-width="3"/>',
        '</g>',
        # label halos, as on printed maps
        f'<g fill="{c["bg"]}" stroke="{c["bg"]}" stroke-width="9" stroke-linejoin="round"><path d="{name1}"/><path d="{name2}"/><path d="{sub}"/></g>',
        f'<g fill="{c["ink"]}"><path d="{name1}"/><path d="{name2}"/></g>',
        f'<path fill="{c["muted"]}" d="{sub}"/>',
        f'<path fill="{c["faint"]}" d="{attr}"/>',
        '</svg>'])


def main():
    tmp = tempfile.gettempdir()
    ap = argparse.ArgumentParser(description="Generate the profile header SVGs (light and dark).")
    ap.add_argument("--osm", default=os.path.join(tmp, "villahermosa-osm.json"), help="cached Overpass JSON")
    ap.add_argument("--font", default=os.path.join(tmp, "Overpass-wght.ttf"), help="Overpass variable font")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets"))
    args = ap.parse_args()

    els = fetch_osm(args.osm)
    font = fetch_font(args.font)
    # x offsets compensate each first glyph's side bearing so the stems align with the README text column
    text = (text_path(font, NAME_LINES[0], 800, 66, -4.1, 176, tracking=-0.005),
            text_path(font, NAME_LINES[1], 800, 66, -3.0, 244, tracking=-0.005),
            text_path(font, SUBTITLE, 400, 27, -1.0, 296),
            text_path(font, ATTRIBUTION, 400, 17, 0.5, H - 14))
    layers, route = build_layers(els), build_route(els)
    for theme, colors in THEMES.items():
        path = os.path.join(args.out, f"header-{theme}.svg")
        open(path, "w").write(render(colors, layers, route, text))
        print("wrote", os.path.normpath(path))


if __name__ == "__main__":
    main()
