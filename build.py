"""楽天APIから商品を取得し「1回あたり単価」ランキングページを生成する。

環境変数（ローカルは .env、GitHub Actions は Secrets）:
  RAKUTEN_APP_ID / RAKUTEN_ACCESS_KEY / RAKUTEN_AFFILIATE_ID / SITE_URL
.env が無い場合は sample_items.json を使って見た目だけ確認できる。
"""
import html
import json
import os
import re
import time
import urllib.parse
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
JST = timezone(timedelta(hours=9))
API = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260701"

# ページごとの設定。unit=表示単位、words=数量の後ろに付く語
CATEGORIES = [
    {
        "slug": "dishwasher-tablet",
        "title": "食洗機用洗剤タブレット 1回あたり単価ランキング",
        "keyword": "食洗機 洗剤 タブレット",
        "unit": "回",
        "words": ["個入り", "個入", "個", "回分", "回", "錠", "粒", "P", "包"],
        "min_reviews": 10,
        "ng": ["クリーナー", "工事", "本体", "分岐水栓"],
        "brands": {"フィニッシュ": ["finish", "フィニッシュ", "フィニッフシュ"], "キュキュット": ["キュキュット"],
                   "ジョイ": ["ジョイ", "joy"], "ミーレ": ["miele", "ミーレ"], "SAMKYO": ["samkyo"]},
        "lines": {"フィニッシュ": [("オールインワン", r"オールインワン|パワーボール"), ("ウルトラ", r"ウルトラ|ジェル"),
                                  ("パワーキューブL", r"キューブ\s*l(?![a-z])|(?<![a-z])l\s*[(（]|lサイズ"),
                                  ("パワーキューブ", r".")]},
    },
    {
        "slug": "garbage-bag-45l",
        "title": "ゴミ袋 45L 1枚あたり単価ランキング",
        "keyword": "ゴミ袋 45L 枚入",
        "unit": "枚", "base": "枚",
        "words": ["枚入り", "枚入", "枚"],
        "min_reviews": 10, "range": (10, 3000),
        "ng": ["ホルダー", "スタンド", "ゴミ箱", "ダストボックス"],
    },
    {
        "slug": "pet-sheet",
        "title": "ペットシーツ レギュラー 1枚あたり単価ランキング",
        "keyword": "ペットシーツ レギュラー",
        "unit": "枚", "base": "枚",
        "words": ["枚入り", "枚入", "枚"],
        "min_reviews": 10, "range": (20, 3000),
        "ng": ["トレー", "トレイ", "ケース", "ワイド", "ハーフ"],
    },
    {
        "slug": "mask",
        "title": "不織布マスク 1枚あたり単価ランキング",
        "keyword": "不織布マスク",
        "unit": "枚", "base": "枚",
        "words": ["枚入り", "枚入", "枚"],
        "min_reviews": 10, "range": (20, 3000),
        "ng": ["ケース", "ホルダー", "フィルター"],
    },
    {
        "slug": "sonicare-brush-head",
        "title": "ソニッケアー 替えブラシ（互換含む）1本あたり単価ランキング",
        "keyword": "ソニッケアー 替えブラシ",
        "unit": "本", "base": "本",
        "words": ["本入り", "本入", "本組", "本", "個入り", "個入", "個"],
        "min_reviews": 10, "range": (2, 100), "outlier": 0.15,
        "ng": ["本体", "充電器", "ケース", "スタンド", "ホルダー", "付き", "モード", "ブラウン", "オーラル"],
    },
    {
        "slug": "oralb-brush-head",
        "title": "ブラウン オーラルB 替えブラシ（互換含む）1本あたり単価ランキング",
        "keyword": "ブラウン オーラルB 替えブラシ",
        "unit": "本", "base": "本",
        "words": ["本入り", "本入", "本組", "本", "個入り", "個入", "個"],
        "min_reviews": 10, "range": (2, 100), "outlier": 0.15,
        "ng": ["本体", "充電器", "ケース", "スタンド", "ホルダー", "付き", "モード", "ソニッケアー", "フィリップス"],
    },
    {
        "slug": "coffee-beans",
        "title": "コーヒー豆 100gあたり単価ランキング",
        "keyword": "コーヒー豆",
        "unit": "100g", "base": "g", "per": 100, "per_text": "100gあたり",
        "words": {"kg": 1000, "g": 1},
        "min_reviews": 10, "range": (200, 10000),
        "ng": ["スケール", "はかり", "ドリップバッグ", "ドリップ バッグ", "インスタント", "ミル", "キャニスター", "カプセル"],
    },
]


