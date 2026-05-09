#!/usr/bin/env python3
"""
Gerador de Material de Estudo de Mandarim com Letras de Música
================================================================
Edite o dicionário CONFIG abaixo com a letra da música que você quer estudar
e rode o script. Ele gera um PDF com:
  • Tradução em português acima de cada refrão (palavras coloridas)
  • Caracteres chineses no meio (estilo Kaiti 楷体, ideal para caligrafia)
  • Pinyin abaixo dos caracteres (mesma cor do caractere)
  • Grade 田字格 (tián-zì-gé) para praticar caligrafia

Caracteres em chinês simplificado (简体字).

Como rodar:
    python3 gerador_mandarim.py

Saída: o arquivo PDF cujo nome estiver em CONFIG["output"].

Dependências (Ubuntu/Debian):
    pip install weasyprint
    sudo apt install fonts-arphic-ukai fonts-arphic-bkai00mp \\
                     fonts-noto-cjk fonts-dejavu

A fonte AR PL UKai CN (do pacote fonts-arphic-ukai) é uma Kaiti livre, em
chinês simplificado. Se não estiver instalada, o script cai no fallback
sans-serif (Noto Sans CJK SC), com aviso impresso no terminal.
"""

import html as html_lib
import os
import subprocess
from weasyprint import HTML, CSS


# ============================================================================
# CONFIGURAÇÃO — preencha com a letra da música que você quer estudar.
#
# Estrutura:
#   • "refraos" é uma lista de refrões.
#   • Cada refrão tem "label" (rótulo) e "lines" (linhas do refrão).
#   • Cada linha tem "segments": lista dos pedaços coloridos da linha.
#   • Cada segmento agrupa um trecho que vai aparecer numa MESMA cor nos
#     três níveis: tradução em português, caractere e pinyin.
#
# REGRA IMPORTANTE: o número de sílabas em "py" (separadas por espaço) deve
# bater com o número de caracteres em "zh". Exemplo:
#   {"zh": "你不知道", "py": "nǐ bù zhī dào", "pt": "você não sabe"}
#       4 caracteres ↔ 4 sílabas pinyin   ✓
# ============================================================================

CONFIG = {
    "title": "时光背面的我",
    "title_pinyin": "Shíguāng bèimiàn de wǒ",
    "artist": "鱼闪闪 BLING",
    "output": "estudo_mandarim.pdf",

    "refraos": [
        # Refrões de DEMONSTRAÇÃO (caracteres simplificados 简体字).
        # Substitua pelos refrões da música que você está estudando.
        # As cores são atribuídas automaticamente, na ordem dos segmentos
        # dentro de cada refrão.
        {
            "label": "Refrão de exemplo · 1",
            "lines": [
                {
                    "segments": [
                        {"zh": "学中文",   "py": "xué zhōng wén", "pt": "Aprender chinês"},
                        {"zh": "很有意思", "py": "hěn yǒu yì si", "pt": "é muito interessante"},
                    ]
                },
                {
                    "segments": [
                        {"zh": "我喜欢",   "py": "wǒ xǐ huān",    "pt": "Eu gosto"},
                        {"zh": "听音乐",   "py": "tīng yīn yuè",  "pt": "de ouvir música"},
                    ]
                },
            ]
        },
        {
            "label": "Refrão de exemplo · 2",
            "lines": [
                {
                    "segments": [
                        {"zh": "今天",   "py": "jīn tiān",   "pt": "Hoje"},
                        {"zh": "天气",   "py": "tiān qì",    "pt": "o tempo"},
                        {"zh": "很好",   "py": "hěn hǎo",    "pt": "está muito bom"},
                    ]
                },
                {
                    "segments": [
                        {"zh": "我们",   "py": "wǒ men",         "pt": "Nós"},
                        {"zh": "一起去", "py": "yì qǐ qù",       "pt": "vamos juntos"},
                        {"zh": "公园",   "py": "gōng yuán",      "pt": "ao parque"},
                    ]
                },
            ]
        },
    ],

    # Quantas linhas de células 田字格 desenhar abaixo de cada refrão para
    # praticar caligrafia.
    "practice_rows": 3,

    # Quantas células por linha na grade de caligrafia (calcule pela largura
    # da página). 14 cabe confortavelmente em A4.
    "practice_cols": 14,
}


# ============================================================================
# Daqui para baixo é o motor de renderização.  Não precisa editar para usar.
# ============================================================================

PALETTE = [
    "#C1272D",  # vermelho
    "#0071BC",  # azul
    "#2E8B57",  # verde
    "#E67E22",  # laranja
    "#6A1B9A",  # roxo
    "#00838F",  # teal
    "#B8860B",  # mostarda
    "#8B4513",  # marrom
    "#1E3A5F",  # azul-marinho
    "#B83280",  # rosa
    "#37474F",  # cinza-escuro
    "#5D4037",  # café
]


