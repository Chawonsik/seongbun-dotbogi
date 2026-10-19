"""Build docs/slides/formal/deck.html: the formal 14-slide deck with topic titles."""
import json
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
DATA = json.loads((ROOT / "docs/report/data.json").read_text(encoding="utf-8"))
OUT = ROOT / "docs/slides/formal/deck.html"
TOTAL = 14
INK, SUB, LINE, ACC, SOFT, SOFTBG = "#111827", "#6b7280", "#e5e7eb", "#2F5BEA", "#9db4f5", "#eef3fe"
SECTIONS = {1: "문제 정의", 2: "실험 설계", 3: "결과 분석", 4: "결론과 제안"}

CSS = """
@page{size:1920px 1080px;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
html{background:#e5e7eb}
body{font-family:"Noto Sans KR",sans-serif;color:#111827;-webkit-print-color-adjust:exact;print-color-adjust:exact;padding:40px 0}
.slide{position:relative;width:1920px;height:1080px;background:#fff;overflow:hidden;margin:0 auto 40px;zoom:var(--z,1);break-after:page}
@media print{html{background:#fff}body{padding:0}.slide{margin:0;zoom:1!important}}
.top{position:absolute;left:112px;right:112px;top:56px;display:flex;justify-content:space-between;font-size:24px;color:#6b7280;letter-spacing:.04em}
.top b{color:#2F5BEA;font-weight:700}
h1{position:absolute;left:112px;right:112px;top:104px;font-size:50px;font-weight:800;letter-spacing:-.01em;line-height:1.2;white-space:nowrap}
.sub{position:absolute;left:112px;right:112px;top:178px;font-size:28px;color:#6b7280;white-space:nowrap}
.rule{position:absolute;left:112px;right:112px;top:228px;border-top:2px solid #111827}
.foot{position:absolute;left:112px;right:112px;bottom:40px;display:flex;justify-content:space-between;font-size:24px;color:#6b7280;border-top:1px solid #e5e7eb;padding-top:12px}
.a{position:absolute}
.L{position:absolute;left:112px;width:1000px}
.R{position:absolute;left:1180px;right:112px}
.W{position:absolute;left:112px;right:112px}
.h3{font-size:28px;font-weight:700;margin-bottom:14px}
.leg{font-size:24px;color:#6b7280;margin-bottom:6px}
.leg i{display:inline-block;width:28px;height:0;border-top:4px solid #2F5BEA;vertical-align:middle;margin-right:8px}
.leg i.b{border-top:3px dashed #9db4f5;margin-left:22px}
table{width:100%;border-collapse:collapse;font-size:28px}
th{font-size:24px;color:#6b7280;font-weight:500;text-align:right;padding:0 0 10px;border-bottom:1px solid #e5e7eb;vertical-align:bottom}
th:first-child,td:first-child{text-align:left}
td{padding:14px 0;border-bottom:1px solid #e5e7eb;text-align:right;vertical-align:top;line-height:1.5}
tr.k td{font-weight:800;font-size:34px}
table.txt td,table.txt th{text-align:left;padding-right:28px}
table.txt td{padding-top:var(--p,20px);padding-bottom:var(--p,20px)}
table.txt td:last-child,table.txt th:last-child{padding-right:0}
td.lb{font-size:24px;font-weight:700;white-space:nowrap}
td.s,span.s,div.s{color:#6b7280}
.n{font-size:24px;color:#6b7280;font-weight:500}
.box{background:#eef3fe;border-left:4px solid #2F5BEA;padding:20px 24px;font-size:28px;line-height:1.55}
.box b{font-size:28px}
.fi{position:absolute;left:112px;right:112px;display:grid;grid-template-columns:1fr 1fr;gap:56px}
.fi div{border-top:1px solid #111827;padding-top:14px;font-size:28px;line-height:1.6}
.fi span,.cap{display:block;font-size:24px;font-weight:700;letter-spacing:.06em;color:#6b7280;margin-bottom:6px}
ul.b{list-style:none}
ul.b li{position:relative;padding-left:24px;font-size:28px;line-height:1.6;margin-bottom:6px}
ul.b li:before{content:"";position:absolute;left:2px;top:.72em;width:7px;height:7px;background:#111827}
.img{border:1px solid #e5e7eb;display:block;object-fit:cover;background:#fff}
.ph{position:relative;border:1px dashed #6b7280;display:flex;align-items:center;justify-content:center;text-align:center;font-size:24px;color:#6b7280;padding:16px;line-height:1.5}
.ph img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.ph:has(img){border:1px solid #e5e7eb}
.big{font-size:96px;font-weight:800;line-height:1;letter-spacing:-.02em}
.acc{color:#2F5BEA}
.code{font-family:ui-monospace,Menlo,monospace;font-size:24px;background:#eef3fe;padding:10px 14px;line-height:1.5;word-break:break-all}
.num{display:inline-block;color:#2F5BEA;font-weight:800;font-size:34px;width:56px}
.arrow{font-size:34px;color:#6b7280;font-weight:700}
.col{border-top:1px solid #e5e7eb;padding-top:14px}
.dev{width:340px;height:580px;border:9px solid #111827;border-radius:44px;overflow:hidden;background:#fff;display:flex;flex-direction:column;font-family:-apple-system,"Noto Sans KR",sans-serif;color:#111827}
.dev .st{flex:none;height:26px;padding:6px 24px 0;display:flex;justify-content:space-between;align-items:center;font-size:13px;font-weight:700}
.dev .igbar{flex:none;height:40px;padding:0 14px;display:flex;justify-content:space-between;align-items:center}
.dev .igbar .logo{font-family:"Snell Roundhand","Brush Script MT",cursive;font-size:26px;font-weight:700}
.dev .pf{display:flex;align-items:center;gap:9px;padding:8px 12px;font-size:13px;line-height:1.2}
.dev .av{width:32px;height:32px;border-radius:50%;border:1px solid #e5e7eb;object-fit:cover}
.dev .cta{display:flex;justify-content:space-between;padding:9px 12px;font-size:13px;font-weight:700;border-bottom:1px solid #e5e7eb}
.dev .acts{display:flex;justify-content:space-between;padding:8px 12px 4px}
.dev .acts span{display:flex;gap:14px}
.dev .cap2{padding:0 12px;font-size:12px;line-height:1.45}
.dev .br{flex:none;height:46px;padding:0 14px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #e5e7eb;background:#fff}
.dev .br .u{text-align:center;font-size:12px;line-height:1.3}
.dev .br .u b{display:block;font-size:13px}
.dev .br .u i{font-style:normal;color:#6b7280}
.dev .webv{flex:1;min-height:0;position:relative;overflow:hidden;background:#fff}
.dev .webv img{position:absolute;left:0;width:100%}
"""


