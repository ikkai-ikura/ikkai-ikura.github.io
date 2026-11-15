"""特集ページ（季節・イベントごとのまとめ）。各ジャンルの単価上位3件を summary.json の top3 から並べる。
months に今月が入っている特集をトップで先に出す。ジャンルの中身は毎朝の更新でそのまま入れ替わる。"""
import html
import json

FEATURES = [
    {
        "slug": "tokushu-osouji",
        "short": "大掃除",
        "title": "大掃除の洗剤・消耗品 まとめ買い最安ガイド",
        "desc": "オキシクリーン・除菌シート・キッチンペーパー・ゴミ袋など、大掃除で使う消耗品を楽天市場の1回あたり単価で比較。毎朝更新の最安上位3件をまとめました。",
        "lead": "大掃除はオキシクリーンや除菌シート、ゴミ袋をたくさん使います。量が多いぶん、1回あたりの単価で選ぶと差がはっきり出ます。毎朝6時に、楽天市場の最安上位3件へ入れ替わります。",
        "months": [11, 12],
        "items": [
            ("oxygen-bleach", "換気扇・五徳のつけ置き、浴室の小物に。お湯で溶かすと効きやすい"),
            ("disinfect-wipes", "ドアノブ・スイッチ・冷蔵庫の取っ手の拭き掃除に"),
            ("kitchen-paper", "油汚れの拭き取りに。大掃除では普段の倍くらい使う"),
            ("garbage-bag-45l", "不用品の処分で一気に減る。年末の収集日に合わせて多めに"),
            ("dish-soap-refill", "つけ置き洗いに大量に使うなら詰め替えの大容量が得"),
            ("dishwasher-tablet", "庫内の掃除のついでに買い足し"),
        ],
    },
    {
        "slug": "tokushu-winter",
        "short": "冬の備え",
        "title": "冬の備え 消耗品の最安まとめ（カイロ・マスク・ティッシュ）",
        "desc": "貼るカイロ・不織布マスク・ティッシュ・水など、冬に買い置きしたい消耗品を楽天市場の1枚・1本あたり単価で比較。毎朝更新。",
        "lead": "寒さと風邪のシーズンは、カイロ・マスク・ティッシュの減りが早くなります。どれも未開封なら長くもつので、安いときの箱買いが向いています。",
        "months": [11, 12, 1, 2],
        "items": [
            ("kairo", "未開封なら数年もつ。シーズン前の箱買いがいちばん安い"),
            ("mask", "風邪・インフルエンザの季節に。1枚あたりで見ると差が大きい"),
            ("tissue", "鼻かぜの時期は消費が倍に。5箱パックのまとめ買いで"),
            ("water-2l", "雪や停電の備えにも。1人1日3Lが目安"),
            ("aa-battery", "停電時のライト・ラジオ用に"),
            ("tea-500ml", "乾燥する季節の水分補給に。箱買いで1本あたりが下がる"),
        ],
    },
    {
        "slug": "tokushu-supersale",
        "short": "スーパーセール",
        "title": "楽天スーパーセールで買いだめする日用品 最安ガイド",
        "desc": "楽天スーパーセール・お買い物マラソンで買いだめしたい日用品を1回あたり単価で比較。ポイント倍率込みの実質価格にも対応。",
        "lead": "楽天スーパーセール（3・6・9・12月）やお買い物マラソンは、ショップの買い回りでポイント倍率が上がります。上の倍率を選ぶと実質価格で表示されます。腐らない・かさばっても使い切る日用品が買いだめ向きです。",
        "months": [3, 6, 9, 12],
        "items": [
            ("toilet-paper-double", "かさばるけれど必ず使い切る。長さ（m）あたりで比べる"),
            ("laundry-gelball", "大容量パックは1個あたりで見ると安い"),
            ("diaper-pants-m", "サイズアウトに注意。今のサイズは1〜2か月分まで"),
            ("rice", "精米日から1か月くらいでおいしく食べ切れる量を"),
            ("dog-food-dry", "開封後は1か月が目安。大袋より小分けの多いものが安心"),
            ("cat-litter", "重くてかさばるので、送料込みで比べる"),
            ("protein", "賞味期限が長いので、まとめ買いに向いている"),
        ],
    },
    {
        "slug": "tokushu-baby",
        "short": "赤ちゃん",
        "title": "出産準備・新生児の消耗品 最安まとめ（おむつ・おしりふき・ミルク）",
        "desc": "新生児用おむつ・おしりふき・粉ミルク・液体ミルクを楽天市場の1枚・100gあたり単価で比較。出産準備にどれくらい必要かの目安つき。",
        "lead": "新生児のころは、おむつを1日10〜12枚、おしりふきは1日20〜30枚くらい使います。すぐサイズが変わるので、おむつは買いすぎないのがコツです。",
        "months": [],
        "items": [
            ("diaper-tape-nb", "新生児用は1か月ほどでサイズアウトする子も多い。1〜2パックから"),
            ("diaper-tape-s", "体重5kg前後から。新生児用の次に使う"),
            ("baby-wipes", "サイズに関係なく長く使えるので、箱買いしても無駄になりにくい"),
            ("baby-formula", "缶の大きさで100gあたりが変わる。詰め替え用（袋）も安い"),
            ("liquid-milk", "外出や夜中に便利。常温保存できるので備えにも"),
        ],
    },
]


