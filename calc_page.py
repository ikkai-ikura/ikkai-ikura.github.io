"""単価計算ツールのページ（calc.html）。「1枚あたりの値段 計算」「100gあたり 計算」などの検索向け。
入力したその場で計算し、ボタンは無い。下に TANKA の毎日更新ランキングへの導線を置く。"""
import html
import json

FAQ = [
    ("1個あたり・1枚あたりの値段はどう計算する？",
     "「価格 ÷ 個数（枚数）」で計算します。例えば 1,980円で 3袋×60枚 なら、1,980 ÷ 180 = 1枚あたり 11.0円です。セット数がある時は、1袋の量にセット数を掛けた合計で割ります。"),
    ("100gあたり・100mlあたりの値段は？",
     "「価格 ÷ 内容量 × 100」で計算します。例えば 2kg（2,000g）で 1,580円なら、1,580 ÷ 2,000 × 100 = 100gあたり 79.0円です。"),
    ("トイレットペーパーはどう比べる？",
     "ロール数ではなく長さで比べます。「1ロールの長さ（m）× ロール数」の合計で割ると、巻きの長さが違う商品も同じ基準で比べられます。シングルとダブルは別々に比べるのが基本です。"),
    ("ポイント還元は計算に入れるべき？",
     "楽天などでポイントが付く場合は、実際に戻ってくる分を差し引いた「実質価格」で比べると正確です。このツールではポイント倍率（%）を入れると実質単価も表示します。"),
    ("送料はどうする？",
     "送料がかかる商品は、価格に送料を足してから計算してください。送料込みで比べないと、表示価格が安くても実際には高くなることがあります。"),
]


def render_calc(site, groups, by_slug, short, per_text_of):
    e = html.escape
    url = f"{site}calc.html"
    links = ""
    for gid, label, slugs in groups:
        if gid == "manga":
            continue
        items = "".join(f"<a href='{e(s)}.html'>{e(short(by_slug[s]))}<small>{e(per_text_of(by_slug[s]))}</small></a>"
                        for s in slugs if s in by_slug)
        if items:
            links += f"<h3>{e(label)}</h3><div class=lk>{items}</div>"
    faq_html = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in FAQ)
    ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
        ensure_ascii=False)
    title = "単価計算ツール｜1個・1枚・100gあたりの値段を計算して比較【無料】｜TANKA"
    desc = "価格と内容量を入れるだけで、1個・1枚・100g・100mlあたりの値段を自動計算。最大4商品を並べて、どれが何%安いかすぐ分かります。セット数・ポイント還元にも対応。"
    page = PAGE.replace("@@TITLE@@", e(title)).replace("@@DESC@@", e(desc)).replace("@@URL@@", e(url))
    return page.replace("@@LINKS@@", links).replace("@@FAQ@@", faq_html).replace("@@LD@@", ld)