def page(n, sec, topic, title, sub, body, source):
    return f"""<section class="slide" id="s{n}">
<div class="top"><span><b>0{sec}</b>&nbsp;&nbsp;{SECTIONS[sec]} · {topic}</span><span>성분돋보기</span></div>
<h1>{title}</h1>
<div class="sub">{sub}</div>
<div class="rule"></div>
{body}
<div class="foot"><span>{source}</span><span>@@PAGE@@ / {TOTAL}</span></div>
</section>"""


def plain(n, title, sub, body, source):
    return f"""<section class="slide" id="s{n}">
<div class="top"><span>&nbsp;</span><span>성분돋보기</span></div>
<h1>{title}</h1>
<div class="sub">{sub}</div>
<div class="rule"></div>
{body}
<div class="foot"><span>{source}</span><span>@@PAGE@@ / {TOTAL}</span></div>
</section>"""


def ph(label, src, w, h, style=""):
    return f'<div class="ph" style="width:{w}px;height:{h}px;{style}">{label}<img src="images/{src}" alt="{label}" onerror="this.remove()"></div>'


def img(src, alt, w, h, style=""):
    return f'<img class="img" src="images/{src}" alt="{alt}" style="width:{w}px;height:{h}px;{style}">'


def fnum(v):
    return f"{v:,}"


# ---------- charts ----------
def line_chart(days, series, ymax, ystep, yfmt, w=1000, h=470, end_labels=True, point_labels=()):
    x0, x1, y0, y1 = 90, 860, 400, 20
    sx = lambda i: x0 + (x1 - x0) * i / (len(days) - 1)
    sy = lambda v: y0 - (y0 - y1) * v / ymax
    out = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg" font-family="Noto Sans KR">']
    v = 0
    while v <= ymax + 1e-9:
        y = sy(v)
        out.append(f'<line x1="{x0}" x2="{x1}" y1="{y:.1f}" y2="{y:.1f}" stroke="{LINE}" stroke-width="1"/>')
        out.append(f'<text x="{x0-14}" y="{y+7:.1f}" font-size="24" fill="{SUB}" text-anchor="end">{yfmt(v)}</text>')
        v += ystep
    for i, d in enumerate(days):
        out.append(f'<text x="{sx(i):.1f}" y="448" font-size="24" fill="{SUB}" text-anchor="middle">{d}</text>')
    labels = []
    for name, vals, color, width, dash in reversed(series):
        pts = " ".join(f"{sx(i):.1f},{sy(val):.1f}" for i, val in enumerate(vals))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}" stroke-linejoin="round"/>')
        for i, val in enumerate(vals):
            out.append(f'<circle cx="{sx(i):.1f}" cy="{sy(val):.1f}" r="5" fill="{color}"/>')
        if end_labels:
            labels.append([sy(vals[-1]) + 7, f"{name} {vals[-1]:.2f}%"])
    labels.sort()
    for i in range(1, len(labels)):
        labels[i][0] = max(labels[i][0], labels[i - 1][0] + 34)
    for y, t in labels:
        out.append(f'<text x="{x1+16}" y="{y:.1f}" font-size="24" font-weight="700" fill="{INK}">{t}</text>')
    for i, val, t in point_labels:
        out.append(f'<text x="{sx(i):.1f}" y="{sy(val)-16:.1f}" font-size="24" font-weight="700" fill="{INK}" text-anchor="middle">{t}</text>')
    out.append("</svg>")
    return "".join(out)


