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
    (MW, "ハンドソープ 詰め替え 770ml×3袋", 2310), (MW, "食器用洗剤 詰め替え 超特大 1.2L", 1200),
    (MW, "ボディソープ つめかえ 2000mL 2個セット", 4000), (MW, "柔軟剤 詰め替え 1250ml 380ml", None),
    (KW, "コシヒカリ 令和7年産 5kg×2袋", 10), (KW, "ブレンド米 20kg (10kg×2)", 20), (KW, "お米 2kg 5kg 10kg 選べる", None),
    (GW, "ロイヤルカナン インドア 4kg 単品 2個セット まとめ買い", None),
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
]

if __name__ == "__main__":
    bad = [(n, build.parse_count(n, w, 2, 10000), e) for w, n, e in CASES if build.parse_count(n, w, 2, 10000) != e]
    bad += [(n, build.parse_product(n, **p), e) for p, n, e in PRODUCT_CASES if build.parse_product(n, **p) != e]
    CASES = CASES + PRODUCT_CASES
    for b in bad:
        print("NG", *b)
    print(f"{len(CASES) - len(bad)}/{len(CASES)} OK")
    raise SystemExit(1 if bad else 0)
