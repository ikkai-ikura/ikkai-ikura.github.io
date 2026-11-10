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
    CASES = CASES + PRODUCT_CASES + VOL_CASES
    # KW_CHECK: 楽天の検索語は1文字の単語を含むとエラーになる
    bad += [(kw, "1文字の単語", None) for c in build.CATEGORIES for kw in (c.get("keywords") or [c["keyword"]])
            if any(len(t) == 1 for t in kw.split())]
    for b in bad:
        print("NG", *b)
    print(f"{len(CASES) - len(bad)}/{len(CASES)} OK")
    raise SystemExit(1 if bad else 0)