def step_bars(steps, w=628):
    base = steps[0][1]
    row = 104
    out = [f'<svg viewBox="0 0 {w} {row*len(steps)}" width="{w}" height="{row*len(steps)}" xmlns="http://www.w3.org/2000/svg" font-family="Noto Sans KR">']
    for i, (label, v) in enumerate(steps):
        y = i * row
        pct = round(v / base * 100)
        out.append(f'<text x="0" y="{y+26}" font-size="24" fill="{INK}">{label}</text>')
        out.append(f'<text x="{w}" y="{y+26}" font-size="24" font-weight="700" fill="{INK}" text-anchor="end">{v}대 · {pct}%</text>')
        out.append(f'<rect x="0" y="{y+42}" width="{w}" height="28" fill="{SOFTBG}"/>')
        if v:
            out.append(f'<rect x="0" y="{y+42}" width="{w*v/base:.1f}" height="28" fill="{ACC}"/>')
    out.append("</svg>")
    return "".join(out)


r1, r2, land = DATA["round1"], DATA["round2"], DATA["landing"]
r2_days = [d["day"] for d in r2["daily"]]
r2_a = [100 * d["a"][0] / d["a"][1] for d in r2["daily"]]
r2_b = [100 * d["b"][0] / d["b"][1] for d in r2["daily"]]
R2_CHART = line_chart(r2_days, [("A", r2_a, ACC, 4, ""), ("B", r2_b, SOFT, 3, "8 6")], 5, 1, lambda v: f"{v:.0f}%")
ing, tex = r1["ingredient"]["daily_impressions"], r1["texture"]["daily_impressions"]
R1_CHART = line_chart(r1["days"], [("원료", ing, ACC, 4, ""), ("사용감", tex, SOFT, 3, "8 6")], 3000, 1000,
                      lambda v: fnum(int(v)), end_labels=False,
                      point_labels=[(tex.index(max(tex)), max(tex), fnum(max(tex))), (ing.index(max(ing)), max(ing), fnum(max(ing)))])
FUNNEL = step_bars([(s["label"], s["devices"]) for s in land["sections"]["steps"]])

S = []

# ---------- slides ----------
def page(sec, title, sub, body, source):
    return f"""<section class="slide">
<div class="top"><span><b>0{sec}</b>&nbsp;&nbsp;{SECTIONS[sec]}</span><span>성분돋보기</span></div>
<h1>{title}</h1>
<div class="sub">{sub}</div>
<div class="rule"></div>
{body}
<div class="foot"><span>{source}</span><span>{len(S) + 1} / {TOTAL}</span></div>
</section>"""


def plain(title, sub, body, source):
    return page(1, title, sub, body, source).replace(f'<span><b>01</b>&nbsp;&nbsp;{SECTIONS[1]}</span>', "<span>&nbsp;</span>")


ul = lambda items: '<ul class="b">' + "".join(f"<li>{x}</li>" for x in items) + "</ul>"
th2 = lambda src, name, copy: f'<th style="vertical-align:top">{img(src, name, 180, 180, "display:inline-block;margin-bottom:8px")}<br><span style="color:{SUB}">{name}</span><br><b style="color:{INK};font-size:28px;line-height:1.3">"{copy}"</b></th>'
th = lambda src, name: f'<th>{img(src, name, 180, 180, "display:inline-block;margin-bottom:10px")}<br>{name}</th>'
pct = lambda c, n: f"{100*c/n:.2f}%"
ri, rt, sd = r1["ingredient"], r1["texture"], r1["same_days"]
a, b = r2["a"], r2["b"]
l1, l2 = land["round1"], land["round2"]
MA, MB = 100 * a["clicks"] / a["impressions"], 100 * b["clicks"] / b["impressions"]

def ico(path, w=22):
    return f'<svg width="{w}" height="{w}" viewBox="0 0 24 24" fill="none" stroke="{INK}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{path}</svg>'
I_HEART = '<path d="M12 20s-7-4.4-9.2-8.6C1.4 8.6 3 5 6.4 5c2 0 3.2 1.1 3.9 2.2.3.5.9.5 1.2 0C12.2 6.1 13.4 5 15.4 5 18.8 5 20.4 8.6 19 11.4 16.8 15.6 12 20 12 20z"/>'
I_COMMENT = '<path d="M20.5 11.5a8.5 8.5 0 1 1-4-7.2 8.5 8.5 0 0 1 4 7.2z"/><path d="M20.5 20.5l-2.2-4.4"/>'
I_SEND = '<path d="M21 3 10 14"/><path d="M21 3l-7 18-4-7-7-4 18-7z"/>'
I_SAVE = '<path d="M6 3h12v18l-6-5-6 5z"/>'
I_DM = '<path d="M21 3 3 10.5l7 2.5 2.5 7z"/><path d="M10 13l4-4"/>'
I_X = '<path d="M6 6l12 12M18 6 6 18"/>'
I_LOCK = '<rect x="6" y="11" width="12" height="9" rx="1.5"/><path d="M9 11V8a3 3 0 0 1 6 0v3"/>'
STATUS = f'<div class="st"><span>9:41</span><span style="display:flex;gap:5px;align-items:center"><svg width="17" height="11" viewBox="0 0 17 11"><rect x="0" y="7" width="3" height="4" fill="{INK}"/><rect x="4.5" y="5" width="3" height="6" fill="{INK}"/><rect x="9" y="2.5" width="3" height="8.5" fill="{INK}"/><rect x="13.5" y="0" width="3" height="11" fill="{INK}"/></svg><svg width="25" height="12" viewBox="0 0 25 12"><rect x=".5" y=".5" width="21" height="11" rx="3" fill="none" stroke="{INK}"/><rect x="2.5" y="2.5" width="16" height="7" rx="1.5" fill="{INK}"/><rect x="22.5" y="4" width="2" height="4" rx="1" fill="{INK}"/></svg></span></div>'


