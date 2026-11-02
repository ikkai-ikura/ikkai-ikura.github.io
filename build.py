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
            print(f"::error::楽天API {e.code}: {e.read()[:300].decode('utf-8', 'replace')}")
            raise SystemExit(1)
        items += data.get("Items", [])
        time.sleep(1.1)  # 1秒1リクエスト制限
    return items


ZEN = str.maketrans("０１２３４５６７８９×Ｘｘ", "0123456789xxx")


def parse_count(name, words):
    """商品名から総数量を推定。例: '60個入×3袋' -> 180。判定できなければ None"""
    s = name.translate(ZEN).replace(",", "")
    # 「1袋～3袋 選べる」のようなバリエーション商品は価格と数量が対応しないので除外
    if re.search(r"選べる|\d\s*[~～〜]\s*\d", s):
        return None
    w = "|".join(map(re.escape, sorted(words, key=len, reverse=True)))
    # 「3個セット」のセット数を拾わないよう、直後がセットの数字は除く。一番大きい数を内容量とみなす
    ms = [m for m in re.finditer(rf"(\d{{1,4}})\s*(?:{w})(?!\s*セット)", s)]
    if not ms:
        return None
    m = max(ms, key=lambda m: int(m.group(1)))
    n = int(m.group(1))
    # 直後の「×3」「/箱×3」、または「3袋セット」「【3個セット】」を掛ける
    k = re.match(r"\s*(?:\S{0,3}?)[x*]\s*(\d{1,2})", s[m.end():m.end() + 15])
    if not k:
        k = re.search(r"(\d{1,2})\s*(?:袋|箱|個|本|パック)\s*セット", s)
    if k and int(k.group(1)) < n:
        n *= int(k.group(1))
    return n if 5 <= n <= 3000 else None


def rank(items, cat):
    rows = []
    for it in items:
        if any(w in it["itemName"] for w in cat.get("ng", [])):
            continue
        n = parse_count(it["itemName"], cat["words"])
        if not n or it.get("reviewCount", 0) < cat["min_reviews"]:
            continue
        price = it["itemPrice"]
        rows.append({
            "name": it["itemName"], "shop": it.get("shopName", ""),
            "price": price, "count": n, "unit_price": price / n,
            "free_ship": it.get("postageFlag") == 0,
            "reviews": it.get("reviewCount", 0), "rating": it.get("reviewAverage", 0),
            "url": it.get("affiliateUrl") or it.get("itemUrl"),
            "img": (it.get("mediumImageUrls") or [""])[0],
        })
    rows.sort(key=lambda r: r["unit_price"])
    # 同じ商品の重複（ショップ違い）は最安だけ残す
    # キーは「ブランド＋1袋の内容量」。ブランド不明なら商品名の先頭で代用
    seen, out = set(), []
    for r in rows:
        low = r["name"].lower()
        brand = next((b for b, aliases in cat.get("brands", {}).items()
                      if any(a in low for a in aliases)), None)
        key = (brand, r["count"]) if brand else re.sub(r"\W", "", r["name"])[:25]
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out[:30]


def render(cat, rows, updated):
    e = html.escape
    trs = "".join(f"""
<tr><td class=n>{i}</td>
<td class=p><a href="{e(r['url'])}" rel="sponsored noopener" target=_blank>
<img src="{e(r['img'])}" alt="" loading=lazy><span>{e(r['name'][:70])}</span></a>
<small>{e(r['shop'])}{' ・送料無料' if r['free_ship'] else ' ・送料別'}</small></td>
<td class=u><b>{r['unit_price']:.1f}円</b><small>/{cat['unit']}</small></td>
<td class=d>{r['price']:,}円<br><small>{r['count']}{cat['unit']}分</small></td>
<td class=d>★{r['rating']:.2f}<br><small>{r['reviews']:,}件</small></td></tr>"""
                  for i, r in enumerate(rows, 1))
    return f"""<!doctype html><html lang=ja><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>{e(cat['title'])}</title>
<meta name=description content="{e(cat['keyword'])}を楽天の価格と内容量から1{cat['unit']}あたりの値段に換算して毎日自動で比較。">
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
<p>楽天市場の商品を「価格 ÷ 内容量」で1{cat['unit']}あたりに換算し、安い順に並べています。毎日自動更新（最終更新 {updated}）。価格は更新時点のもので、送料別の商品は送料を含みません。</p>
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
<meta name=description content="日用品・消耗品を楽天の価格と内容量から1回あたりの値段に換算して毎日比較。">
<style>body{{margin:0;font:16px/1.7 system-ui,sans-serif;background:#fff;color:#1d1d1f}}
@media(prefers-color-scheme:dark){{body{{background:#111;color:#f2f2f7}}a{{color:#8ab4ff}}}}
main{{max-width:720px;margin:auto;padding:16px}}</style></head><body><main>
<p style="font-size:.8rem;opacity:.7">PR：このサイトは楽天アフィリエイトを利用しています</p>
<h1>1回いくら</h1><p>日用品を「1回あたりの値段」で比べるサイトです。価格は毎日自動で更新しています（最終更新 {updated}）。</p>
<ul>{links}</ul></main></body></html>""", encoding="utf-8")


if __name__ == "__main__":
    main()
