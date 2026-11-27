"""数量解析の回帰テスト: python test_parse.py"""
import build

CW = ["個入り", "個入", "個", "錠", "粒", "枚入", "枚", "回"]
BW = ["本入り", "本入", "本"]
GW = {"g": 1, "kg": 1000}
MW = build.ML
KW = {"kg": 1, "キロ": 1}
CASES = [
    (CW, "150個入り 3袋セット", 450), (CW, "【3個セット】150個入り", 450), (CW, "60粒/箱×3箱", 180),
    (CW, "50個入×4セット(1個13g)", 200), (CW, "100錠 2個セット", 200), (CW, "112枚入×4袋セット", 448),
    (CW, "112枚 4袋", None), (CW, "1200枚（400枚×3袋）", 1200), (CW, "88枚 66枚 56枚", None),
    (CW, "ゴミ袋 45L 10枚×60冊", 600), (CW, "フィニッシュ 150個入り", 150),
    (BW, "保存水 2L 6本 / 2ケース ( 12本セット ) 長期", 12), (BW, "水 2リットル 9本 天然水", 9),
    (BW, "炭酸水 500ml 48本 (24本×2ケース)", 48), (BW, "40本入り 単3", 40),
    (GW, "500g 4個セット 2kg", 2000), (GW, "(500g×4袋) 2kg", 2000), (GW, "100g/200g/300g", None),
    (GW, "コーヒー豆 1kg", 1000),
    (["枚入り", "枚入", "枚", "シート"], "パンパース テープ Sサイズ 大容量 198枚(66枚×3個）", 198),
    (["枚入り", "枚入", "枚", "シート"], "メリーズ テープ Sサイズ 62枚×4個入", 248),
    (GW, "レーベンスミルク はいはい(2缶入×4セット(1缶810g))", 6480), (GW, "ほほえみらくらくキューブ(27g×120袋)", 3240),
    (CW, "50個入×4セット(1個13g)", 200), (BW, "40本セット 単3電池 LR6N/10S", 40),
    (GW, "オキシクリーン 5.26kg 大容量", 5260), (GW, "オキシクリーン 1500g×2個セット", 3000),
    (["個入り", "個入", "個", "枚入り", "枚入", "枚", "P入", "P"], "貼るカイロ 30個入×8箱", 240),
    (["個入り", "個入", "個", "枚入り", "枚入", "枚", "P入", "P"], "ホッカイロ 貼る 30P", 30),
    (BW, "伊右衛門 525ml×24本", 24),
    (BW, "伊賀の天然水 強炭酸水 500ml×2ケース 48本炭酸", 48), (BW, "強炭酸水 500ml 48本 送料無料 2ケース PET", 48),
    (BW, "おいしい水 富士山 2000ml 【2L×12本(2ケース)】", 12), (BW, "2L×6本入り 2ケース", 12), (BW, "お〜いお茶 600ml×24本×2ケース", 48),
    (GW, "ソイプロテイン 無添加 1kg／3kg(1kg×3袋)", None), (GW, "【4・6個セット】レノア 650g", None),
    (GW, "はいはい 810g 2缶パック", 1620), (GW, "ほほえみ 800g×2缶", 1600), (GW, "はぐくみ 800g×8缶 ケース", 6400),
    (MW, "ハンドソープ 詰め替え 770ml×3袋", 2310), (MW, "食器用洗剤 詰め替え 超特大 1.2L", 1200),
    (MW, "ボディソープ つめかえ 2000mL 2個セット", 4000), (MW, "柔軟剤 詰め替え 1250ml 380ml", None),
    (MW, "ソフラン 柔軟剤 詰め替え メガジャンボ 2100ml×6袋 4袋 2袋 大容量", None), (MW, "アタック 2380g×6袋 4袋 2袋", None), (MW, "ハミング 詰め替え 1190ml×6袋", 7140),
    (KW, "コシヒカリ 令和7年産 5kg×2袋", 10), (KW, "ブレンド米 20kg (10kg×2)", 20), (KW, "お米 2kg 5kg 10kg 選べる", None),
    (GW, "ロイヤルカナン インドア 4kg 単品 2個セット まとめ買い", None),
    ({"mAh": 1}, "Anker モバイルバッテリー 10000mAh 22.5W", 10000), ({"mAh": 1}, "モバイルバッテリー 5000mAh 10000mAh 選べる", None),
]