def load_env():
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def fetch(keyword, pages=3):
    items = []
    for page in range(1, pages + 1):
        q = urllib.parse.urlencode({
            "applicationId": os.environ["RAKUTEN_APP_ID"],
            "accessKey": os.environ["RAKUTEN_ACCESS_KEY"],
            "affiliateId": os.environ.get("RAKUTEN_AFFILIATE_ID", ""),
            "keyword": keyword, "hits": 30, "page": page,
            "sort": "-reviewCount", "format": "json", "formatVersion": 2,
        })
        req = urllib.request.Request(f"{API}?{q}", headers={
            "Referer": os.environ.get("SITE_URL", ""),
            "Origin": os.environ.get("SITE_URL", "").rstrip("/"),
            "User-Agent": "Mozilla/5.0",
        })
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.load(r)
        except urllib.error.HTTPError as e:
            # GitHub Actions の注釈に出してログイン無しで原因を読めるようにする
            body = " ".join(e.read()[:300].decode("utf-8", "replace").split())
            site = os.environ.get("SITE_URL", "")
            print(f"::error::楽天API {e.code}: {body} / SITE_URL={len(site)}文字 / ID={len(os.environ.get('RAKUTEN_APP_ID',''))}文字")
            raise SystemExit(1)
        items += data.get("Items", [])
        time.sleep(1.1)  # 1秒1リクエスト制限
    return items


ZEN = str.maketrans("０１２３４５６７８９×Ｘｘ", "0123456789xxx")


def parse_count(name, words, lo=5, hi=3000):
    """商品名から総数量を推定。例: '60個入×3袋' -> 180、'500g×2袋' -> 1000。判定できなければ None
    words は語のリスト、または {語: 倍率}（例 {"kg": 1000, "g": 1}）"""
    if isinstance(words, list):
        words = {w: 1 for w in words}
    s = name.translate(ZEN).replace(",", "")
    # 「1袋～3袋 選べる」のようなバリエーション商品は価格と数量が対応しないので除外
    if re.search(r"選べる|\d\s*[~～〜]\s*\d", s):
        return None
    w = "|".join(map(re.escape, sorted(words, key=len, reverse=True)))
    # 「3個セット」のセット数を拾わないよう、直後がセットの数字は除く。一番大きい量を内容量とみなす
    ms = [(float(m.group(1)) * words[m.group(2)], m)
          for m in re.finditer(rf"(\d{{1,4}}(?:\.\d{{1,2}})?)\s*({w})(?!\s*セット)", s)]
    if not ms:
        return None
    # セット数の候補: 「×3」「/箱×3」「3袋セット」「【3個セット】」
    ks_set = [int(x) for x in re.findall(r"(\d{1,2})\s*(?:袋|箱|個|本|パック|冊)\s*セット", s)]
    ks = ks_set + [int(x) for x in re.findall(r"[x*]\s*(\d{1,2})(?!\d|\.\d|\s*(?:g|kg|ml|L|枚|個|本|回))", s)]
    ms = [t for t in ms if t[0] > 1] or ms  # 「1個13g」の1個などは内容量ではない
    vals = sorted({v for v, _ in ms})
    if len(vals) >= 2:
        # 量が複数ある: 「500g×4袋 2kg」のように 大=小×セット数 なら大を採用、
        # 「88枚 66枚 56枚」のようなサイズ違いの羅列は価格がどれのものか分からないので除外
        lo_v, hi_v = vals[0], vals[-1]
        if len(vals) == 2 and any(abs(lo_v * k - hi_v) < 1e-6 for k in ks):
            n = hi_v
        else:
            return None
    else:
        n, m = ms[0]
        k = re.match(r"\s*(?:\S{0,3}?)[x*]\s*(\d{1,2})(?!\d|\.\d|\s*(?:g|kg|ml|L))", s[m.end():m.end() + 15])
        k = int(k.group(1)) if k else next(iter(ks_set), None)
        if k:
            n *= k
        elif re.search(r"(?<![x*\d])\s*\d\s*(?:袋|箱|冊|パック)(?!\s*(?:入|セット))", s):
            return None  # 「112枚 4袋」のように袋数の掛け方が読めない
    return n if lo <= n <= hi else None


