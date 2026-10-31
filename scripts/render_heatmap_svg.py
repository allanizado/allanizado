"""Renderiza data/contributions.json como contrib-heatmap.svg (53 semanas x 7 dias),
com revelacao diagonal unica (CSS keyframes) e rodape de estatisticas.
"""
import json
from datetime import date

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
BG = "#0d1117"
DIM = "#8b949e"
BOX, GAP = 12, 3
STEP = BOX + GAP
PAD_L, PAD_T = 44, 56
OUT = "contrib-heatmap.svg"
MONTHS = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
DOW = {1: "Seg", 3: "Qua", 5: "Sex"}


def main() -> None:
    data = json.load(open("data/contributions.json", encoding="utf-8"))
    days = data["days"]
    st = data["stats"]

    # semana comeca no domingo; alinha a primeira coluna
    first = date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7
    cells = []
    for i, d in enumerate(days):
        idx = i + offset
        cells.append((idx // 7, idx % 7, d))
    weeks = cells[-1][0] + 1

    W = PAD_L + weeks * STEP + 20
    H = PAD_T + 7 * STEP + 62

    # nivel 5 (neon) so para os dias mais fortes do ano
    maxc = max((d["count"] for d in days), default=0)

    def level(d):
        lv = d["level"]
        if lv >= 4 and maxc and d["count"] >= maxc * 0.8:
            return 5
        return min(lv, 4)

    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        "<style>",
        "text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:10px;fill:%s}" % DIM,
        ".b{opacity:0;animation:slide .45s ease-out forwards}",
        "@keyframes slide{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:translateY(0)}}",
        "</style>",
        f'<rect width="{W}" height="{H}" rx="8" fill="{BG}" stroke="#30363d"/>',
        f'<text x="{PAD_L}" y="26" style="font-size:12px;fill:#c9d1d9">{st["total"]:,} contribuições no último ano</text>'.replace(",", "."),
    ]

    # rotulos de mes (descarta o primeiro se colidir com o seguinte)
    marks = []
    last_m = None
    for w, dow, d in cells:
        if dow == 0:
            m = int(d["date"][5:7])
            if m != last_m:
                marks.append((w, m))
                last_m = m
    if len(marks) > 1 and marks[1][0] - marks[0][0] < 3:
        marks = marks[1:]
    for w, m in marks:
        o.append(f'<text x="{PAD_L + w * STEP}" y="{PAD_T - 8}">{MONTHS[m - 1]}</text>')
    for r, label in DOW.items():
        o.append(f'<text x="10" y="{PAD_T + r * STEP + 10}">{label}</text>')

    for w, dow, d in cells:
        x = PAD_L + w * STEP
        y = PAD_T + dow * STEP
        delay = (w + dow) * 0.012
        c = PALETTE[level(d)]
        o.append(
            f'<rect class="b" x="{x}" y="{y}" width="{BOX}" height="{BOX}" rx="3" fill="{c}" style="animation-delay:{delay:.3f}s">'
            f'<title>{d["count"]} em {d["date"]}</title></rect>'
        )

    # legenda
    ly = PAD_T + 7 * STEP + 18
    lx = W - 20 - (6 * STEP + 70)
    o.append(f'<text x="{lx}" y="{ly + 10}">Menos</text>')
    for i, c in enumerate(PALETTE):
        o.append(f'<rect x="{lx + 38 + i * STEP}" y="{ly}" width="{BOX}" height="{BOX}" rx="3" fill="{c}"/>')
    o.append(f'<text x="{lx + 42 + 6 * STEP}" y="{ly + 10}">Mais</text>')

    # rodape com estatisticas
    bd = st["best_day"]
    foot = (
        f'sequência atual: {st["current_streak"]} dias   '
        f'maior sequência: {st["longest_streak"]} dias   '
        f'melhor dia: {bd["count"]} em {bd["date"]}'
    )
    o.append(f'<text x="{PAD_L}" y="{H - 16}">{foot}</text>')
    o.append("</svg>")
    open(OUT, "w", encoding="utf-8").write("\n".join(o))
    print(f"ok: {OUT}")


if __name__ == "__main__":
    main()