def assign_colors(refrao):
    """Atribui uma cor a cada segmento dentro de um refrão (sequencial)."""
    idx = 0
    for line in refrao["lines"]:
        for seg in line["segments"]:
            seg["_color"] = PALETTE[idx % len(PALETTE)]
            idx += 1


def render_pt_line(segments):
    """Linha em português: cada segmento com sua cor, separados por ' · '."""
    parts = []
    for i, seg in enumerate(segments):
        if i > 0:
            parts.append('<span class="sep">·</span>')
        text = html_lib.escape(seg["pt"])
        parts.append(f'<span class="pt-seg" style="color:{seg["_color"]}">{text}</span>')
    return '<div class="pt-line">' + " ".join(parts) + "</div>"


def render_zh_line(segments):
    """Linha de caracteres chineses + pinyin: cada caractere num 'slot' com
    pinyin centralizado abaixo, ambos na cor do segmento."""
    slots = []
    for s_idx, seg in enumerate(segments):
        chars = list(seg["zh"])
        syls = seg["py"].split()
        # alinha número de sílabas e caracteres
        while len(syls) < len(chars):
            syls.append("")
        syls = syls[: len(chars)]

        for ch, sy in zip(chars, syls):
            ch_e = html_lib.escape(ch)
            sy_e = html_lib.escape(sy)
            slots.append(
                f'<span class="slot" style="color:{seg["_color"]}">'
                f'<span class="zh">{ch_e}</span>'
                f'<span class="py">{sy_e}</span>'
                f"</span>"
            )
        # marca o fim de cada segmento com um pequeno espaço (visual)
        if s_idx < len(segments) - 1:
            slots.append('<span class="seg-gap"></span>')
    return '<div class="zh-line">' + "".join(slots) + "</div>"


def render_practice_grid(rows, cols, cell_size_cm=1.18):
    """Grade 田字格 vazia desenhada como uma única SVG, garantindo que as
    células saiam quadradas e proporções fiquem corretas no PDF."""
    unit = 100  # unidades por célula no espaço SVG
    w_units = cols * unit
    h_units = rows * unit
    width_cm = cols * cell_size_cm
    height_cm = rows * cell_size_cm

    parts = [
        f'<svg class="practice-grid" '
        f'width="{width_cm}cm" height="{height_cm}cm" '
        f'viewBox="0 0 {w_units} {h_units}" '
        f'xmlns="http://www.w3.org/2000/svg">'
    ]

    # Borda externa de cada célula + cruz interna fina (linhas sólidas claras)
    for row in range(rows):
        for col in range(cols):
            x = col * unit
            y = row * unit
            # quadrado
            parts.append(
                f'<rect x="{x + 0.75}" y="{y + 0.75}" width="{unit - 1.5}" height="{unit - 1.5}" '
                f'fill="none" stroke="#444" stroke-width="1.5"/>'
            )
            # cruz interna
            cx = x + unit / 2
            cy = y + unit / 2
            parts.append(
                f'<line x1="{cx}" y1="{y + 3}" x2="{cx}" y2="{y + unit - 3}" '
                f'stroke="#bbb" stroke-width="0.6"/>'
            )
            parts.append(
                f'<line x1="{x + 3}" y1="{cy}" x2="{x + unit - 3}" y2="{cy}" '
                f'stroke="#bbb" stroke-width="0.6"/>'
            )

    parts.append("</svg>")
    return '<div class="grid-wrap">' + "".join(parts) + "</div>"


def render_refrao(refrao, practice_rows, practice_cols):
    assign_colors(refrao)

    label = html_lib.escape(refrao.get("label", "Refrão"))
    lines_html = []
    for line in refrao["lines"]:
        segs = line["segments"]
        lines_html.append('<div class="line">')
        lines_html.append(render_pt_line(segs))
        lines_html.append(render_zh_line(segs))
        lines_html.append("</div>")

    grid = render_practice_grid(practice_rows, practice_cols)

    return f"""
    <section class="refrao">
        <h2>{label}</h2>
        {''.join(lines_html)}
        <div class="caligrafia-rotulo">Caligrafia · 书法练习</div>
        {grid}
    </section>
    """


def build_html(config):
    refraos_html = "".join(
        render_refrao(r, config.get("practice_rows", 2), config.get("practice_cols", 14))
        for r in config["refraos"]
    )

    title = html_lib.escape(config.get("title", ""))
    title_py = html_lib.escape(config.get("title_pinyin", ""))
    artist = html_lib.escape(config.get("artist", ""))

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Estudo de Mandarim</title>
<style>
@page {{
    size: A4;
    margin: 1.6cm 1.8cm;
}}