def ig_feed(ad_src):
    return f"""<div class="dev">{STATUS}
<div class="igbar"><span class="logo">Instagram</span><span style="display:flex;gap:16px">{ico(I_HEART)}{ico(I_DM)}</span></div>
<div class="pf"><img class="av" src="images/logo-mark.webp" alt=""><div style="flex:1"><b>성분돋보기</b><br><span style="font-size:11px">광고</span></div><b style="font-size:16px">⋯</b></div>
<img src="images/{ad_src}" alt="인스타그램 피드의 광고 이미지" style="width:322px;height:322px;object-fit:cover;flex:none">
<div class="cta"><span>더 알아보기</span><span>›</span></div>
<div class="acts"><span>{ico(I_HEART)}{ico(I_COMMENT)}{ico(I_SEND)}</span>{ico(I_SAVE)}</div>
<div class="cap2"><b>성분돋보기</b> 새 크림을 준비하고 있어요. 판매 전 콘셉트를 가장 먼저 공개해요… <span style="color:{SUB}">더 보기</span></div>
</div>"""


def ig_browser(scroll, alt, survey=False, tap=False):
    over = ""
    if tap:
        over = f'<div style="position:absolute;left:5px;right:5px;top:219px;height:42px;border:3px solid {ACC};border-radius:26px"></div>'
    if survey:
        over = ('<div style="position:absolute;inset:0;background:rgba(17,24,39,.45)"></div>'
                '<img src="images/landing-survey.png" alt="설문 카드" style="top:auto;bottom:0;border-radius:16px 16px 0 0">')
    return f"""<div class="dev">{STATUS}
<div class="br">{ico(I_X, 20)}<div class="u"><b>성분돋보기</b><i><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="{SUB}" stroke-width="2.4">{I_LOCK}</svg> seongbun-dotbogi.vercel.app</i></div><b style="font-size:18px">⋯</b></div>
<div class="webv"><img src="images/landing-r1-full.png" alt="{alt}" style="top:-{scroll}px">{over}</div>
</div>"""


S = []

# 1 cover
S.append(f"""<section class="slide">
<div class="a" style="left:112px;top:300px;width:80px;height:6px;background:{ACC}"></div>
<div class="a big" style="left:112px;top:340px">성분돋보기</div>
<div class="a" style="left:112px;top:470px;font-size:34px;font-weight:700">화장품 성분 마케팅 검증 프로젝트</div>
<div class="a" style="left:112px;top:528px;font-size:28px;color:{SUB}">소액 Meta 광고로 성분 이름 문구와 리뷰 언어 문구를 비교한 A/B 테스트</div>
<div class="a" style="left:112px;right:112px;bottom:96px;border-top:1px solid {INK};padding-top:18px;display:flex;justify-content:space-between;font-size:28px">
<b>차원식 · 권지원</b><span style="color:{SUB}">2026년 10월</span></div>
</section>""")

# 2 one-page summary
def sc(k, t, body):
    return f'<div class="col"><span class="cap" style="color:{ACC}">{k}</span><div style="font-size:28px;font-weight:700;line-height:1.45;margin-bottom:16px">{t}</div>{body}</div>'