def active(month):
    """今月の特集を先に、それ以外を後ろに"""
    return sorted(FEATURES, key=lambda f: month not in f["months"])


def feature_cards(month):
    e = html.escape
    cards = "".join(
        f"<a class=fc href='{f['slug']}.html'>{'<span class=now>今月</span>' if month in f['months'] else ''}"
        f"<b>{e(f['short'])}</b><span>{e(f['title'])}</span></a>" for f in active(month))
    return ("<style>.tokushu{margin-top:22px;scroll-margin-top:120px}.fcs{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:10px}"
            ".fc{position:relative;display:grid;gap:2px;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:12px;color:inherit;text-decoration:none}"
            ".fc:hover{border-color:var(--acc)}.fc b{font-size:1.05rem}.fc span{font-size:.78rem;color:var(--mut);line-height:1.4}"
            ".fc .now{position:absolute;top:8px;right:8px;background:var(--acc);color:#fff;border-radius:6px;padding:0 6px;font-size:.68rem;font-weight:700}</style>"
            f"<section class=tokushu id=tokushu><h2>特集</h2><div class=fcs>{cards}</div></section>")


def render_feature(f, summary, by_slug, site, updated, short, per_text_of):
    e = html.escape
    url = f"{site}{f['slug']}.html"
    blocks, n_items, toc = "", 0, ""
    for slug, why in f["items"]:
        c, s = by_slug.get(slug), summary.get(slug) or {}
        top = s.get("top3") or []
        if not c or not top:
            continue
        n_items += len(top)
        per = per_text_of(c)
        d = 0 if per.startswith("1冊") else 1
        rows = "".join(
            f"<li class=pi><span class=rk>{i}</span><img src='{e(r['i'])}' alt='' loading=lazy width=64 height=64>"
            f"<div><a href='{e(r['u'])}' rel='sponsored noopener' target=_blank>{e(r['n'])}</a>"
            f"<p><b class=up data-u='{r['up']:.4f}' data-pt='{r.get('pt', 1)}' data-d='{d}'>{r['up']:.{d}f}円</b><small>/{e(per)}</small>"
            f" ・ {r['p']:,}円{'（送料込み）' if r.get('fs') else ''}</p></div></li>"
            for i, r in enumerate(top, 1))
        toc += f"<a href='#{slug}'>{e(short(c))}</a>"
        blocks += (f"<section id='{slug}'><h2>{e(short(c))}<small>{e(per)}の安い順</small></h2><p class=why>{e(why)}</p>"
                   f"<ol class=list>{rows}</ol><p class=all><a href='{slug}.html'>{e(short(c))}のランキングをすべて見る（{s.get('count', 0)}件）→</a></p></section>")
    others = "".join(f"<a href='{o['slug']}.html'>{e(o['title'])}</a>" for o in FEATURES if o is not f)
    ld = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "TANKA", "item": site},
        {"@type": "ListItem", "position": 2, "name": f["title"], "item": url}]}, ensure_ascii=False)
    robots = "" if n_items >= 6 else "<meta name=robots content=noindex>"
    return (PAGE.replace("@@TITLE@@", e(f["title"] + "｜TANKA")).replace("@@DESC@@", e(f["desc"])).replace("@@URL@@", e(url))
            .replace("@@ROBOTS@@", robots).replace("@@LD@@", ld).replace("@@H1@@", e(f["title"])).replace("@@LEAD@@", e(f["lead"]))
            .replace("@@TOC@@", toc).replace("@@BLOCKS@@", blocks or "<p>集計中です。</p>").replace("@@OTHERS@@", others)
            .replace("@@UPDATED@@", e(updated[5:10].replace("-", "/") + " " + updated[11:])))