NOISE = r"送料無料|最安値|挑戦|楽天|ランキング|\d位|入賞|受賞|獲得|クーポン|ポイント|限定|お試し|価格|大容量|お得|まとめ買い|"         r"セット|業務用|公式|正規品|純正品|純正|互換品|互換|対応|高評価|レビュー|特典|送料込み|メール便|新色|本日|先着"


COMMON = ["電動歯ブラシ", "歯ブラシ", "替えブラシ", "替ブラシ", "ブラシヘッド", "ブラシ", "ヘッド", "食洗機用", "食洗機", "食器洗い機用",
          "食器洗い乾燥機用", "食器洗い機", "洗剤", "タブレット", "ペットシーツ", "ペットシート", "トイレシート", "シーツ", "レギュラー",
          "ゴミ袋", "ごみ袋", "ポリ袋", "半透明", "リットル", "マスク", "不織布", "立体", "コーヒー豆", "コーヒー", "珈琲豆", "珈琲",
          "フィリップス", "ソニッケアー", "ソニッケア", "ブラウン", "オーラルb", "oralb", "philips", "sonicare", "braun"]


def signature(name):
    """商品名から宣伝文句・数量・ジャンル共通語を除いた (2-gram集合, 型番集合)"""
    s = name.translate(ZEN).lower()
    s = re.sub(r"[【\[［《〈].*?[】\]］》〉]", " ", s)  # 墨付き括弧内はほぼ宣伝
    codes = set(re.findall(r"[a-z]{1,4}-?\d{2,5}[a-z]?", s)) - {"45l"}
    s = re.sub(NOISE, " ", s)
    for w in COMMON:
        s = s.replace(w, " ")
    s = re.sub(r"[\d.]+\s*(?:個入り|個入|個|回分|回|錠|粒|枚入り|枚入|枚|本入り|本入|本組|本|袋|箱|冊|kg|g|ml|l|p|パック)?", " ", s)
    s = re.sub(r"[^\w]|_", "", s)
    return {s[i:i + 2] for i in range(len(s) - 1)}, codes


def similar(a, b, th=0.35):
    """型番が両方にあって食い違えば別商品。それ以外は2-gramのJaccard係数で判定"""
    (ga, ca), (gb, cb) = a, b
    if ca and cb:
        return bool(ca & cb)  # 型番が両方にあれば型番だけで判定（HX6014互換どうしは同じ扱い）
    if not ga or not gb:
        return False
    return len(ga & gb) / len(ga | gb) >= th


def product_line(name, cat):
    """カテゴリ設定の lines（ブランド→[(シリーズ名, 正規表現)]）で決まるシリーズ名。該当なしは None"""
    low = name.translate(ZEN).lower()
    for brand, aliases in cat.get("brands", {}).items():
        if any(a in low for a in aliases):
            for label, pat in cat.get("lines", {}).get(brand, []):
                if re.search(pat, low):
                    return f"{brand} {label}"
            return brand
    return None


