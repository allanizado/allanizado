"""Le o calendario publico de contribuicoes (sem token) e grava data/contributions.json.

Uso: python scripts/fetch_contributions.py [usuario]
"""
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime

import requests
from bs4 import BeautifulSoup

USER = sys.argv[1] if len(sys.argv) > 1 else "allanizado"
URL = f"https://github.com/users/{USER}/contributions"


def parse(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    tips = {}
    for tip in soup.find_all("tool-tip"):
        m = re.match(r"\s*(No|\d+)\s+contribution", tip.get_text(" ", strip=True))
        if m and tip.get("for"):
            tips[tip["for"]] = 0 if m.group(1) == "No" else int(m.group(1))
    days = []
    for td in soup.select("td.ContributionCalendar-day"):
        d = td.get("data-date")
        if not d:
            continue
        days.append(
            {
                "date": d,
                "level": int(td.get("data-level", 0)),
                "count": tips.get(td.get("id"), 0),
            }
        )
    days.sort(key=lambda x: x["date"])
    return days


def stats(days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)
    longest = cur = 0
    for d in days:
        cur = cur + 1 if d["count"] > 0 else 0
        longest = max(longest, cur)
    # sequencia atual: ignora hoje se ainda estiver zerado
    current = 0
    for d in reversed(days):
        if d["count"] > 0:
            current += 1
        elif d is days[-1]:
            continue
        else:
            break
    best = max(days, key=lambda x: x["count"]) if days else {"date": "", "count": 0}
    monthly = defaultdict(int)
    for d in days:
        monthly[d["date"][:7]] += d["count"]
    return {
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best,
        "monthly": dict(monthly),
    }


def main() -> None:
    r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0 (profile-readme-bot)"}, timeout=30)
    r.raise_for_status()
    days = parse(r.text)
    if not days:
        raise SystemExit("nenhum dia encontrado no HTML do calendario")
    data = {
        "user": USER,
        "generated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "days": days,
        "stats": stats(days),
    }
    os.makedirs("data", exist_ok=True)
    with open("data/contributions.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"ok: {len(days)} dias, {data['stats']['total']} contribuicoes")


if __name__ == "__main__":
    main()
