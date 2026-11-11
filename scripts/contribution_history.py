#!/usr/bin/env python3
"""Render a multi-year contribution heatmap (one row per year, one cell per week).

GitHub's own graph only shows the last 12 months; older years hide behind the year
tabs. This card shows every year at once. It reads the public contribution calendar
through the GraphQL API, so the workflow's GITHUB_TOKEN is enough (no PAT). Private
contributions appear as counts because "Include private contributions on my
profile" is enabled.

Usage:
    GITHUB_TOKEN=... python3 scripts/contribution_history.py --user Darkerc \
        --out profile/history.svg --out-dark profile/history-dark.svg
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from html import escape
from pathlib import Path

API = "https://api.github.com/graphql"
QUERY = """
query($login: String!, $from: DateTime, $to: DateTime) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionYears
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
    }
  }
}
"""

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


@dataclass(frozen=True)
class Theme:
    text: str
    muted: str
    cells: tuple[str, str, str, str, str]  # level 0 (none) .. 4 (most)


# GitHub's own contribution-graph scales, so the card reads like the native graph.
LIGHT = Theme("#1f2328", "#59636e", ("#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"))
DARK = Theme("#e6edf3", "#9198a1", ("#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"))


def gql(token: str, variables: dict[str, str]) -> dict:
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": QUERY, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "profile-cards"},
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        payload = json.load(res)
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])
    return payload["data"]["user"]["contributionsCollection"]


def fetch(token: str, login: str) -> dict[int, dict[date, int]]:
    years = sorted(gql(token, {"login": login})["contributionYears"])
    now = datetime.now(timezone.utc)
    out: dict[int, dict[date, int]] = {}
    for y in years:
        end = min(datetime(y, 12, 31, 23, 59, 59, tzinfo=timezone.utc), now)
        cal = gql(token, {"login": login, "from": f"{y}-01-01T00:00:00Z", "to": end.isoformat()})
        days = {}
        for week in cal["contributionCalendar"]["weeks"]:
            for d in week["contributionDays"]:
                day = date.fromisoformat(d["date"])
                if day.year == y:
                    days[day] = d["contributionCount"]
        out[y] = days
    return out


def week_col(d: date) -> int:
    """Column of `d` in its year, with Sunday-start weeks like GitHub's graph."""
    jan1 = date(d.year, 1, 1)
    first_sunday = jan1 - timedelta(days=(jan1.weekday() + 1) % 7)
    return (d - first_sunday).days // 7


def levels(weekly: list[int]) -> list[int]:
    """Quartile thresholds over all non-empty weeks, so every year shares one scale."""
    nonzero = sorted(v for v in weekly if v > 0)
    if not nonzero:
        return [1, 1, 1]
    q = lambda p: nonzero[min(len(nonzero) - 1, int(p * len(nonzero)))]
    return [q(0.25), q(0.5), q(0.75)]


def level_of(v: int, cuts: list[int]) -> int:
    if v <= 0:
        return 0
    return 1 + sum(v > c for c in cuts)


def render(data: dict[int, dict[date, int]], theme: Theme, today: date) -> str:
    cell, gap, row_gap = 10, 2, 4
    pitch = cell + gap
    pad, label_w, total_w = 16, 40, 64
    title_h, months_h, legend_h = 46, 16, 30
    cols = 54
    grid_x = pad + label_w
    grid_w = cols * pitch - gap
    width = grid_x + grid_w + total_w + pad
    years = sorted(data)
    grid_y = pad + title_h + months_h
    height = grid_y + len(years) * (cell + row_gap) - row_gap + legend_h + pad

    weekly: dict[int, dict[int, int]] = {}
    for y, days in data.items():
        w: dict[int, int] = {}
        for d, n in days.items():
            w[week_col(d)] = w.get(week_col(d), 0) + n
        weekly[y] = w
    cuts = levels([v for w in weekly.values() for v in w.values()])
    totals = {y: sum(days.values()) for y, days in data.items()}
    first, grand = years[0], sum(totals.values())

    desc = "; ".join(f"{y}: {totals[y]:,} contributions" for y in years)
    font = "font-family=\"-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif\""
    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'role="img" aria-labelledby="t d" {font}>',
        f'<title id="t">Contribution history since {first}</title>',
        f'<desc id="d">Weekly contributions per year. {escape(desc)}. Total {grand:,}.</desc>',
        f'<text x="{pad}" y="{pad + 14}" font-size="15" font-weight="600" fill="{theme.text}">Contribution history</text>',
        f'<text x="{pad}" y="{pad + 33}" font-size="11.5" fill="{theme.muted}">'
        f"{grand:,} contributions since {first} · one cell per week · private GitHub work + GitLab commits (2020–2025)</text>",
    ]
    # Month labels, positioned on a generic year (columns shift by at most one between years).
    ref = today.year
    for m, name in enumerate(MONTHS, start=1):
        x = grid_x + week_col(date(ref, m, 1)) * pitch
        o.append(f'<text x="{x}" y="{grid_y - 5}" font-size="10" fill="{theme.muted}">{name}</text>')
    o.append(
        f'<text x="{width - pad}" y="{grid_y - 5}" font-size="10" fill="{theme.muted}" text-anchor="end">Total</text>'
    )

    for i, y in enumerate(years):
        top = grid_y + i * (cell + row_gap)
        mid = top + cell - 1
        o.append(f'<text x="{grid_x - 8}" y="{mid}" font-size="10.5" fill="{theme.muted}" text-anchor="end">{y}</text>')
        last_col = week_col(date(y, 12, 31)) if y < today.year else week_col(today)
        for c in range(last_col + 1):
            v = weekly[y].get(c, 0)
            fill = theme.cells[level_of(v, cuts)]
            o.append(f'<rect x="{grid_x + c * pitch}" y="{top}" width="{cell}" height="{cell}" rx="2" fill="{fill}"/>')
        label = f"{totals[y]:,}" + (" so far" if y == today.year else "")
        o.append(
            f'<text x="{width - pad}" y="{mid}" font-size="10.5" fill="{theme.text}" text-anchor="end">{label}</text>'
        )

    ly = height - pad - 10
    lx = grid_x + grid_w - (5 * pitch - gap)
    o.append(f'<text x="{lx - 6}" y="{ly + cell - 1}" font-size="10" fill="{theme.muted}" text-anchor="end">Less</text>')
    for k, fill in enumerate(theme.cells):
        o.append(f'<rect x="{lx + k * pitch}" y="{ly}" width="{cell}" height="{cell}" rx="2" fill="{fill}"/>')
    o.append(f'<text x="{lx + 5 * pitch + 4}" y="{ly + cell - 1}" font-size="10" fill="{theme.muted}">More</text>')
    o.append(
        f'<text x="{pad}" y="{ly + cell - 1}" font-size="10" fill="{theme.muted}">'
        f"Updated {today.isoformat()}</text>"
    )
    o.append("</svg>")
    return "\n".join(o) + "\n"


def write(path: str, content: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(content)
    tmp.replace(p)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--out-dark", required=True)
    args = ap.parse_args()
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN is not set", file=sys.stderr)
        return 1
    data = fetch(token, args.user)
    today = datetime.now(timezone.utc).date()
    write(args.out, render(data, LIGHT, today))
    write(args.out_dark, render(data, DARK, today))
    print(f"years={sorted(data)} total={sum(sum(d.values()) for d in data.values())}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
