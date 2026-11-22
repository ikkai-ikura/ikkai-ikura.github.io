"""楽天ROOM用のネタ帳ページ（本人だけが使う。検索エンジンには載せない）。
毎日のビルドで、週替わりの10ジャンルから「コスパ最強（なければ最安）」の商品と紹介文を作る。
商品リンクはアフィリエイトではない普通の商品ページ（本人がクリックしても自己クリックにならないように）。"""
import html
import json
from datetime import datetime

# 紹介文のハッシュタグ（ジャンルの区分ごと）
TAGS = {
    "baby": "#赤ちゃん #育児グッズ", "pet": "#ペットのいる暮らし", "laundry": "#洗濯 #家事楽",
    "paper": "#日用品ストック", "care": "#バスタイム", "food": "#食費節約", "eye": "#コンタクト",
    "furusato": "#ふるさと納税 #返礼品", "manga": "#漫画 #全巻セット",
}


def pick_week(cands, n=10, today=None):
    """候補（報酬の目安が大きい順）を週ごとにずらして n 件選ぶ。同じ週は同じ10件"""
    if not cands:
        return []
    week = (today or datetime.now()).isocalendar()[1]
    start = (week * n) % len(cands)
    return [cands[(start + i) % len(cands)] for i in range(min(n, len(cands)))]


def comment(c):
    """ROOMの紹介文（本人の言葉に直してもらう前提の下書き）"""
    tags = "#楽天ROOM #コスパ " + TAGS.get(c["group"], "#まとめ買い")
    if c["furusato"]:
        head = f"【ふるさと納税 {c['genre']}】寄付{c['price']:,}円で{c['count']:,.0f}{c['base']}。寄付額あたりの量で比べるとこれが多くもらえます。"
    elif c["kind"] == "cospa":
        head = (f"【{c['genre']}のコスパ最強】{c['unit_price']:,.1f}円/{c['unit']}。★{c['rating']:.1f}（レビュー{c['reviews']:,}件）で評価も高い定番。"
                f"{c['count']:,.0f}{c['base']}入り。")
    elif c["kind"] == "manga":
        head = f"【{c['genre']}】1冊あたり{c['unit_price']:,.0f}円。全巻まとめて買うならこのセットがいちばん安かったです。"
    else:
        head = f"【{c['genre']}の最安】{c['unit_price']:,.1f}円/{c['unit']}。{c['count']:,.0f}{c['base']}入りでまとめ買い向き。"
    return head + "毎日値段をチェックしていて、いまの最安クラスです。 " + tags


def render_room(picks, updated):
    e = html.escape
    cards = ""
    for i, c in enumerate(picks, 1):
        txt = comment(c)
        cards += (f"<li class=c data-id='{e(c['code'])}'><img src='{e(c['img'])}' alt='' loading=lazy>"
                  f"<div><b>{i}. {e(c['genre'])}</b><p class=n>{e(c['name'][:70])}</p>"
                  f"<textarea readonly rows=4>{e(txt)}</textarea>"
                  f"<p class=b><button type=button class=cp>紹介文をコピー</button>"
                  f"<a href='{e(c['item_url'])}' target=_blank rel=noopener>楽天の商品ページを開く</a>"
                  f"<label><input type=checkbox class=dn> 投稿した</label></p></div></li>")
    return f"""<!doctype html><html lang=ja><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>ROOMネタ帳（非公開）｜TANKA</title><meta name=robots content="noindex,nofollow">
<style>:root{{--bg:#fff;--fg:#1d1d1f;--mut:#6e6e73;--card:#f5f5f7;--line:#e3e3e8;--acc:#bf0000}}
@media(prefers-color-scheme:dark){{:root{{--bg:#111;--fg:#f2f2f7;--mut:#a1a1a6;--card:#1c1c1e;--line:#333;--acc:#ff6b6b}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.6 system-ui,sans-serif}}
main{{max-width:760px;margin:auto;padding:16px}}h1{{font-size:1.3rem;margin:.2em 0}}.mut{{color:var(--mut);font-size:.85rem}}
ol{{list-style:none;padding:0;display:grid;gap:12px}}.c{{display:flex;gap:10px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px}}
.c img{{width:72px;height:72px;object-fit:contain;background:#fff;border-radius:8px;flex:none}}.c div{{min-width:0;flex:1}}
.n{{margin:2px 0;font-size:.82rem;color:var(--mut)}}textarea{{width:100%;font:inherit;font-size:.85rem;border:1px solid var(--line);border-radius:8px;padding:6px;background:var(--bg);color:var(--fg)}}
.b{{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;margin:6px 0 0;font-size:.9rem}}
.cp{{font:inherit;font-weight:700;padding:6px 12px;border:0;border-radius:8px;background:var(--acc);color:#fff;cursor:pointer}}
.c.done{{opacity:.5}}a{{color:var(--acc);font-weight:600}}</style></head><body><main>
<h1>楽天ROOM ネタ帳</h1>
<p class=mut>あなた専用のページです（検索エンジンには載せていません）。毎週月曜に10商品が入れ替わり、値段は毎日更新されます（最終更新 {e(updated)}）。</p>
<p class=mut>使い方：①「紹介文をコピー」②「楽天の商品ページを開く」③ 商品ページの「ROOMに投稿」を押して貼り付け、ひとこと自分の言葉に直して投稿。商品ページのリンクはアフィリエイトではないので、押しても問題ありません。</p>
<ol>{cards}</ol></main>
<script>
(function(){{
  var KEY='tanka_room_done'; var done={{}}; try{{done=JSON.parse(localStorage.getItem(KEY)||'{{}}')}}catch(e){{}}
  [].forEach.call(document.querySelectorAll('.c'),function(li){{
    var id=li.dataset.id, cb=li.querySelector('.dn'), ta=li.querySelector('textarea');
    if(done[id]){{cb.checked=true;li.classList.add('done')}}
    cb.addEventListener('change',function(){{done[id]=cb.checked;li.classList.toggle('done',cb.checked);try{{localStorage.setItem(KEY,JSON.stringify(done))}}catch(e){{}}}});
    li.querySelector('.cp').addEventListener('click',function(){{var b=this;
      (navigator.clipboard?navigator.clipboard.writeText(ta.value):Promise.reject()).catch(function(){{ta.select();document.execCommand('copy')}}).then(function(){{b.textContent='コピーしました';setTimeout(function(){{b.textContent='紹介文をコピー'}},1500)}});
    }});
  }});
}})();
</script></body></html>"""