bar = lambda name, v, color: f'<div style="margin-bottom:16px"><div style="display:flex;justify-content:space-between;font-size:24px"><span>{name}</span><b>{v:.2f}%</b></div><div style="height:20px;background:{SOFTBG};margin-top:6px"><div style="height:20px;width:{v/3.5*100:.0f}%;background:{color}"></div></div></div>'
S.append(plain("한 장 요약", "",
               f"""<div class="W" style="top:262px;display:grid;grid-template-columns:repeat(4,1fr);gap:48px">
{sc("배경", "비슷해지는 성분 광고 문구", ul(['화해 "PDRN" 제품 1,824개', "권고: 광고도 리뷰 언어로", "실험 근거는 없음"]))}
{sc("가설", "리뷰 언어 문구가 더 클릭될 것", f'<div style="display:flex;gap:16px">{img("r2-a.png", "A 성분 이름", 170, 170)}{img("r2-b.png", "B 리뷰 언어", 170, 170)}</div><div style="font-size:24px;margin-top:10px">A 성분 이름 · B 리뷰 언어</div>')}
{sc("방법", "Meta 광고, 한 번에 하나만 바꿈", ul(["1차 그림, 2차 문구", "20~49세 여성, 7일씩, 14만 원", "지표: 링크 클릭률"]))}
{sc("결과", "차이는 유의하지 않음", bar("A 성분 이름", MA, ACC) + bar("B 리뷰 언어", MB, SOFT) + '<div class="n">p = 0.48</div>')}
</div>
<div class="W box" style="top:780px;padding:26px 30px;font-size:34px;font-weight:700">리뷰 언어가 더 클릭된다는 근거 없음<br><span style="font-size:28px;font-weight:400">관심 표시 1대에 광고비 약 23,300원. 3차는 랜딩 첫 화면 비교</span></div>""",
               "출처: Meta 광고 관리자, Amplitude(10/17 조회)"))

# 3 background
grp = lambda label, x, y: f"""<div style="width:808px"><div style="font-size:28px;font-weight:700;margin-bottom:14px">{label}</div><div style="display:flex;gap:24px">{x}{y}</div></div>"""
S.append(page(1, "비슷해지는 성분 광고 문구", "서로 다른 브랜드의 PDRN 크림 광고",
              f"""<div class="W" style="top:262px;display:flex;gap:80px">
{grp("수분 · 광", ph("경쟁 광고 1", "competitor-1.png", 392, 350), ph("경쟁 광고 2", "competitor-2.png", 392, 350))}
{grp("모공", ph("경쟁 광고 3", "competitor-3.png", 392, 350), ph("경쟁 광고 4", "competitor-4.png", 392, 350))}
</div>
<div class="W" style="top:760px;display:grid;grid-template-columns:420px 1fr;gap:56px;align-items:end">
<div><span class="big acc">1,824</span><span style="font-size:34px;font-weight:700;margin-left:8px">개</span><div class="n" style="margin-top:10px">화해 "PDRN" 검색 결과 (10/12)</div></div>
<div class="box" style="font-size:34px;font-weight:700;padding:28px 32px">광고 문구가 달라지면 반응도 달라질까?</div></div>""",
              "출처: 화해 앱 검색(10/12), 각 브랜드 광고"))

# 4 article
S.append(page(1, "참고한 화해 글", "화해 비즈니스 인사이트 · 2026년 4월 13일",
              f"""<div class="L" style="top:262px">{img("hwahae-article.png", "화해 글 첫 화면", 790, 330)}
<div style="margin-top:28px">{img("hwahae-quote.png", "화해 글에서 기능과 경험을 비교한 문단", 1000, 272, "object-fit:contain;padding:24px")}</div></div>
<div class="R" style="top:262px"><table class="txt" style="--p:28px">
<tr><td class="lb">결론</td><td>기능이 아니라 경험에 지갑을 엶</td></tr>
<tr><td class="lb">권고</td><td>광고 문구도 리뷰 언어로</td></tr>
<tr><td class="lb">근거</td><td><b>권고는 있지만 실험이나 데이터는 없음</b></td></tr></table></div>""",
              "출처: 화해 비즈니스 인사이트"))

# 5 hypothesis
adc = lambda src, cap, copy: f'<div><span class="cap">{cap}</span>{img(src, cap, 300, 300)}<div style="font-size:34px;font-weight:700;margin-top:14px;line-height:1.4">{copy}</div></div>'
S.append(page(1, "가설", "페르소나: PDRN 크림 출시를 앞둔 브랜드 마케터 (가정)",
              f"""<div class="W" style="top:262px;display:flex;gap:64px">
{adc("r2-a.png", "A · 성분 이름 (대조군)", '"PDRN 연어크림"')}
{adc("r2-b.png", "B · 리뷰 언어 (실험군)", '"바르면 쫀쫀해지고<br>광이 나는 크림"')}</div>
<div class="W box" style="top:800px;padding:24px 28px;font-size:34px;font-weight:700">리뷰 언어 문구의 링크 클릭률이 성분 이름 문구보다 높을 것이다</div>
<div class="W" style="top:910px;font-size:28px;color:{SUB}">범위: 광고를 보고 누르는 단계까지. 가상 제품이라 구매는 범위 밖</div>""",
              "광고 대상: 20~49세 여성"))