PAGE = """<!doctype html><html lang=ja><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>@@TITLE@@</title>
<meta name=description content="@@DESC@@">@@ROBOTS@@
<link rel=canonical href="@@URL@@">
<meta property="og:title" content="@@TITLE@@"><meta property="og:description" content="@@DESC@@">
<meta property="og:url" content="@@URL@@"><meta property="og:type" content="article"><meta name="twitter:card" content="summary">
<script type="application/ld+json">@@LD@@</script>
<style>:root{--bg:#fff;--fg:#1d1d1f;--mut:#6e6e73;--card:#f5f5f7;--line:#e3e3e8;--acc:#bf0000;--ok:#0a7d4f}
@media(prefers-color-scheme:dark){:root{--bg:#111;--fg:#f2f2f7;--mut:#a1a1a6;--card:#1c1c1e;--line:#333;--acc:#ff6b6b;--ok:#4cd38f}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.7 system-ui,sans-serif}
main{max-width:760px;margin:auto;padding:16px}a{color:inherit}h1{font-size:1.35rem;line-height:1.4;margin:.2em 0 .4em}
.mut{color:var(--mut);font-size:.85rem}.pr{font-size:.75rem;color:var(--mut)}
.spu{display:flex;flex-wrap:wrap;gap:6px 10px;align-items:center;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:8px 12px;font-size:.85rem;margin:12px 0}
.spu select{font:inherit;padding:3px 6px;border-radius:8px;border:1px solid var(--line);background:var(--bg);color:var(--fg)}
.toc{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 4px}.toc a{border:1px solid var(--line);border-radius:999px;padding:3px 10px;text-decoration:none;font-size:.85rem;background:var(--card)}
section{scroll-margin-top:12px}h2{font-size:1.1rem;margin:1.8em 0 .2em}h2 small{font-weight:400;color:var(--mut);font-size:.78rem;margin-left:8px}
.why{margin:0 0 6px;color:var(--mut);font-size:.88rem}
.list{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.pi{display:flex;gap:10px;align-items:center;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:8px 10px}
.pi img{width:64px;height:64px;object-fit:contain;background:#fff;border-radius:8px;flex:none}.pi div{min-width:0}
.pi a{font-size:.88rem;line-height:1.4;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.pi p{margin:2px 0 0;font-size:.8rem;color:var(--mut)}.pi b{color:var(--acc);font-size:1.1rem}
.rk{flex:none;width:1.6em;height:1.6em;line-height:1.6em;text-align:center;border-radius:50%;background:var(--acc);color:#fff;font-size:.75rem;font-weight:700}
.all{margin:6px 0 0;font-size:.88rem}.all a{color:var(--ok);font-weight:600}
.others{display:grid;gap:6px;margin-top:8px}.others a{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px 12px;text-decoration:none;font-size:.9rem}
footer{margin-top:28px;color:var(--mut);font-size:.8rem}</style></head><body><main>
<p class=mut><a href="./">TANKA</a> › 特集</p>
<p class=pr>PR：楽天アフィリエイトを利用しています</p>
<h1>@@H1@@</h1>
<p>@@LEAD@@</p>
<div class=spu><label for=spu>楽天ポイント倍率（SPU）</label><select id=spu><option value=0>未設定</option></select><span id=spumsg class=mut></span></div>
<nav class=toc aria-label="目次">@@TOC@@</nav>
@@BLOCKS@@
<h2>ほかの特集</h2><div class=others>@@OTHERS@@</div>
<footer><p>価格は @@UPDATED@@ 時点で楽天市場から取得したものです。毎朝6時に更新しています。購入前に商品ページで確認してください。</p>
<p><a href="./">トップへ戻る</a> ・ <a href="calc.html">単価計算ツール</a> ・ <a href="about.html">このサイトについて</a></p></footer>
</main>
<script>
(function(){
  var sel=document.getElementById('spu'), msg=document.getElementById('spumsg'), ups=[].slice.call(document.querySelectorAll('.up'));
  for(var k=1;k<=20;k++){var o=document.createElement('option');o.value=k;o.textContent=k+'倍';sel.appendChild(o);}
  function spu(v){
    ups.forEach(function(b){var u=+b.dataset.u, d=+b.dataset.d;
      if(v>0){b.textContent='実質'+(u*(1-(v+(+b.dataset.pt||1)-1)/110)).toFixed(d)+'円';} else b.textContent=u.toFixed(d)+'円';});
    msg.textContent=v>0?'ショップのポイントアップも足した実質価格です':'';
  }
  var saved=0; try{saved=+localStorage.getItem('tanka_spu')||0}catch(e){}
  if(saved){sel.value=saved; spu(saved);}
  sel.addEventListener('change',function(){var v=+sel.value; try{localStorage.setItem('tanka_spu',v)}catch(e){} spu(v);
    if(window.gtag) gtag('event','set_spu',{value:v});});
})();
</script></body></html>"""