* {{ box-sizing: border-box; }}

body {{
    font-family: "DejaVu Sans", "Liberation Sans", sans-serif;
    color: #222;
    font-size: 11pt;
    line-height: 1.4;
}}

.zh, .zh-title {{
    /* Kaiti (楷体) — estilo caligráfico ideal para aprendizado e prática
       de caligrafia. Fallbacks para sans-serif se Kaiti não estiver
       instalada. */
    font-family: "AR PL UKai CN", "AR PL KaitiM GB", "KaiTi", "STKaiti",
                 "Kaiti SC", "Noto Sans CJK SC", "WenQuanYi Zen Hei", serif;
}}

header.doc-header {{
    border-bottom: 1.5pt solid #333;
    padding-bottom: 8pt;
    margin-bottom: 14pt;
}}
header.doc-header .zh-title {{
    font-size: 22pt;
    font-weight: 600;
    margin: 0;
    line-height: 1.1;
}}
header.doc-header .pinyin-title {{
    font-style: italic;
    color: #555;
    font-size: 12pt;
    margin-top: 2pt;
}}
header.doc-header .artist {{
    color: #777;
    font-size: 10pt;
    margin-top: 2pt;
}}
header.doc-header .legend {{
    font-style: italic;
    color: #666;
    font-size: 8.5pt;
    margin-top: 6pt;
}}

section.refrao {{
    margin-bottom: 16pt;
    page-break-inside: avoid;
}}

section.refrao h2 {{
    font-size: 12pt;
    font-weight: 700;
    margin: 0 0 4pt 0;
    border-bottom: 0.5pt solid #ccc;
    padding-bottom: 3pt;
}}

.line {{
    margin-bottom: 10pt;
}}

.pt-line {{
    font-weight: 700;
    font-size: 11pt;
    margin-bottom: 4pt;
    line-height: 1.4;
}}
.pt-line .sep {{
    color: #aaa;
    font-weight: 400;
    margin: 0 4pt;
}}

.zh-line {{
    line-height: 1;
    margin-bottom: 0;
}}
.zh-line .slot {{
    display: inline-block;
    text-align: center;
    vertical-align: top;
    margin: 0 1pt;
    min-width: 1.2em;
}}
.zh-line .slot .zh {{
    display: block;
    font-size: 20pt;
    line-height: 1.05;
}}
.zh-line .slot .py {{
    display: block;
    font-size: 9pt;
    line-height: 1.4;
    margin-top: 1pt;
    /* pinyin não é em itálico mas usa fonte com tone marks */
    font-family: "DejaVu Sans", "Liberation Sans", sans-serif;
    font-weight: 500;
}}
.zh-line .seg-gap {{
    display: inline-block;
    width: 6pt;
}}

.caligrafia-rotulo {{
    font-style: italic;
    color: #666;
    font-size: 9pt;
    margin: 8pt 0 4pt 0;
}}

.grid-wrap {{
    margin-top: 2pt;
    line-height: 0;
}}
.practice-grid {{
    display: block;
}}

</style>
</head>
<body>
<header class="doc-header">
    <h1 class="zh-title">{title}</h1>
    {f'<div class="pinyin-title">{title_py}</div>' if title_py else ''}
    {f'<div class="artist">— {artist}</div>' if artist else ''}
    <div class="legend">Cores correspondentes ligam tradução (português), caractere e pinyin do mesmo segmento.</div>
</header>
{refraos_html}
</body>
</html>
"""


def _check_kaiti_available():
    """Avisa se nenhuma fonte Kaiti foi encontrada (cai no fallback sans)."""
    try:
        result = subprocess.run(
            ["fc-list", ":lang=zh"], capture_output=True, text=True, timeout=5
        )
        listing = result.stdout.lower()
        if any(k in listing for k in ["ukai", "kaiti", "kaitim", "kai cn"]):
            return True
    except (FileNotFoundError, subprocess.SubprocessError):
        pass
    print(
        "AVISO: nenhuma fonte Kaiti (楷体) encontrada — usando fallback "
        "sans-serif para os caracteres chineses."
    )
    print("  Instale com:  sudo apt install fonts-arphic-ukai fonts-arphic-bkai00mp")
    return False


def build_pdf(config):
    output = config.get("output", "estudo_mandarim.pdf")
    _check_kaiti_available()
    html_str = build_html(config)
    HTML(string=html_str).write_pdf(output)
    print(f"PDF gerado: {output}")


if __name__ == "__main__":
    build_pdf(CONFIG)
