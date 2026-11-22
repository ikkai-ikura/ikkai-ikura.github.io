"""「月いくら？」ページ: 毎日の最安単価 × 1か月に使う量 で、生活の消耗品の月額を出す。
一人暮らし（少なめの量の最安）とまとめ買い（全体の最安）の2通りを並べる。赤ちゃんは月齢ごと。"""
import html
import json

from features import PAGE

# (ジャンル, 1か月に使う量（そのジャンルの base の単位）, 表示用の量)
SOLO_MONTH = [
    ("toilet-paper-double", 150, "ダブル約5ロール（150m）"),
    ("tissue", 200, "1箱（200組）"),
    ("kitchen-paper", 150, "約1.5ロール（150カット）"),
    ("food-wrap", 10, "10m"),
    ("garbage-bag-45l", 10, "10枚"),
    ("liquid-laundry-refill", 400, "週4回分（400g）"),
    ("dish-soap-refill", 150, "150ml"),
    ("body-soap-refill", 300, "300ml"),
    ("shampoo-refill", 250, "250ml"),
    ("toothpaste", 50, "約半本（50g）"),
    ("rice", 4, "4kg（自炊で1日1〜2食）"),
]

# 月齢ごとの使用量の目安（おむつの枚数・おしりふきの枚数・ミルクだけで育てる場合の粉ミルクg）
BABY_STAGES = [
    ("0〜1か月（新生児）", "diaper-tape-nb", 330, 600, 2300),
    ("1〜3か月", "diaper-tape-s", 270, 500, 3000),
    ("3〜6か月", "diaper-tape-m", 210, 400, 3600),
    ("6〜12か月", "diaper-pants-m", 180, 300, 1800),
    ("1〜2歳", "diaper-pants-l", 150, 250, 0),
]

PAGES = [
    {
        "slug": "hitorigurashi-nichiyouhin",
        "short": "一人暮らしの日用品 月いくら？",
        "title": "一人暮らしの日用品は月いくら？ 楽天の最安で揃えた月額（毎日更新）",
        "desc": "一人暮らしの日用品（トイレットペーパー・洗剤・ティッシュ・ゴミ袋・お米など）を楽天の最安で揃えると月いくらか、毎日の価格から自動で計算。少なめの量で買う場合とまとめ買いの場合を比較。",
        "lead": "一人暮らしでよく使う消耗品を、1か月に使う量の目安と楽天の今日の最安単価から計算しました。一人暮らしで買いやすい少なめの量で揃えた場合と、置き場所があってまとめ買いする場合の2通りを並べています。",
        "guide": [
            ("使う量の目安について", "使う量は一人暮らしの平均的な目安です。洗濯の回数、自炊の頻度、髪の長さなどで変わるので、自分の使い方に近い量で読み替えてください。"),
            ("まとめ買いで安くするコツ", "トイレットペーパーや洗剤の詰め替えは腐らないので、置き場所があればまとめ買いのほうが安くなります。お米は精米日から1か月くらいで食べ切れる量が目安です。楽天スーパーセールやお買い物マラソンのポイントアップに合わせると、さらに安くなります。"),
        ],
        "faq": [
            ("一人暮らしの日用品代の平均は？", "総務省の家計調査では、単身世帯の「家事用消耗品」と「保健医療・理美容の消耗品」を合わせて月3,000〜5,000円くらいです。このページの合計はお米を含むので、そのぶん高めになります。"),
            ("どこで買うのが安い？", "ドラッグストアの特売とネット通販の最安はあまり変わりませんが、重くてかさばるトイレットペーパー・水・お米・洗剤はネットのまとめ買いが送料込みでも安くなりやすいです。"),
        ],
    },
    {
        "slug": "akachan-shoumouhin",
        "short": "赤ちゃんの消耗品 月いくら？",
        "title": "赤ちゃんの消耗品は月いくら？ おむつ・おしりふき・ミルクの月額（月齢別・毎日更新）",
        "desc": "赤ちゃんのおむつ・おしりふき・粉ミルクが月いくらかかるかを、月齢ごとの使用量の目安と楽天の今日の最安単価から自動で計算。新生児〜2歳まで。",
        "lead": "おむつ・おしりふき・粉ミルクを、月齢ごとの1か月の使用量の目安と、楽天の今日の最安単価から計算しました。ミルクは「ミルクだけで育てる場合」の量です。母乳と混合なら、ミルク代はおおよそ半分になります。",
        "guide": [
            ("使用量の目安について", "おむつは新生児で1日10〜12枚、成長とともに1日5〜7枚くらいに減ります。ミルクの量は赤ちゃんによって大きく違うので、缶の表示や健診で言われた量を優先してください。"),
            ("費用を抑えるコツ", "新生児用のおむつはすぐサイズアウトするので、まとめ買いは1〜2パックまでに。M以降はケース買いのほうが1枚あたりが安くなりやすいです。粉ミルクは缶より詰め替え（袋）のほうが100gあたりが安いことが多いです。"),
        ],
        "faq": [
            ("赤ちゃんの消耗品代は月いくらくらい？", "このページの計算では、ミルクだけで育てる場合、生後数か月はミルク代が大きく、1歳を過ぎるとおむつ代が中心になります。母乳との混合なら、ミルク代はおおよそ半分になります。"),
            ("おむつはどのメーカーが安い？", "サイズと入数で毎日入れ替わります。紙おむつの種類別まとめページで、サイズごとの最安とコスパ最強を確認できます。"),
        ],
    },
]