# 6 design
def design_col(head, imgs, rows):
    pics = "".join(f'<div>{img(s, c, 220, 220)}<div style="font-size:24px;font-weight:700;margin-top:10px">{c}</div></div>' for s, c in imgs)
    trs = "".join(f'<tr><td class="lb" style="width:200px">{x}</td><td>{y}</td></tr>' for x, y in rows)
    return f"""<div><div style="font-size:28px;font-weight:700;border-bottom:1px solid {LINE};padding-bottom:10px;margin-bottom:18px">{head}</div>
<div style="display:flex;gap:24px">{pics}</div><table class="txt" style="margin-top:12px;--p:13px">{trs}</table></div>"""
S.append(page(2, "실험 설계", "한 번에 하나만 바꿈",
              f"""<div class="W" style="top:262px;display:grid;grid-template-columns:1fr 1fr;gap:72px">
{design_col("1차 · 10/2 ~ 10/9", [("r1-ingredient.png", "원료 그림"), ("r1-texture.png", "사용감 그림")],
            [("독립변수", "그림"), ("종속변수", "링크 클릭률"), ("통제변수", "광고 글, 대상, 예산, 기간"), ("실험군 · 대조군", "없음 (그림 고르는 단계)"), ("나누는 방식", "세트 하나, Meta가 배분")])}
{design_col("2차 · 10/9 ~ 10/16", [("r2-a.png", "A 성분 이름"), ("r2-b.png", "B 리뷰 언어")],
            [("독립변수", "그림 위 문구"), ("종속변수", "링크 클릭률"), ("통제변수", "그림, 광고 글, 대상, 예산, 기간"), ("실험군 · 대조군", "B 리뷰 언어 · A 성분 이름"), ("나누는 방식", "광고마다 세트, 예산 고정")])}
</div>""",
              "사람은 무작위로 나누지 않음. 보여 줄 사람은 Meta가 고름"))

# 7 channel, target, metric, budget
card = lambda t, items: f'<div class="col"><div style="font-size:34px;font-weight:700;margin-bottom:14px">{t}</div>{ul(items)}</div>'
S.append(page(2, "채널, 대상, 지표, 예산", "",
              f"""<div class="W" style="top:262px;display:grid;grid-template-columns:1fr 1fr;column-gap:72px;row-gap:56px">
{card("Meta 광고", ["성별 · 나이 지정, 광고별 수치 제공", "온드미디어가 없어 유료 광고"])}
{card("20~49세 여성", ["대상을 고정해 문구 차이만 봄", "자동 타겟 끔"])}
{card("링크 클릭률", ["구매는 출시 전이라 잴 수 없음", "광고를 보고 누르는 반응을 봄"])}
{card("7일씩, 회차당 7만 원", ["평일과 주말을 담는 최소 기간", "광고당 노출 약 7천 회. 1.0% 대 1.5% 차이를 볼 수 있는 규모"])}
</div>""",
              "실제 지출: 1차 69,937원, 2차 69,787원"))

# 8 landing and events
phones = [("인스타그램 광고", ig_feed("r1-texture.png")),
          ("누르면 랜딩", ig_browser(0, "랜딩 첫 화면")),
          ("관심 버튼", ig_browser(240, "관심 버튼까지 내린 화면", tap=True)),
          ("설문 3문항", ig_browser(240, "관심 버튼을 누른 뒤 뜨는 설문", survey=True))]
cells = []
for i, (t, dev) in enumerate(phones):
    cells.append(f'<div><div style="font-size:28px;font-weight:700;margin-bottom:14px"><span class="acc">{i+1}</span>&nbsp;&nbsp;{t}</div>{dev}</div>')
    if i < 3:
        cells.append('<div class="arrow" style="align-self:center;margin-top:50px">→</div>')
S.append(page(2, "랜딩과 이벤트", "",
              f"""<div class="W" style="top:250px;display:flex;justify-content:space-between">{''.join(cells)}</div>
<div class="fi" style="top:900px"><div style="padding-top:10px"><span style="display:inline;margin-right:16px">설계</span>광고와 같은 사진. 제품 이름과 가격 없음</div>
<div style="padding-top:10px"><span style="display:inline;margin-right:16px">기록</span>이벤트 8개. 핵심은 관심 버튼 클릭</div></div>""",
              "이벤트 정의: docs/taxonomy/events.csv. 코드와 어긋나면 자동 검사가 막음"))

# 9 UTM
flow = [("Meta 광고 관리자", "img_texture_text_review_r2_v1"),
        ("광고 링크", "utm_content=<br>img_texture_text_review_r2_v1"),
        ("랜딩 기록 (Amplitude)", "utm_content=<br>img_texture_text_review_r2_v1")]
fc = []
for i, (t, code) in enumerate(flow):
    fc.append(f'<div class="col" style="width:500px"><div style="font-size:28px;font-weight:700;margin-bottom:14px"><span class="acc">{i+1}</span>&nbsp;&nbsp;{t}</div><div class="code">{code}</div></div>')
    if i < 2:
        fc.append('<div class="arrow" style="align-self:center">→</div>')
parts = [("img_texture", "그림: 사용감"), ("text_review", "글: 리뷰 언어"), ("r2", "2차"), ("v1", "첫 버전")]
pc = '<span class="arrow">_</span>'.join(f'<div style="text-align:center"><div class="code" style="font-size:34px">{x}</div><div style="font-size:24px;color:{SUB};margin-top:10px">{y}</div></div>' for x, y in parts)
S.append(page(2, "광고 이름이 곧 UTM", "",
              f"""<div class="W" style="top:262px;display:flex;justify-content:space-between">{''.join(fc)}</div>
<div class="W" style="top:560px"><div class="h3">이름 읽는 법</div><div style="display:flex;gap:20px;align-items:flex-start">{pc}</div></div>""",
              "규칙: ads/README.md"))