TI = {"size": r"(\d{2,3})\s*組", "pack": r"箱|個", "lo": 300, "hi": 100000}
PRODUCT_CASES = [
    (build.TP_PARSER, "トイレットペーパー ダブル 30m 12ロール×4パック", 1440),
    (build.TP_PARSER, "トイレットペーパー シングル 60m 48ロール(12ロール×4パック)", 2880),
    (build.TP_PARSER, "1.5倍巻 45m 12R 8パックセット", 4320),
    (build.TP_PARSER, "トイレットペーパー 114mm×27.5m ダブル 96ロール", 2640),
    (build.TP_PARSER, "シングル60m ダブル30m 12ロール", None),
    (TI, "ティッシュ 160組 5箱×12パック", 9600), (TI, "ティッシュペーパー 150組(300枚) 60箱(5箱×12パック)", 9000),
    (TI, "エリエール 180組 5箱 ×10セット", 9000), (TI, "鼻セレブ 200組 5箱", 1000),
    (TI, "【50・90個】ティッシュ 300枚（150組）", None), (TI, "ソフトパック 200組 大容量 80個 90個", None),
    (TI, "400枚 ( 200組 ) 80個 大容量 5個 × 16", 16000),
]

if __name__ == "__main__":
    bad = [(n, build.parse_count(n, w, 2, 10000), e) for w, n, e in CASES if build.parse_count(n, w, 2, 10000) != e]
    bad += [(n, build.parse_product(n, **p), e) for p, n, e in PRODUCT_CASES if build.parse_product(n, **p) != e]
    VOL_CASES = [("【中古】呪術廻戦 全巻セット 1-29巻 完結", 29), ("鬼滅の刃 全23巻 完結セット 新品", 23),
                 ("ワンピース 全巻セット 1～111巻", 111), ("進撃の巨人 全巻 34冊セット", 34), ("お好きな巻 1冊から 全巻対応", None)]
    bad += [(n, build.parse_volumes(n)[0], e) for n, e in VOL_CASES if build.parse_volumes(n)[0] != e]
    LIMIT_CASES = [  # 購入・同梱の上限は数量ではない
        (lambda n: build.parse_product(build.strip_limits(n), **build.CATEGORIES_BY_SLUG["food-wrap"]["parser"]), "【お一人様2個まで】旭化成 業務用サランラップ BOXタイプ 30cm×50m", 50),
        (lambda n: build.parse_product(build.strip_limits(n), **build.CATEGORIES_BY_SLUG["liquid-milk"]["parser"]), "明治ほほえみ らくらくミルク240ml 6本入り【0から1歳用】【2セットまで】", 1440),
        (lambda n: build.parse_volumes(build.strip_limits(n))[0], "【中古】HUNTER×HUNTER 37巻全巻セット150冊迄同梱ok 2k-0953", None),
    ]
    bad += [(n, f(n), e) for f, n, e in LIMIT_CASES if f(n) != e]
    OTHER_CASES = [  # 漫画: 別作品の名前が入った出品はそのページに載せない
        ("manga-kimetsu", "【中古】七つの大罪 1〜41巻 完結・おまけ 付き 鈴木央 講談社 レンタル落ち 鬼滅の刃 全巻", 0),
        ("manga-kimetsu", "【中古】鬼滅の刃 1〜23巻 漫画 全巻セット 完結 ジャンプコミックス 吾峠呼世晴 集英社", 1),
        ("manga-nanatsu", "【中古】七つの大罪 1〜41巻 漫画 全巻セット 完結 週マガKC 鈴木央 講談社", 1),
        ("manga-hunter", "HUNTER×HUNTER ハンターハンター ＜1〜39巻＞ 冨樫義博 全巻", 1),
        ("manga-slamdunk", "【中古】 送料無料 バガボンド 1-37巻 井上雄彦(スラムダンク著者) バカボンド 中古コミック 全巻セット", 0),
        ("mask", "マスク 子供 マスク 不織布 子供用 小学生 50枚 x 6箱 300枚", 0),
        ("mask", "【血色不織布マスク】マスク 子供 不織布マスク 50枚 ×20箱 カラーマスク快適 子供用 小さめ プリーツ", 0),
    ]
    def _n_rows(slug, name):
        it = {"itemName": name, "itemPrice": 5000, "reviewCount": 0}
        return len(build.rank([it], build.CATEGORIES_BY_SLUG[slug]))
    bad += [(n, _n_rows(s, n), e) for s, n, e in OTHER_CASES if _n_rows(s, n) != e]
    LIMIT_CASES = LIMIT_CASES + [(None, n, e) for s, n, e in OTHER_CASES]
    # マスク: 子供専用は除外、「大人・キッズ選べる」は残す（ng_unless）
    _MASK_KEEP = [("プリーツマスク 50枚 血色マスク 不織布マスク 大きい 大きめ キッズ 子供用 小さめ 小さい サイズ", 1),
                  ("マスク プリーツ 不織布 50枚 12箱 600枚セット 不織布マスク 子供 大人 立体", 1),
                  ("【血色不織布マスク】マスク 子供 不織布マスク 50枚 ×20箱 カラーマスク快適 子供用 小さめ プリーツ", 0)]
    def _n_mask(name):
        return len(build.rank([{"itemName": name, "itemPrice": 400, "reviewCount": 50, "itemCode": "m"}], build.CATEGORIES_BY_SLUG["mask"]))
    bad += [(n, _n_mask(n), e) for n, e in _MASK_KEEP if _n_mask(n) != e]
    LIMIT_CASES = LIMIT_CASES + [(None, n, e) for n, e in _MASK_KEEP]
    # 同じメーカー・同じ枚数・同じ値段の出品は1行に（テープS: メリーズ296枚が書き方違いで2行出ていた）
    _its = [{"itemName": "花王 メリーズさらさらエアスルー テープ Sサイズ (4~8kg)296枚 (74枚×4) 送料無料", "itemPrice": 7150, "reviewCount": 50, "itemCode": "a"},
            {"itemName": "メリーズ テープ Sサイズ 74シート×4個入り", "itemPrice": 7150, "reviewCount": 50, "itemCode": "b"},
            {"itemName": "ムーニー テープ Sサイズ 74枚×4 (4~8kg)", "itemPrice": 7150, "reviewCount": 50, "itemCode": "c"}]
    _n = len(build.rank(_its, build.CATEGORIES_BY_SLUG["diaper-tape-s"]))
    if _n != 2:
        bad.append(("同一出品のまとめ(テープS)", _n, 2))
    LIMIT_CASES = LIMIT_CASES + [(None, "same-listing", 2)]
    # 漫画: 系列店が同じ文面・同じ値段で出している全巻セットは1行に（スラムダンク・BLEACHで1位と2位が同じだった）
    _its = [{"itemName": "【漫画全巻セット】【中古】BLEACH（ブリーチ） ＜1〜74巻完結＞ 久保帯人", "itemPrice": 14600, "reviewCount": 0, "shopName": "A"},
            {"itemName": "【漫画】【中古】BLEACH（ブリーチ） ＜1〜74巻完結＞ 久保帯人 【全巻セット】", "itemPrice": 14600, "reviewCount": 0, "shopName": "B"},
            {"itemName": "【中古】BLEACH ブリーチ (1-74巻 全巻) 全巻セット", "itemPrice": 14600, "reviewCount": 0, "shopName": "C"}]
    _n = len(build.rank(_its, build.CATEGORIES_BY_SLUG["manga-bleach"]))
    if _n != 2:
        bad.append(("系列店の同じ出品のまとめ(漫画)", _n, 2))
    LIMIT_CASES = LIMIT_CASES + [(None, "same-manga-listing", 2)]
    # ラップ: 業務用（30本ケース・750mロール）は印を付けて「最安」に出さない。家庭用100mは対象外
    for _name, _e in [("まとめ買い 業務用 キッチニスタラップ 30cm×100m 外刃タイプ 30本入", True),
                      ("ポリマラップ R300 幅30cm×750m 2本", True), ("リケンラップ VS300 ラップ 30cm×500m 1本 塩ビラップ", True), ("リケンラップ たっぷり 30cm*100m(3本パック)", False),
                      ("宇部フィルム ポリラップ 30cm×50m", False)]:
        _r = build.rank([{"itemName": _name, "itemPrice": 3000, "reviewCount": 10}], build.CATEGORIES_BY_SLUG["food-wrap"])
        if not _r or _r[0]["biz"] != _e:
            bad.append(("ラップ業務用", _name, _e))
        LIMIT_CASES = LIMIT_CASES + [(None, _name, _e)]
    PICK_CASES = [  # ペットシーツのサイズ選択式: レギュラーの枚数だけ（最小）
        ("Air Ultra Lightシート ペットシーツ　レギュラー　800枚　(200枚×4袋)　ワイド　400枚　(100枚×4袋)", 800),
        ("ペットシーツ 薄型 レギュラー800枚 レギュラー1200枚 ワイド400枚 ワイド600枚 ダブルワイド 200枚", 800),
        ("ペットシーツ ワイド 200枚 レギュラー 400枚 スーパーワイド 100枚 大容量", 400),
        ("猛吸くん 4袋セット〔レギュラーサイズ(400枚)/ワイドサイズ(200枚)/スーパーワイドサイズ(100枚)〕", 400),
        ("ペットシーツ レギュラー ワイド 800枚 おしっこシート 400枚 薄型", None),
        ("ペットシーツ 中厚型 レギュラー ワイド スーパーワイド 1ケース", None),
        ("超薄型 ペットシーツ レギュラー 1200枚 800枚 ワイド 600枚 400枚 スーパーワイド 300枚 200枚", 800),
        ("超薄型 ペットシーツ レギュラー 1200枚（300枚×4袋） ワイド 600枚（150枚×4袋）", 1200),
    ]
    bad += [(n, build.size_pick_min(n, "レギュラー", 20, 3000), e) for n, e in PICK_CASES
            if build.size_pick_min(n, "レギュラー", 20, 3000) != e]
    WIDE = build.CATEGORIES_BY_SLUG["pet-sheet-wide"]["size_word"]
    WIDE_CASES = [(n, e) for (n, _), e in zip(PICK_CASES, [400, 400, 200, 200, None, None, 400, 600])]
    bad += [(n, build.size_pick_min(n, WIDE, 20, 3000), e) for n, e in WIDE_CASES
            if build.size_pick_min(n, WIDE, 20, 3000) != e]
    LIMIT_CASES = LIMIT_CASES + [(None, n, e) for n, e in PICK_CASES]
    # 漫画: 1冊3,000円超の全巻セット（透明カバー付きの高額出品）は載せない
    _ck = build.CATEGORIES_BY_SLUG["manga-chiikawa"]
    _r = build.rank([{"itemName": n, "itemPrice": p, "reviewCount": 0} for n, p in [
        ("[新品]ちいかわ なんか小さくてかわいいやつ (1-9巻 最新刊) 全巻セット", 12595),
        ("【中古】ちいかわ なんか小さくてかわいいやつ 1〜8巻 までの全巻セット ワイドKC ナガノ 講談社", 14300),
        ("【予約商品】ちいかわ なんか小さくてかわいいやつ コミック 全巻セット（1-8巻セット・以下続巻)ナガノ 「透明カバー付」", 64580)]], _ck)
    if len(_r) != 2 or any(r["price"] == 64580 for r in _r):
        bad.append(("漫画の高額外れ値", [r["price"] for r in _r], 2))
    LIMIT_CASES = LIMIT_CASES + [(None, "漫画の高額外れ値", 2)]
    # ふるさと納税: 回数が決まった定期便は載せない（1回分で割ると単価が回数倍になる）。選べる出品は残す
    _fw = build.CATEGORIES_BY_SLUG["furusato-water-2l"]
    _r = build.rank([{"itemName": n, "itemPrice": p, "reviewCount": 5, "itemCode": "f123456-x:1"} for n, p in [
        ("【ふるさと納税】 《定期便》 四万十の純天然水 (2L×6本)×2ケース 3回コース 水 天然水", 24000),
        ("【ふるさと納税】＜定期便＞ 水の王国 ミネラルウォーター 2L×6本 2ヶ月毎に1回 ＜全3回＞ 定期便", 27000),
        ("【ふるさと納税】水 ミネラルウォーター 2L 定期便《出荷時期をお選びください》 熊本イオン純天然水 1箱 10本 2箱 20本", 4700)]], _fw)
    if [r["price"] for r in _r] != [4700]:
        bad.append(("ふるさと納税の定期便", [r["price"] for r in _r], [4700]))
    LIMIT_CASES = LIMIT_CASES + [(None, "ふるさと納税の定期便", 1)]
    # 枚数の選択式（「30・40・60・90・150枚」）は最大の150枚で割らず、最小の30枚で割る（2026-11-23 マスク1位 798円が5.3円/枚と表示）
    _mk = build.CATEGORIES_BY_SLUG["mask"]
    _r = build.rank([{"itemName": "マスク 不織布 アイリスオーヤマ 立体 30・40・60・90・150枚 立体マスク バイカラー", "itemPrice": 798, "reviewCount": 50}], _mk)
    if [round(r["unit_price"], 2) for r in _r] not in ([], [26.6]):
        bad.append(("枚数の選択式", [round(r["unit_price"], 2) for r in _r], [26.6]))
    LIMIT_CASES = LIMIT_CASES + [(None, "枚数の選択式", 1)]
    # 表示名: 店の宣伝を外しても商品名は残す
    NAME_CASES = [
        ("【ポイント10倍！11/19-12/31迄】P&G アリエールジェルボール4D微香 83個×4個セット", "P&G アリエールジェルボール4D微香 83個×4個セット"),
        ("【ポイント5倍 要エントリー】アタック消臭ストロングジェル 4kg×4本／ケース 花王プロシリーズ", "アタック消臭ストロングジェル 4kg×4本／ケース 花王プロシリーズ"),
        ("[エントリーで最大ポイント10倍/スタンプラリー]【公式】水 2リットル 9本 天然水", "水 2リットル 9本 天然水"),
        ("ソニッケアー 替えブラシ/当店全商品P5倍!BLACKFRIDAY中！要エントリー/ HX6064 4本入", "ソニッケアー 替えブラシ HX6064 4本入"),
        ("【推しの子】 1〜16巻 漫画 全巻セット 完結", "推しの子 1〜16巻 漫画 全巻セット 完結"),
    ]
    bad += [(n, build.clean_name(n, 200), e) for n, e in NAME_CASES if build.clean_name(n, 200) != e]
    LIMIT_CASES = LIMIT_CASES + [(None, n, e) for n, e in NAME_CASES]
    VOL_CASES = VOL_CASES + LIMIT_CASES
    CASES = CASES + PRODUCT_CASES + VOL_CASES
    # KW_CHECK: 楽天の検索語は1文字の単語を含むとエラーになる
    bad += [(kw, "1文字の単語", None) for c in build.CATEGORIES for kw in (c.get("keywords") or [c["keyword"]])
            if any(len(t) == 1 for t in kw.split())]
    for b in bad:
        print("NG", *b)
    print(f"{len(CASES) - len(bad)}/{len(CASES)} OK")
    raise SystemExit(1 if bad else 0)