def rank(items, cat):
    rows = []
    for it in items:
        if any(w in it["itemName"] for w in cat.get("ng", [])):
            continue
        n = parse_count(it["itemName"], cat["words"], *cat.get("range", (5, 3000)))
        if not n or it.get("reviewCount", 0) < cat["min_reviews"]:
            continue
        price = it["itemPrice"]
        rows.append({
            "name": it["itemName"], "shop": it.get("shopName", ""),
            "price": price, "count": n, "unit_price": price / (n / cat.get("per", 1)),
            "free_ship": it.get("postageFlag") == 0,
            "reviews": it.get("reviewCount", 0), "rating": it.get("reviewAverage", 0),
            "url": it.get("affiliateUrl") or it.get("itemUrl"),
            "img": (it.get("mediumImageUrls") or [""])[0],
        })
    rows.sort(key=lambda r: r["unit_price"])
    # 相場の35%未満（純正と互換が混ざるジャンルは15%未満）は数量の読み違いの可能性が高いので載せない
    if len(rows) >= 5:
        med = rows[len(rows) // 2]["unit_price"]
        rows = [r for r in rows if r["unit_price"] >= med * cat.get("outlier", 0.35)]
    # 同じ商品（ショップ違い・袋数違い）は1行にまとめ、1回あたり最安の出品だけを載せる
    groups = []
    for r in rows:  # rows は単価の安い順なので、各グループの先頭が最安
        sig = product_line(r["name"], cat) or signature(r["name"])
        for g in groups:
            if sig == g["sig"] or (not isinstance(sig, str) and not isinstance(g["sig"], str) and similar(sig, g["sig"])):
                g["others"] += 1
                break
        else:
            groups.append({"sig": sig, "row": r, "others": 0})
    out = []
    for g in groups[:30]:
        g["row"]["others"] = g["others"]
        out.append(g["row"])
    return out


def render(cat, rows, updated):
    e = html.escape
    per_text = cat.get('per_text', f"1{cat['unit']}あたり")
    trs = "".join(f"""
<tr><td class=n>{i}</td>
<td class=p><a href="{e(r['url'])}" rel="sponsored noopener" target=_blank>
<img src="{e(r['img'])}" alt="" loading=lazy><span>{e(r['name'][:70])}</span></a>
<small>{e(r['shop'])}{' ・送料無料' if r['free_ship'] else ' ・送料別'}{f" ・同じ商品の出品ほか{r['others']}件（ここが最安）" if r.get('others') else ''}</small></td>
<td class=u><b>{r['unit_price']:.1f}円</b><small>/{cat['unit']}</small></td>
<td class=d>{r['price']:,}円<br><small>{r['count']:,.0f}{cat.get('base', cat['unit'] + '分')}</small></td>
<td class=d>★{r['rating']:.2f}<br><small>{r['reviews']:,}件</small></td></tr>"""
                  for i, r in enumerate(rows, 1))
    return f"""<!doctype html><html lang=ja><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>{e(cat['title'])}</title>
<meta name=description content="{e(cat['keyword'])}を楽天の価格と内容量から{per_text}の値段に換算して毎日自動で比較。">
<style>
:root{{--bg:#fff;--fg:#1d1d1f;--mut:#6e6e73;--line:#e5e5ea;--acc:#bf0000}}
@media(prefers-color-scheme:dark){{:root{{--bg:#111;--fg:#f2f2f7;--mut:#a1a1a6;--line:#333;--acc:#ff5a5a}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.6 system-ui,sans-serif}}
main{{max-width:880px;margin:auto;padding:16px}}
h1{{font-size:1.35rem;margin:.2em 0}} .pr{{color:var(--mut);font-size:.8rem}}
table{{width:100%;border-collapse:collapse}} td{{border-bottom:1px solid var(--line);padding:8px 4px;vertical-align:middle}}
.n{{color:var(--mut);width:2em;text-align:center}} .u b{{color:var(--acc);font-size:1.1rem}}
.p a{{display:flex;gap:8px;align-items:center;color:inherit;text-decoration:none}}
.p img{{width:56px;height:56px;object-fit:contain;flex:none}} small{{display:block;color:var(--mut);font-size:.75rem}}
.d{{text-align:right;white-space:nowrap;font-size:.85rem}}
@media(max-width:560px){{.d:last-child{{display:none}} .p span{{font-size:.85rem}}}}
</style></head><body><main>
<p class=pr>PR：このページは楽天アフィリエイトを利用しています</p>
<h1>{e(cat['title'])}</h1>
<p>楽天市場の商品を「価格 ÷ 内容量」で{per_text}に換算し、安い順に並べています。同じ商品はショップ違い・袋数違いをまとめ、1回あたり最安の出品だけを載せています。毎日自動更新（最終更新 {updated}）。価格は更新時点のもので、送料別の商品は送料を含みません。</p>
<table>{trs}</table>
<p class=pr>内容量は商品名から自動で読み取っています。セット数の読み違いがある場合があるので、購入前に商品ページで確認してください。</p>
</main></body></html>"""


def main():
    load_env()
    live = bool(os.environ.get("RAKUTEN_APP_ID"))
    OUT.mkdir(exist_ok=True)
    updated = datetime.now(JST).strftime("%Y-%m-%d %H:%M")
    for cat in CATEGORIES:
        if live:
            items = fetch(cat["keyword"])
        else:
            items = json.loads((ROOT / "sample_items.json").read_text(encoding="utf-8"))
        rows = rank(items, cat)
        (OUT / f"{cat['slug']}.html").write_text(render(cat, rows, updated), encoding="utf-8")
        print(f"{cat['slug']}: 取得{len(items)}件 → 掲載{len(rows)}件 ({'本番' if live else 'サンプル'})")
    links = "".join(f'<li><a href="{c["slug"]}.html">{html.escape(c["title"])}</a></li>' for c in CATEGORIES)
    (OUT / "index.html").write_text(f"""<!doctype html><html lang=ja><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>1回いくら</title>
<meta name="google-site-verification" content="A-JyA2Us3KYpkTLgjEMxZSKUwAAWLqE7rWFsJdlSn9o">
<meta name=description content="日用品・消耗品を楽天の価格と内容量から1回あたりの値段に換算して毎日比較。">
<style>body{{margin:0;font:16px/1.7 system-ui,sans-serif;background:#fff;color:#1d1d1f}}
@media(prefers-color-scheme:dark){{body{{background:#111;color:#f2f2f7}}a{{color:#8ab4ff}}}}
main{{max-width:720px;margin:auto;padding:16px}}</style></head><body><main>
<p style="font-size:.8rem;opacity:.7">PR：このサイトは楽天アフィリエイトを利用しています</p>
<h1>1回いくら</h1><p>日用品を「1回あたりの値段」で比べるサイトです。価格は毎日自動で更新しています（最終更新 {updated}）。</p>
<ul>{links}</ul></main></body></html>""", encoding="utf-8")
    # 検索エンジン向けのサイトマップ
    site = os.environ.get("SITE_URL", "https://ikkai-ikura.github.io/")
    day = updated[:10]
    urls = [site] + [f"{site}{c['slug']}.html" for c in CATEGORIES]
    xml = "".join(f"<url><loc>{u}</loc><lastmod>{day}</lastmod></url>" for u in urls)
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>' + chr(10)
        + f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{xml}</urlset>' + chr(10), encoding="utf-8")
    (OUT / "robots.txt").write_text(chr(10).join(["User-agent: *", "Allow: /", f"Sitemap: {site}sitemap.xml", ""]),
                                    encoding="utf-8")


if __name__ == "__main__":
    main()