# 10 round 1 (+ what changed in round 2)
S.append(page(3, "1차 결과", "세트 하나에 광고 둘, 배분은 Meta",
              f"""<div class="L" style="top:262px"><div class="h3">하루 노출 수</div><div class="leg"><i></i>원료 그림<i class="b"></i>사용감 그림</div>{R1_CHART}</div>
<div class="R" style="top:262px"><table><tr><th></th>{th("r1-ingredient.png", "원료 그림")}{th("r1-texture.png", "사용감 그림")}</tr>
<tr class="k"><td>노출</td><td>7%</td><td>93%</td></tr>
<tr><td>링크 클릭률</td><td>{pct(ri["clicks"], ri["impressions"])}</td><td>{pct(rt["clicks"], rt["impressions"])}</td></tr>
<tr><td>함께 나간 이틀</td><td>{pct(*sd["ingredient"])}</td><td>{pct(*sd["texture"])}</td></tr>
<tr><td>클릭당 비용</td><td>{round(ri["spend"]/ri["clicks"])}원</td><td>{round(rt["spend"]/rt["clicks"])}원</td></tr></table>
<div class="box" style="margin-top:24px;padding:18px 24px"><b>2차는 광고마다 세트를 따로, 예산 고정</b><br>노출 7% 대 93% → 51.2% 대 48.8%</div></div>
<div class="fi" style="top:830px;right:auto;width:1000px;gap:40px"><div><span>사실</span>원료 그림은 10/5부터 거의 안 나감</div>
<div><span>해석</span>두 그림의 차이는 확정 못 함. 사실상 Meta가 고름</div></div>""",
              f"출처: Meta 광고 관리자. 노출 {fnum(ri['impressions'])} 대 {fnum(rt['impressions'])}. 연휴 10/3~10/5, 공휴일 10/9"))

# 11 round 2 and hypothesis
S.append(page(3, "2차 결과와 가설 검증", "같은 그림 위 문구만 다르게 · 10/9 ~ 10/16",
              f"""<div class="L" style="top:262px"><div class="h3">일자별 링크 클릭률</div><div class="leg"><i></i>A 성분 이름<i class="b"></i>B 리뷰 언어</div>{R2_CHART}</div>
<div class="R" style="top:262px"><table><tr><th style="width:150px;white-space:nowrap">7일 누적</th>{th2("r2-a.png", "A 성분 이름", "PDRN 연어크림")}{th2("r2-b.png", "B 리뷰 언어", "바르면 쫀쫀해지고<br>광이 나는 크림")}</tr>
<tr><td>노출</td><td>{fnum(a["impressions"])}</td><td>{fnum(b["impressions"])}</td></tr>
<tr class="k"><td style="font-size:28px;white-space:nowrap">링크 클릭률</td><td>{MA:.2f}%</td><td>{MB:.2f}%</td></tr>
<tr><td>클릭당 비용</td><td>{round(a["spend"]/a["clicks"])}원</td><td>{round(b["spend"]/b["clicks"])}원</td></tr></table>
<div class="box" style="margin-top:20px;padding:14px 24px"><b style="font-size:34px">가설은 지지되지 않음</b> &nbsp;z = 0.71, p = 0.48</div></div>
<div class="fi" style="top:830px;right:auto;width:1000px;gap:40px"><div><span>사실</span>노출 51.2% 대 48.8%. 앞선 쪽은 8일 중 4일씩</div>
<div><span>해석</span>리뷰 언어가 더 클릭된다는 근거 없음</div></div>""",
              "출처: Meta 광고 관리자(10/17 조회). 두 비율 z검정(양측). 95% 신뢰구간 −0.36 ~ 0.77%p"))

# 12 after the click
fun = [("노출", a["impressions"] + b["impressions"]), ("링크 클릭", a["clicks"] + b["clicks"]), ("랜딩 도착", l2["arrived"]), ("관심 버튼", l2["interest"])]
fcells = []
for i, (lab, v) in enumerate(fun):
    if i:
        rate = 100 * v / fun[i - 1][1]
        fcells.append(f'<div style="text-align:center;align-self:center;padding-bottom:6px"><div class="arrow" style="font-size:34px">→</div><div style="font-size:34px;font-weight:700;color:{ACC if i == 3 else SUB}">{rate:.1f}%</div></div>')
    fcells.append(f'<div><span class="cap">{lab}</span><div style="font-size:50px;font-weight:800;line-height:1.1;{"color:" + ACC if i == 3 else ""}">{fnum(v)}</div></div>')