def _pick(summary, slug):
    """一人暮らし向け（少なめで最安）があればそれ、なければ全体の最安"""
    s = summary.get(slug) or {}
    so = s.get("solo")
    if so:
        return so["up"], so["u"], so["n"], True
    if s:
        return s["unit_price"], s.get("url", f"{slug}.html"), s.get("clean") or s.get("name", ""), False
    return None


def render_monthly(p, summary, by_slug, site, updated, short):
    e = html.escape
    url = f"{site}{p['slug']}.html"
    day = f"{int(updated[5:7])}月{int(updated[8:10])}日"
    if p["slug"] == "hitorigurashi-nichiyouhin":
        trs, tot_solo, tot_bulk = "", 0, 0
        for slug, qty, qlabel in SOLO_MONTH:
            c, s, pk = by_slug.get(slug), summary.get(slug), _pick(summary, slug)
            if not c or not s or not pk:
                continue
            per = c.get("per", 1)
            up, link, name, is_solo = pk
            m_solo, m_bulk = up * qty / per, s["unit_price"] * qty / per
            tot_solo += m_solo
            tot_bulk += m_bulk
            trs += (f"<tr><th><a href='{slug}.html'>{e(short(c))}</a><small>{e(qlabel)}</small></th>"
                    f"<td><a href='{e(link)}' rel='sponsored noopener' target=_blank>{m_solo:,.0f}円</a>"
                    f"<small>{e(name[:30])}{'' if is_solo else '（まとめ買いの最安）'}</small></td>"
                    f"<td>{m_bulk:,.0f}円</td></tr>")
        table = (f"<table class=cmp><caption>{e(day)}時点の楽天の最安単価で計算（1か月分）</caption>"
                 f"<thead><tr><th>品目・使う量</th><th>少なめの量で買う</th><th>まとめ買い</th></tr></thead><tbody>{trs}</tbody>"
                 f"<tfoot><tr><th>合計</th><td><b>{tot_solo:,.0f}円</b></td><td><b>{tot_bulk:,.0f}円</b></td></tr></tfoot></table>")
        tldr = (f"<p class=tldr><b>結論：</b>{e(day)}時点、一人暮らしの日用品（お米を含む{len(SOLO_MONTH)}品目）を楽天の最安で揃えると、"
                f"少なめの量で買って月<b>{tot_solo:,.0f}円</b>、まとめ買いなら月<b>{tot_bulk:,.0f}円</b>です。"
                + (f"まとめ買いにすると月{tot_solo - tot_bulk:,.0f}円（年{(tot_solo - tot_bulk) * 12:,.0f}円）安くなります。" if tot_solo - tot_bulk >= 50 else "")
                + "</p>")
    else:
        trs, firsty = "", 0
        for label, dslug, n_d, n_w, g_f in BABY_STAGES:
            cost, parts = 0, []
            for slug, qty in ((dslug, n_d), ("baby-wipes", n_w), ("baby-formula", g_f)):
                c, s = by_slug.get(slug), summary.get(slug)
                if not c or not s or not qty:
                    parts.append("—")
                    continue
                v = s["unit_price"] * qty / c.get("per", 1)
                cost += v
                parts.append(f"<a href='{slug}.html'>{v:,.0f}円</a><small>{qty:,}{e(c.get('base', ''))}</small>")
            if not label.startswith("1〜2"):
                firsty += cost * (1 if label.startswith("0") else 2 if label.startswith("1〜3") else 3 if label.startswith("3") else 6)
            trs += f"<tr><th>{e(label)}</th>" + "".join(f"<td>{x}</td>" for x in parts) + f"<td><b>{cost:,.0f}円</b></td></tr>"
        table = (f"<table class=cmp><caption>{e(day)}時点の楽天の最安単価で計算（1か月分・ミルクだけで育てる場合）</caption>"
                 f"<thead><tr><th>月齢</th><th>おむつ</th><th>おしりふき</th><th>粉ミルク</th><th>合計</th></tr></thead><tbody>{trs}</tbody></table>")
        tldr = (f"<p class=tldr><b>結論：</b>{e(day)}時点の楽天の最安で計算すると、ミルクだけで育てる場合の0歳の1年間のおむつ・おしりふき・ミルク代は"
                f"約<b>{firsty:,.0f}円</b>（月平均約{firsty / 12:,.0f}円）です。母乳と混合なら、ミルク代はおおよそ半分になります。</p>")
    guide = "".join(f"<h3>{e(h)}</h3><p>{e(t)}</p>" for h, t in p["guide"])
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in p["faq"])
    extra = f"<section class=guide><h2>知っておきたいこと</h2>{guide}</section><section class=faq><h2>よくある質問</h2>{faq}</section>"
    lds = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "TANKA", "item": site},
        {"@type": "ListItem", "position": 2, "name": p["title"], "item": url}]},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]}]
    others = "".join(f"<a href='{o['slug']}.html'>{e(o['title'])}</a>" for o in PAGES if o is not p)
    return (PAGE.replace("@@TITLE@@", e(p["title"] + "｜TANKA")).replace("@@DESC@@", e(p["desc"])).replace("@@URL@@", e(url))
            .replace("@@ROBOTS@@", "").replace("@@LD@@", json.dumps(lds, ensure_ascii=False)).replace("@@H1@@", e(p["title"]))
            .replace("@@LEAD@@", e(p["lead"])).replace("@@EVENT@@", tldr).replace("@@TOC@@", table).replace("@@BLOCKS@@", "")
            .replace("@@EXTRA@@", extra).replace("@@OTHERS@@", others)
            .replace("@@UPDATED@@", e(updated[5:10].replace("-", "/") + " " + updated[11:]))
            .replace("@@CRUMB@@", "月いくら？").replace("@@OTHERHEAD@@", "ほかの「月いくら？」"))