PAGE = """<!doctype html><html lang=ja><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>@@TITLE@@</title>
<meta name=description content="@@DESC@@">
<link rel=canonical href="@@URL@@">
<meta property="og:title" content="@@TITLE@@"><meta property="og:description" content="@@DESC@@">
<meta property="og:url" content="@@URL@@"><meta property="og:type" content="website"><meta name="twitter:card" content="summary">
<script type="application/ld+json">@@LD@@</script>
<style>:root{--bg:#fff;--fg:#1d1d1f;--mut:#6e6e73;--card:#f5f5f7;--line:#e3e3e8;--acc:#0a7d4f;--accbg:#e6f6ee}
@media(prefers-color-scheme:dark){:root{--bg:#111;--fg:#f2f2f7;--mut:#a1a1a6;--card:#1c1c1e;--line:#333;--acc:#4cd38f;--accbg:#123222}a{color:#8ab4ff}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.7 system-ui,sans-serif}
main{max-width:760px;margin:auto;padding:16px}h1{font-size:1.4rem;margin:.2em 0}h2{font-size:1.1rem;margin-top:1.8em}h3{font-size:.95rem;margin:1.2em 0 .4em}
.mut{color:var(--mut);font-size:.85rem}
.units{display:flex;flex-wrap:wrap;gap:6px;margin:12px 0}.units button{border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:999px;padding:6px 12px;font:inherit;cursor:pointer}
.units button.on{background:var(--acc);border-color:var(--acc);color:#fff}
.row{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px 12px;margin:8px 0;display:grid;grid-template-columns:repeat(4,1fr);gap:8px;align-items:end}
.row.best{border-color:var(--acc);background:var(--accbg)}
.row b.nm{grid-column:1/-1;font-size:.9rem}
label{font-size:.75rem;color:var(--mut);display:block}input{width:100%;font:16px system-ui;padding:7px 8px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--fg)}
.out{grid-column:1/-1;font-size:.95rem}.out strong{font-size:1.25rem}.tag{display:inline-block;background:var(--acc);color:#fff;border-radius:6px;padding:0 6px;font-size:.75rem;margin-left:6px}
.lk{display:flex;flex-wrap:wrap;gap:6px}.lk a{border:1px solid var(--line);border-radius:10px;padding:6px 10px;text-decoration:none;color:var(--fg);background:var(--card);font-size:.88rem}
.lk a small{display:block;color:var(--mut);font-size:.72rem}
details{border-bottom:1px solid var(--line);padding:8px 0}summary{cursor:pointer;font-weight:600}
@media(max-width:520px){.row{grid-template-columns:1fr 1fr}}</style></head><body><main>
<p class=mut><a href="./">TANKA</a> › 単価計算ツール</p>
<h1>単価計算ツール</h1>
<p>価格と内容量を入れると、<b>1個・1枚・100g・100mlあたりの値段</b>をその場で計算します。いちばん安い商品に印が付き、ほかより何%安いかも分かります。</p>
<div class=units id=units></div>
<div id=rows></div>
<p class=mut>送料がかかる商品は、価格に送料を足して入力してください。ポイント倍率は任意です（例: 5倍なら 5）。</p>
<h2>計算済みの最安ランキング（毎日更新）</h2>
<p>よく買う日用品は、TANKAが楽天市場の商品を毎日自動で単価計算しています。自分で計算しなくても、安い順にすぐ分かります。</p>
@@LINKS@@
<h2>よくある質問</h2>
@@FAQ@@
<p class=mut style="margin-top:20px"><a href="./">トップへ戻る</a> ・ <a href="sim.html">格安SIM料金比較</a> ・ <a href="about.html">このサイトについて</a></p>
</main>
<script>
(function(){
var U=[["個","1個",1],["枚","1枚",1],["g","100g",100],["ml","100ml",100],["m","100m",100],["回","1回",1],["kg","1kg",1]];
var u=0,N=4,R=document.getElementById("rows"),B=document.getElementById("units");
U.forEach(function(x,i){var b=document.createElement("button");b.type="button";b.textContent=x[1]+"あたり";b.onclick=function(){u=i;draw();calc()};B.appendChild(b)});
for(var i=0;i<N;i++){R.insertAdjacentHTML("beforeend","<div class=row id=r"+i+"><b class=nm>商品"+"ABCD"[i]+"</b>"+
"<div><label>価格（円）</label><input inputmode=decimal data-k=p></div>"+
"<div><label class=ql>内容量</label><input inputmode=decimal data-k=q></div>"+
"<div><label>セット数</label><input inputmode=decimal data-k=s placeholder=1></div>"+
"<div><label>ポイント倍率</label><input inputmode=decimal data-k=pt placeholder=1></div><div class=out></div></div>")}
R.addEventListener("input",calc);
function v(r,k){var x=parseFloat((r.querySelector("[data-k="+k+"]").value||"").replace(/[,，円]/g,""));return isFinite(x)?x:NaN}
function draw(){[].forEach.call(B.children,function(b,i){b.className=i==u?"on":""});
[].forEach.call(document.querySelectorAll(".ql"),function(l){l.textContent="内容量（"+U[u][0]+"）"})}
function calc(){var res=[];
for(var i=0;i<N;i++){var r=document.getElementById("r"+i),p=v(r,"p"),q=v(r,"q"),s=v(r,"s"),pt=v(r,"pt");
if(!(s>0))s=1;var o=r.querySelector(".out");r.classList.remove("best");
if(p>0&&q>0){var per=p/(q*s)*U[u][2],eff=pt>1?per*(1-(pt-1)/100):per;res.push({i:i,per:per,eff:eff});
o.innerHTML=U[u][1]+"あたり <strong>"+per.toFixed(per<10?2:1)+"円</strong>"+(pt>1?"（ポイント込み実質 "+eff.toFixed(eff<10?2:1)+"円）":"")}else o.textContent=""}
if(res.length>1){res.sort(function(a,b){return a.eff-b.eff});var b=res[0],r=document.getElementById("r"+b.i);r.classList.add("best");
var t=res.slice(1).map(function(x){return "商品"+"ABCD"[x.i]+"より"+((1-b.eff/x.eff)*100).toFixed(0)+"%安い"}).join("・");
r.querySelector(".out").insertAdjacentHTML("beforeend","<span class=tag>いちばん安い</span><br><span class=mut>"+t+"</span>")}}
draw();
})();
</script></body></html>"""