S.append(page(3, "클릭 뒤", "2차 광고가 어디까지 이어졌나",
              f"""<div class="W" style="top:262px;display:flex;justify-content:space-between;align-items:flex-end;padding-bottom:28px;border-bottom:1px solid {LINE}">{''.join(fcells)}</div>
<div class="L" style="top:540px;width:900px"><div class="h3">관심 버튼을 누른 기기</div>
<div style="display:flex;align-items:center;gap:40px;margin-top:16px">
<div><div style="font-size:50px;font-weight:800;color:{SUB}">{100*l1["interest"]/l1["arrived"]:.1f}%</div><div class="n" style="margin-top:6px">1차 · {l1["arrived"]}대 중 {l1["interest"]}대</div></div>
<div class="arrow">→</div>
<div><div style="font-size:50px;font-weight:800">{100*l2["interest"]/l2["arrived"]:.1f}%</div><div class="n" style="margin-top:6px">2차 · 랜딩 고친 뒤 · {l2["arrived"]}대 중 {l2["interest"]}대</div></div></div>
<div style="font-size:28px;color:{SUB};margin-top:24px">버튼은 99%가 화면에서 봄. 안 누르는 이유는 알 수 없음</div></div>
<div class="R box" style="top:540px;padding:26px 30px"><b style="font-size:34px">관심 표시 1대에 광고비 약 23,300원</b><br>1차 23,312원, 2차 23,262원<br>문구보다 이 비용을 낮추는 쪽이 먼저</div>""",
              "출처: 클릭은 Meta 광고 관리자, 도착과 버튼은 Amplitude(10/17 조회). 광고 링크로 온 기기만. 2차 랜딩은 첫 화면 문구와 버튼을 고친 것"))

# 13 limits
lim = [("차이가 없다", "신뢰구간 −0.36 ~ 0.77%p. 리뷰 언어가 0.36%p 더 높을 가능성도 남음. 작은 차이를 잡을 규모가 아니었음"),
       ("리뷰 언어는 안 통한다", "문구를 하나씩만 비교. B는 두 줄이라 소재 인상도 다름. 이 두 문장에 대한 결과"),
       ("구매도 같다", "잰 것은 클릭. 화해 글이 말한 \"지갑\"은 검증하지 않음"),
       ("랜딩이 문제다", "관심 3대가 랜딩 탓인지 판매하지 않는 가상 제품 탓인지 못 가림. 3차는 그래서 해결책이 아니라 가설임"),
       ("20~49세 여성 전체", "노출의 3분의 2가 20~24세, 거의 전부 릴스")]
trs = "".join(f'<tr><td class="lb" style="width:380px;font-size:34px;color:{SUB}">"{g}"</td><td>{x}</td></tr>' for g, x in lim)
S.append(page(4, "한계", "이 결과로 말할 수 없는 것",
              f'<div class="W" style="top:262px"><table class="txt" style="--p:26px">{trs}</table></div>',
              "신뢰구간은 두 비율 차이의 95% 구간(A − B). 전체 목록: README 5절"))

# 14 conclusion and proposal
wr = [("결과", "리뷰 언어가 더 클릭된다는 근거 없음", "2.97% 대 2.77%, p = 0.48"),
      ("결과", "병목은 클릭 뒤. 랜딩을 고쳐도 관심 버튼은 한 자리 수", "365대 중 3대 · 1대에 약 23,300원"),
      ("권고", "문구를 더 고르는 데 쓰지 말고 클릭 뒤에 투자", "이 규모에서 문구 차이는 안 보임"),
      ("제안", "3차: 광고는 그대로, 랜딩 첫 화면만 바꿔 비교", "관심 버튼 클릭률로 판정")]
rows = "".join(f'<div style="display:grid;grid-template-columns:160px 1fr 460px;align-items:baseline;padding:22px 0;border-bottom:1px solid {LINE}"><span style="font-size:24px;font-weight:700;color:{ACC if k in ("권고", "제안") else SUB}">{k}</span><span style="font-size:34px;font-weight:800">{t}</span><span style="font-size:28px;color:{SUB};text-align:right">{d}</span></div>' for k, t, d in wr)
S.append(page(4, "결론과 제안", "",
              f"""<div class="W" style="top:262px">{rows}</div>
<div class="W" style="top:840px;display:flex;justify-content:space-between;align-items:flex-end;border-top:1px solid {INK};padding-top:24px">
<div style="font-size:50px;font-weight:800">감사합니다</div>
<table class="txt" style="width:auto;--p:8px"><tr><td class="lb" style="border:none">리포트</td><td style="border:none">seongbun-dotbogi.vercel.app/report</td></tr>
<tr><td class="lb" style="border:none">저장소</td><td style="border:none">github.com/Chawonsik/seongbun-dotbogi</td></tr></table></div>""",
              "2차는 연장하지 않고 정한 예산 안에서 끝냄. 출처: Meta 광고 관리자, Amplitude(10/17 조회)"))

assert len(S) == TOTAL, len(S)
html = f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>성분돋보기 최종 발표</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800&display=swap">
<style>{CSS}</style></head><body>
{chr(10).join(S)}
<script>function fit(){{document.documentElement.style.setProperty('--z',Math.min(1,(innerWidth-32)/1920))}}fit();addEventListener('resize',fit)</script>
</body></html>"""
OUT.write_text(html, encoding="utf-8")
print("wrote", OUT, len(html))
