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

ML = {"ml": 1, "mL": 1, "ML": 1, "L": 1000, "l": 1000, "リットル": 1000}
REFILL = ["詰め替え", "詰替", "つめかえ", "詰めかえ"]
TP_PARSER = {"size": r"(\d{2,3}(?:\.\d)?)\s*m(?![ml])", "pack": r"ロール|R(?![a-z])", "lo": 100, "hi": 20000}
NG_ALL = ["ふるさと納税", "返礼品"]  # 寄付額なので実際の値段と比べられない

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
    {
        "slug": "laundry-gelball",
        "title": "洗濯洗剤ジェルボール 1回あたり単価ランキング",
        "keyword": "洗濯洗剤 ジェルボール",
        "unit": "回",
        "words": ["個入り", "個入", "個", "粒", "回分"],
        "min_reviews": 10, "range": (10, 3000),
        "ng": ["ケース", "ボトル", "ホルダー"],
    },
    {
        "slug": "cat-litter",
        "title": "猫砂 1Lあたり単価ランキング",
        "keyword": "猫砂",
        "unit": "L", "base": "L", "per_text": "1Lあたり",
        "words": {"L": 1, "l": 1, "リットル": 1},
        "min_reviews": 10, "range": (3, 300),
        "ng": ["トイレ本体", "システムトイレ", "スコップ", "マット", "シート"],
    },
    {
        "slug": "baby-wipes",
        "title": "おしりふき 1枚あたり単価ランキング",
        "keyword": "おしりふき",
        "unit": "枚", "base": "枚",
        "words": ["枚入り", "枚入", "枚"],
        "min_reviews": 10, "range": (50, 10000),
        "ng": ["ケース", "ふた", "フタ", "ウォーマー"],
    },
    {
        "slug": "aa-battery",
        "title": "単3形 乾電池 1本あたり単価ランキング",
        "keyword": "単3 乾電池",
        "unit": "本", "base": "本",
        "words": ["本入り", "本入", "本パック", "本"],
        "min_reviews": 10, "range": (4, 500),
        "must": ["電池"],
        "ng": ["充電", "ニッケル水素", "エネループ", "単4", "単1", "単2", "ケース", "ライト", "LED", "電池式"],
    },
    {
        "slug": "protein",
        "title": "プロテイン 100gあたり単価ランキング",
        "keyword": "プロテイン 1kg",
        "unit": "100g", "base": "g", "per": 100, "per_text": "100gあたり",
        "words": {"kg": 1000, "g": 1},
        "min_reviews": 10, "range": (300, 10000),
        "must": ["プロテイン"],
        "ng": ["シェイカー", "バー", "サンプル", "お試し", "ドリンク", "ml", "クッキー", "大豆ミート", "黒豆", "黒千石", "おから"],
    },
    {
        "slug": "water-2l",
        "title": "ミネラルウォーター 2L 1本あたり単価ランキング",
        "keyword": "ミネラルウォーター 2L",
        "unit": "本", "base": "本",
        "words": ["本入り", "本入", "本"],
        "min_reviews": 10, "range": (6, 200),
        "ng": ["500ml", "550ml", "サーバー", "ボトル用"],
    },
    {
        "slug": "sparkling-water-500ml",
        "title": "炭酸水 500ml 1本あたり単価ランキング",
        "keyword": "炭酸水 500ml",
        "unit": "本", "base": "本",
        "words": ["本入り", "本入", "本"],
        "min_reviews": 10, "range": (12, 300),
        "must": ["炭酸"],
        "ng": ["1L", "1000ml", "2L", "メーカー", "ガスシリンダー", "ソーダストリーム"],
    },
    {
        "slug": "hand-soap-refill",
        "title": "ハンドソープ 詰め替え 100mlあたり単価ランキング",
        "keyword": "ハンドソープ 詰め替え",
        "keywords": ["ハンドソープ 詰め替え 大容量", "キレイキレイ 詰め替え", "ビオレu 泡ハンドソープ 詰め替え", "ミューズ 詰め替え"],
        "unit": "100ml", "base": "ml", "per": 100, "per_text": "100mlあたり",
        "words": ML,
        "min_reviews": 10, "range": (200, 20000),
        "must": REFILL,
        "ng": ["ディスペンサー", "オート", "自動", "本体", "ポンプ付", "ボディソープ", "食器"],
    },
    {
        "slug": "dish-soap-refill",
        "title": "食器用洗剤 詰め替え 100mlあたり単価ランキング",
        "keyword": "食器用洗剤 詰め替え",
        "keywords": ["食器用洗剤 詰め替え 大容量", "ジョイ 詰め替え", "キュキュット 詰め替え", "チャーミー 詰め替え"],
        "unit": "100ml", "base": "ml", "per": 100, "per_text": "100mlあたり",
        "words": ML,
        "min_reviews": 10, "range": (200, 20000),
        "must": REFILL,
        "ng": ["食洗機", "タブレット", "スポンジ", "ボトル", "ディスペンサー", "洗濯", "ペット用"],
    },
    {
        "slug": "body-soap-refill",
        "title": "ボディソープ 詰め替え 100mlあたり単価ランキング",
        "keyword": "ボディソープ 詰め替え",
        "keywords": ["ボディソープ 詰め替え 大容量", "ビオレu 詰め替え", "ダヴ ボディウォッシュ 詰め替え", "ナイーブ 詰め替え"],
        "unit": "100ml", "base": "ml", "per": 100, "per_text": "100mlあたり",
        "words": ML,
        "min_reviews": 10, "range": (200, 20000),
        "must": REFILL,
        "ng": ["本体", "ポンプ", "シャンプー", "ボトル", "ディスペンサー", "ハンドソープ"],
    },
    {
        "slug": "softener-refill",
        "title": "柔軟剤 詰め替え 100mlあたり単価ランキング",
        "keyword": "柔軟剤 詰め替え",
        "keywords": ["柔軟剤 詰め替え 大容量", "レノア 詰め替え", "ソフラン 詰め替え", "ハミング 詰め替え"],
        "unit": "100ml", "base": "ml", "per": 100, "per_text": "100mlあたり",
        "words": ML,
        "min_reviews": 10, "range": (300, 30000),
        "must": REFILL,
        "ng": ["本体", "ボトル", "ビーズ", "シート", "ミスト"],
    },
    {
        "slug": "disinfect-wipes",
        "title": "除菌ウェットシート 1枚あたり単価ランキング",
        "keyword": "除菌 ウェットシート",
        "unit": "枚", "base": "枚",
        "words": ["枚入り", "枚入", "枚"],
        "min_reviews": 10, "range": (30, 10000),
        "ng": ["ケース", "フタ", "ふた", "おしりふき", "トイレ", "フローリング", "ワイパー"],
    },
    {
        "slug": "cotton-swab",
        "title": "綿棒 1本あたり単価ランキング",
        "keyword": "綿棒",
        "unit": "本", "base": "本", "per_text": "1本あたり",
        "words": ["本入り", "本入", "本"],
        "min_reviews": 10, "range": (100, 20000),
        "ng": ["ケース", "スタンド", "耳かき", "イヤースコープ", "カメラ"],
    },
    {
        "slug": "rice",
        "title": "お米 1kgあたり単価ランキング",
        "keyword": "お米 5kg",
        "keywords": ["お米 5kg", "お米 10kg", "お米 20kg", "無洗米 5kg"],
        "unit": "kg", "base": "kg", "per_text": "1kgあたり",
        "words": {"kg": 1, "キロ": 1},
        "min_reviews": 10, "range": (2, 60),
        "must": ["米"],
        "ng": ["もち米", "米粉", "米ぬか", "パックご飯", "レトルト", "米びつ", "ライスストッカー", "精米機", "玄米茶", "米麹", "酒"],
    },
    {
        "slug": "cat-food-dry",
        "title": "キャットフード ドライ 100gあたり単価ランキング",
        "keyword": "キャットフード ドライ",
        "keywords": ["キャットフード ドライ 大容量", "カルカン ドライ", "ピュリナワン キャット", "銀のスプーン ドライ", "メディファス", "ロイヤルカナン 猫"],
        "unit": "100g", "base": "g", "per": 100, "per_text": "100gあたり",
        "words": {"kg": 1000, "g": 1},
        "min_reviews": 10, "range": (500, 20000),
        "must": ["キャットフード", "猫", "ねこ", "キャット"],
        "ng": ["ウェット", "パウチ", "缶", "おやつ", "ちゅ～る", "ちゅーる", "ふりかけ", "トッピング", "ドッグ", "犬"],
    },
    {
        "slug": "dog-food-dry",
        "title": "ドッグフード ドライ 100gあたり単価ランキング",
        "keyword": "ドッグフード ドライ",
        "keywords": ["ドッグフード ドライ 大容量", "ビタワン", "ペディグリー ドライ", "ピュリナワン ドッグ", "サイエンスダイエット 犬", "ロイヤルカナン 犬"],
        "unit": "100g", "base": "g", "per": 100, "per_text": "100gあたり",
        "words": {"kg": 1000, "g": 1},
        "min_reviews": 10, "range": (500, 20000),
        "must": ["ドッグフード", "犬", "いぬ", "ドッグ"],
        "ng": ["ウェット", "パウチ", "缶", "おやつ", "ジャーキー", "ふりかけ", "トッピング", "キャット", "猫"],
    },
    {
        "slug": "shampoo-refill",
        "title": "シャンプー 詰め替え 100mlあたり単価ランキング",
        "keyword": "シャンプー 詰め替え",
        "keywords": ["シャンプー 詰め替え 大容量", "パンテーン 詰め替え", "TSUBAKI シャンプー 詰め替え", "メリット シャンプー 詰め替え"],
        "unit": "100ml", "base": "ml", "per": 100, "per_text": "100mlあたり",
        "words": ML,
        "min_reviews": 10, "range": (200, 20000),
        "must": REFILL,
        "ng": ["コンディショナー", "トリートメント", "リンス", "ボディ", "ペット", "犬", "猫", "ドライ", "ボトル", "ディスペンサー", "容器"],
    },
    {
        "slug": "toothpaste",
        "title": "歯磨き粉 100gあたり単価ランキング",
        "keyword": "歯磨き粉",
        "keywords": ["歯磨き粉 まとめ買い", "クリニカ 歯磨き粉", "シュミテクト", "クリアクリーン 歯磨き粉", "システマ ハミガキ", "生葉 歯磨き"],
        "unit": "100g", "base": "g", "per": 100, "per_text": "100gあたり",
        "words": {"g": 1},
        "min_reviews": 10, "range": (50, 5000),
        "must": ["歯磨", "歯みがき", "ハミガキ", "はみがき"],
        "ng": ["歯ブラシ", "マウスウォッシュ", "洗口液", "フロス", "犬", "猫", "ペット", "シート"],
    },
    {
        "slug": "liquid-laundry-refill",
        "title": "液体洗濯洗剤 詰め替え 100gあたり単価ランキング",
        "keyword": "洗濯洗剤 液体 詰め替え",
        "keywords": ["洗濯洗剤 液体 詰め替え 大容量", "アタック 詰め替え", "アリエール 詰め替え", "トップ スーパーナノックス 詰め替え"],
        "unit": "100g", "base": "g", "per": 100, "per_text": "100gあたり",
        "words": {"kg": 1000, "g": 1},
        "min_reviews": 10, "range": (300, 20000),
        "must": REFILL,
        "ng": ["ジェルボール", "柔軟剤", "漂白", "粉末", "おしゃれ着", "ボトル"],
    },
    {
        "slug": "toilet-paper-double",
        "title": "トイレットペーパー ダブル 100mあたり単価ランキング",
        "keyword": "トイレットペーパー ダブル",
        "keywords": ["トイレットペーパー ダブル まとめ買い", "トイレットペーパー ダブル 長持ち", "エリエール トイレットペーパー ダブル", "スコッティ ダブル"],
        "unit": "100m", "base": "m", "per": 100, "per_text": "100mあたり",
        "parser": TP_PARSER,
        "min_reviews": 10,
        "must": ["ダブル"],
        "ng": ["シングル", "ホルダー", "収納", "ラック", "キッチンペーパー", "ティッシュ"],
    },
    {
        "slug": "toilet-paper-single",
        "title": "トイレットペーパー シングル 100mあたり単価ランキング",
        "keyword": "トイレットペーパー シングル",
        "keywords": ["トイレットペーパー シングル まとめ買い", "トイレットペーパー シングル 長持ち", "エリエール トイレットペーパー シングル", "スコッティ シングル"],
        "unit": "100m", "base": "m", "per": 100, "per_text": "100mあたり",
        "parser": TP_PARSER,
        "min_reviews": 10,
        "must": ["シングル"],
        "ng": ["ダブル", "ホルダー", "収納", "ラック", "キッチンペーパー", "ティッシュ"],
    },
    {
        "slug": "tissue",
        "title": "ティッシュペーパー 100組あたり単価ランキング",
        "keyword": "ティッシュペーパー",
        "keywords": ["ティッシュペーパー まとめ買い", "ティッシュ 箱 ケース", "エリエール ティッシュ", "スコッティ ティッシュ", "ネピア ティッシュ"],
        "unit": "100組", "base": "組", "per": 100, "per_text": "100組あたり",
        "parser": {"size": r"(\d{2,3})\s*組", "pack": r"箱|個", "lo": 300, "hi": 100000},
        "min_reviews": 10,
        "must": ["ティッシュ"],
        "ng": ["ウェット", "ポケット", "ケース付", "カバー", "トイレット", "キッチン", "除菌"],
    },
]

# 楽天以外の提携案件（A8）。ページ下部の紹介枠に出す。link はA8の広告コードそのまま（クリック計測の画像を含む）
PROMOS = {
    "dog-food-dry": {
        "title": "原材料にこだわるなら：プレミアムドッグフード",
        "lead": "上のランキングは一般的なドッグフードの単価順です。グレインフリーや生肉使用など原材料にこだわる場合はプレミアムフードという選択肢もあります。100gあたりは上のフードより高めになるので、定期便の割引も含めて公式サイトで確認してください。",
        "items": [
            {"name": "モグワン", "desc": "チキン生肉とサーモンを使ったグレインフリーのドッグフード",
             "link": '<a href="https://px.a8.net/svt/ejp?a8mat=4BGBN4+8OKLDE+3J8+1BNJ9E" rel="sponsored nofollow noopener" target="_blank">モグワンの公式サイトを見る</a>'
                     '<img border="0" width="1" height="1" src="https://www19.a8.net/0.gif?a8mat=4BGBN4+8OKLDE+3J8+1BNJ9E" alt="">'},
            {"name": "カナガン サーモン", "desc": "サーモンを主原料にしたグレインフリーのドッグフード",
             "link": '<a href="https://px.a8.net/svt/ejp?a8mat=4BGBN4+8PRGKY+3J8+64KO76" rel="sponsored nofollow noopener" target="_blank">カナガン サーモンの公式サイトを見る</a>'
                     '<img border="0" width="1" height="1" src="https://www10.a8.net/0.gif?a8mat=4BGBN4+8PRGKY+3J8+64KO76" alt="">'},
        ],
    },
    "cat-food-dry": {
        "title": "原材料にこだわるなら：プレミアムキャットフード",
        "lead": "上のランキングは一般的なキャットフードの単価順です。グレインフリーやヒューマングレードの原材料にこだわる場合はプレミアムフードという選択肢もあります。100gあたりは上のフードより高めになるので、定期便の割引も含めて公式サイトで確認してください。",
        "items": [
            {"name": "モグニャン", "desc": "白身魚を中心にしたグレインフリーのキャットフード（ヒューマングレード、遺伝子組み換え原材料不使用）",
             "link": '<a href="https://px.a8.net/svt/ejp?a8mat=4BGBN4+8VPSMQ+3J8+1TIJEP" rel="sponsored nofollow noopener" target="_blank">'
                     '<img border="0" width="300" height="250" alt="モグニャン" style="max-width:100%;height:auto" loading="lazy" '
                     'src="https://www22.a8.net/svt/bgt?aid=261102064537&amp;wid=001&amp;eno=01&amp;mid=s00000000458011004000&amp;mc=1"><br>モグニャンの公式サイトを見る</a>'
                     '<img border="0" width="1" height="1" src="https://www10.a8.net/0.gif?a8mat=4BGBN4+8VPSMQ+3J8+1TIJEP" alt="">'},
            {"name": "カナガン デンタルキャットフード", "desc": "歯の健康に配慮した成分を配合したグレインフリーのキャットフード",
             "link": '<a href="https://px.a8.net/svt/ejp?a8mat=4BGBN4+9Q2WHE+3J8+3SXWUQ" rel="sponsored nofollow noopener" target="_blank">カナガン デンタルキャットフードの公式サイトを見る</a>'
                     '<img border="0" width="1" height="1" src="https://www19.a8.net/0.gif?a8mat=4BGBN4+9Q2WHE+3J8+3SXWUQ" alt="">'},
        ],
    },
    "water-2l": {
        "title": "毎月たくさん飲むなら：ウォーターサーバー",
        "lead": "重いペットボトルを運ぶ手間がなくなり、冷水・温水がすぐ使えるのがウォーターサーバーの利点です。費用はボトル代に電気代や配送条件が加わるので、上のペットボトルの1本あたり単価と比べながら、毎月飲む量で検討してください。",
        "items": [
            {"name": "ワンウェイウォーター", "desc": "サーバーのレンタル料が無料のウォーターサーバー",
             "link": '<a href="https://px.a8.net/svt/ejp?a8mat=4BGBN4+8G8IWI+1MQG+5Z6WY" rel="sponsored nofollow noopener" target="_blank">ワンウェイウォーターの公式サイトを見る</a>'
                     '<img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4BGBN4+8G8IWI+1MQG+5Z6WY" alt="">'},
        ],
    },
}

# 各ページ下部の「選び方のポイント」
TIPS = {
    "dishwasher-tablet": ["ほとんどのタブレットは1回1個。大容量の袋ほど1回あたりが安くなりやすい", "オールインワンやジェル入りは、すすぎ剤や油汚れ対策の成分が入るぶん単価が高め", "海外製の食洗機（ミーレなど）は、メーカー指定の洗剤を確認してから選ぶ"],
    "garbage-bag-45l": ["自治体指定のゴミ袋がある地域では使えないので、先に確認する", "厚さ（0.015mm、0.03mmなど）が薄いほど安いが、生ゴミや角のあるゴミには厚手が安心", "半透明・透明・黒は自治体ルールで決まっていることが多い"],
    "pet-sheet": ["レギュラーは小型犬・猫向けの標準サイズ。犬の体格に合わないと漏れやすい", "薄型は安くて収納しやすいが、交換回数が増えると1日あたりのコストは上がる", "1回で替えるか、数回使うかで最適な厚みが変わる"],
    "mask": ["1枚あたりは大箱・まとめ買いが安い", "子供用・小さめ・大きめなどサイズ違いが混ざるので、商品ページでサイズを確認する", "日本製や個包装は単価が高め。持ち歩きが多いなら個包装が便利"],
    "sonicare-brush-head": ["型番（HX6014=スタンダード、HX6024=ミニ、HX6064=ダイヤモンドクリーンなど）で形が決まる", "互換品は純正の数分の1の値段だが、毛の品質や耐久性は製品ごとに差がある", "交換の目安は約3か月。年間の本数から1本あたりの差を考えると選びやすい"],
    "oralb-brush-head": ["EB17・EB20・EB50など型番でブラシの種類が決まる。手持ちの本体に合うか確認する", "互換品は純正よりかなり安いが、毛の硬さや品質には差がある", "交換の目安は約3か月"],
    "coffee-beans": ["大袋は安いが、開封後は風味が落ちやすい。冷凍保存すると長持ちする", "「豆のまま」と「粉」がある。ミルがなければ粉を選ぶ", "福袋やセットは1kgあたりが安い一方、好みの銘柄が入るとは限らない"],
    "laundry-gelball": ["基本は1回1個。洗濯物の量が多い日に2個使うと単価は倍になる", "つめかえ用の大袋ほど1回あたりが安い", "部屋干し用・柔軟剤入りなど機能で値段が変わる"],
    "cat-litter": ["紙・木・おから・ベントナイト（鉱物）で、固まり方や処分方法が違う", "ここでは容量（L）で比べている。重さ（kg）表記の商品は含まれない", "トイレに流せるタイプかどうかは商品ごとに確認する"],
    "baby-wipes": ["厚手は1枚で拭ける範囲が広く、薄手は単価が安い", "水99%などの成分や、手口ふき兼用かどうかで選ぶ", "ケース買い（12個入りなど）が1枚あたり最安になりやすい"],
    "aa-battery": ["アルカリ乾電池はリモコン・時計など幅広く使える定番", "使用推奨期限（10年など）が長いものは備蓄にも向く", "消費が多い機器なら充電池も検討する（このページは使い切りの乾電池のみ）"],
    "protein": ["ホエイ・ソイ・カゼインで吸収の速さや原料が違う", "100gあたりの価格だけでなく、たんぱく質の含有率も商品ページで確認する", "初めての味は小さい袋で試してから大袋にすると失敗しにくい"],
    "water-2l": ["軟水は日本人になじみやすく、硬水はミネラルが多い", "ケース（6本・9本・12本）単位が安い。重いので送料込みかどうかも見る", "備蓄用なら保存期間の長い商品を選ぶ"],
    "toilet-paper-double": ["ダブルは2枚重ねなので、同じ長さでもシングルより紙の量が多い。ここではダブル同士で比べている", "1.5倍巻・2倍巻などの長巻きは交換の手間が減り、収納場所も節約できる", "芯なしタイプは長さが長いぶん、ホルダーに入るサイズか確認する"],
    "toilet-paper-single": ["シングルは1枚なので、ダブルより長く巻かれていて交換回数が少ない", "再生紙（古紙）100%は安く、パルプ100%はやわらかい傾向", "長巻き（1.5倍・2倍）は1mあたりが安くなりやすい"],
    "tissue": ["「組」は2枚1組の数。150組と200組では1箱で使える量が違うので、100組あたりで比べている", "保湿ティッシュ（鼻セレブなど）は単価が高いが、鼻をよくかむ時期にはやさしい", "5箱パック×数パックのケース買いが最安になりやすい"],
    "rice": ["銘柄米・ブレンド米・複数原料米で価格が大きく違う。ブレンド米は安いが産地や品種は混ざる", "10kg・20kgの大袋は1kgあたりが安いが、精米後は早めに食べきるのがおすすめ（夏は特に）", "無洗米は研ぐ手間と水が省けるぶん、少し高めのことが多い"],
    "cat-food-dry": ["総合栄養食かどうかを確認する（主食にするなら総合栄養食）", "子猫用・成猫用・シニア用など年齢で栄養バランスが違う", "大袋は割安だが、開封後は酸化しやすいので小分け包装が便利"],
    "dog-food-dry": ["総合栄養食かどうかを確認する（主食にするなら総合栄養食）", "小型犬用は粒が小さい。犬種や年齢に合ったものを選ぶ", "大袋は割安だが、開封後は湿気と酸化に注意。小分け包装だと鮮度を保ちやすい"],
    "shampoo-refill": ["詰め替えは本体ボトルより100mlあたりが安い。大容量パウチほど割安", "ノンシリコン・アミノ酸系などで洗い上がりが違う", "同じシリーズのコンディショナーと合わせると仕上がりがそろいやすい"],
    "toothpaste": ["フッ素濃度（1450ppmなど）は虫歯予防の目安。年齢によって推奨濃度が違う", "歯周病ケア・ホワイトニング・知覚過敏など目的で選ぶ", "まとめ買い（3本・5本セット）が100gあたり安くなりやすい"],
    "liquid-laundry-refill": ["濃縮タイプは1回の使用量が少ないので、100gあたりの価格だけで比べると割高に見えることがある", "超特大の詰め替えほど100gあたりが安い", "部屋干し・抗菌・すすぎ1回など、機能で価格帯が分かれる"],
    "hand-soap-refill": ["泡タイプと液体タイプで詰め替え先のボトルが違うので、手持ちのボトルに合うものを選ぶ", "大容量の詰め替え（1L以上）ほど100mlあたりが安い", "薬用（殺菌成分入り）かどうかで値段が変わる"],
    "dish-soap-refill": ["濃縮タイプは1回に使う量が少ないので、100mlあたりの値段だけでなく使用量も考える", "超特大の詰め替えは1回の購入額は高いが、単価は最安になりやすい", "手肌へのやさしさや除菌など、機能で価格帯が分かれる"],
    "body-soap-refill": ["詰め替えは本体ボトルより100mlあたりがかなり安い", "大容量パウチは開け口が大きいと詰め替えやすい", "肌が弱い人は無添加・弱酸性などの表示を確認する"],
    "softener-refill": ["濃縮タイプは1回あたりの使用量が少ないので、表示上の単価より割安になることがある", "香りの強さや持続時間で好みが分かれる。初めてなら小さい袋で試す", "部屋干し用・消臭重視など目的で選ぶ"],
    "disinfect-wipes": ["アルコールタイプとノンアルコールタイプがある。手肌用か、物の掃除用かで選ぶ", "大判・厚手は1枚で拭ける範囲が広いが、枚数あたりは高め", "詰め替え用やまとめ買いが1枚あたり最安になりやすい"],
    "cotton-swab": ["紙軸とプラスチック軸があり、紙軸は環境にやさしい", "細軸・ベビー用はサイズが小さいので、用途に合わせて選ぶ", "大容量（1000本以上）はまとめ買いで1本1円以下になることも多い"],
    "sparkling-water-500ml": ["強炭酸・微炭酸で飲みごたえが違う", "24本ケースが1本あたり最安になりやすい", "ラベルレスは分別の手間が少なく、価格も安め"],
}


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
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=20) as r:
                    data = json.load(r)
                break
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < 2:  # 回数制限は少し待てば通る
                    time.sleep(3)
                    continue
                # GitHub Actions の注釈に出してログイン無しで原因を読めるようにする
                body = " ".join(e.read()[:300].decode("utf-8", "replace").split())
                site = os.environ.get("SITE_URL", "")
                raise RuntimeError(f"楽天API {e.code}: {body} / SITE_URL={len(site)}文字 / "
                                   f"ID={len(os.environ.get('RAKUTEN_APP_ID', ''))}文字")
            except (urllib.error.URLError, TimeoutError) as e:
                if attempt == 2:
                    raise RuntimeError(f"楽天APIに接続できません: {e}")
                time.sleep(5)
        items += data.get("Items", [])
        time.sleep(1.1)  # 1秒1リクエスト制限
    return items


ZEN = str.maketrans("０１２３４５６７８９×Ｘｘ", "0123456789xxx")


def parse_product(name, size, pack, lo, hi):
    """1個あたりの量（size）×個数（pack）で総量を出す。
    例 トイレットペーパー '30m 12ロール×4パック' -> 1440、ティッシュ '160組 5箱×12パック' -> 9600
    size, pack は正規表現（数字を1つ目のグループで取る）。読めなければ None"""
    s = name.translate(ZEN).replace(",", "")
    if re.search(r"選べる|選択|単品.*セット|セット.*単品|\d\s*[~～〜]\s*\d|\d\s*[・/]\s*\d+\s*(?:個|箱|ロール)", s):
        return None  # 「50・90個」のような選択式
    sizes = {float(x) for x in re.findall(size, s)}
    if len(sizes) != 1:  # 「シングル60m ダブル30m」のように複数あると価格との対応が分からない
        return None
    per = sizes.pop()
    # 個数の候補: 「12ロール」「12ロール×4パック」「5箱x12」→ 一番大きいものを総数とみなす
    cands, used_x = [], False
    for m in re.finditer(rf"(\d{{1,3}})\s*(?:{pack})(?:\s*[x*]\s*(\d{{1,2}}))?", s):
        cands.append(int(m.group(1)) * (int(m.group(2)) if m.group(2) else 1))
        used_x |= bool(m.group(2))
    if not cands:
        return None
    # 「80個 90個」のように掛け算の関係にない個数が並ぶのはサイズ違いの羅列
    plain = set(cands)
    if not used_x and len(plain) >= 2 and max(plain) not in {a * b for a in plain for b in plain}:
        return None
    n = max(cands)
    # 「12ロール 4パックセット」「(5箱) 3セット」のように別に書かれたセット数
    extra = re.search(r"(\d{1,2})\s*(?:パック|袋|ケース)?\s*セット", s)
    if extra and not used_x and n == min(cands) and int(extra.group(1)) > 1:
        n *= int(extra.group(1))
    total = per * n
    return total if lo <= total <= hi else None


def parse_count(name, words, lo=5, hi=3000):
    """商品名から総数量を推定。例: '60個入×3袋' -> 180、'500g×2袋' -> 1000。判定できなければ None
    words は語のリスト、または {語: 倍率}（例 {"kg": 1000, "g": 1}）"""
    if isinstance(words, list):
        words = {w: 1 for w in words}
    s = name.translate(ZEN).replace(",", "")
    # 「1袋～3袋 選べる」のようなバリエーション商品は価格と数量が対応しないので除外
    if re.search(r"選べる|選択|単品.*セット|セット.*単品|\d\s*[~～〜]\s*\d", s):
        return None
    w = "|".join(map(re.escape, sorted(words, key=len, reverse=True)))
    # 「3個セット」のセット数を拾わないよう、直後がセットの数字は除く。一番大きい量を内容量とみなす
    ms = [(float(m.group(1)) * words[m.group(2)], m)
          for m in re.finditer(rf"(\d{{1,4}}(?:\.\d{{1,2}})?)\s*({w})(?!\s*セット)", s)]
    if not ms:
        return None
    # セット数の候補: 「×3」「/箱×3」「3袋セット」「【3個セット】」「2ケース」
    # ただしジャンルの単位と同じ語（水なら「12本セット」）は合計数量なので、セット数ではなく量の候補に回す
    units = ["袋", "箱", "個", "本", "パック", "冊", "ケース"]
    own = [u for u in units if any(k.startswith(u) for k in words)]
    pack = "|".join(u for u in units if u not in own)
    ks_set = [int(x) for x in re.findall(rf"(\d{{1,2}})\s*(?:{pack})\s*(?:セット)?(?![入\d])", s)
              if re.search(rf"{x}\s*(?:{pack})\s*セット|{x}\s*ケース", s)]
    if own:
        top = max(v for v, _ in ms)
        for x in re.findall(rf"(\d{{1,4}})\s*(?:{'|'.join(own)})\s*セット", s):
            # 1袋の量より大きければ合計数量（12本セット）、小さければセット数（150個入りの3個セット）
            if float(x) > top:
                ms.append((float(x), None))
            else:
                ks_set.append(int(x))
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
        elif re.search(r"(?<![x*\d])\s*\d\s*(?:袋|箱|冊|パック|ケース)(?!\s*(?:入|セット))", s):
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
        if any(w in it["itemName"] for w in cat.get("ng", []) + NG_ALL):
            continue
        if cat.get("must") and not any(w in it["itemName"] for w in cat["must"]):
            continue
        if cat.get("parser"):  # 「ロール数×長さ」のように2つの数字を掛けるジャンル
            n = parse_product(it["itemName"], **cat["parser"])
        else:
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
            "rate": float(it.get("affiliateRate") or 0),
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


def short(c):
    """ナビ用の短い名前: 「ゴミ袋 45L 1枚あたり単価ランキング」→「ゴミ袋 45L」"""
    per = c.get("per_text", f"1{c['unit']}あたり")
    return c["title"].replace("単価ランキング", "").replace(per, "").strip()


def render(cat, rows, updated):
    e = html.escape
    per_text = cat.get('per_text', f"1{cat['unit']}あたり")
    tips = TIPS.get(cat["slug"], [])
    tips_html = ("<h2>選び方のポイント</h2><ul>" + "".join(f"<li>{e(t)}</li>" for t in tips) + "</ul>") if tips else ""
    promo = PROMOS.get(cat["slug"])
    if promo:  # link は自分で管理する広告コードなのでエスケープしない
        tips_html += (f"<section class=promo><p class=pr>PR</p><h2>{e(promo['title'])}</h2><p>{e(promo['lead'])}</p>"
                      + "".join(f"<div class=pi><b>{e(i['name'])}</b><span>{e(i['desc'])}</span>{i['link']}</div>"
                                for i in promo["items"]) + "</section>")
    trs = "".join(f"""
<tr><td class=n>{i}</td>
<td class=p><a href="{e(r['url'])}" rel="sponsored noopener" target=_blank>
<img src="{e(r['img'])}" alt="" loading=lazy><span>{e(r['name'][:70])}</span></a>
<small>{e(r['shop'])}{' ・送料無料' if r['free_ship'] else ' ・送料別'}{f" ・同じ商品の出品ほか{r['others']}件（ここが最安）" if r.get('others') else ''}</small></td>
<td class=u><b>{r['unit_price']:.1f}円</b><small>/{cat['unit']}</small></td>
<td class=d>{r['price']:,}円<br><small>{r['count']:,.0f}{cat.get('base', cat['unit'] + '分')}</small></td>
<td class=d>★{r['rating']:.2f}<br><small>{r['reviews']:,}件</small></td></tr>"""
                  for i, r in enumerate(rows, 1))
    site = os.environ.get("SITE_URL", "https://ikkai-ikura.github.io/")
    url = f"{site}{cat['slug']}.html"
    desc = f"{cat['keyword']}を楽天の価格と内容量から{per_text}の値段に換算して毎日自動で比較。同じ商品は最安の出品だけを掲載。"
    # 検索エンジン向け構造化データ（パンくず＋ランキングの並び）
    ld = json.dumps([
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "TANKA", "item": site},
            {"@type": "ListItem", "position": 2, "name": cat["title"], "item": url}]},
        {"@context": "https://schema.org", "@type": "ItemList", "name": cat["title"], "itemListElement": [
            {"@type": "ListItem", "position": i, "name": r["name"][:80]} for i, r in enumerate(rows[:10], 1)]},
    ], ensure_ascii=False).replace("</", "<\\/")
    others = "".join(f'<a href="{c["slug"]}.html">{e(short(c))}</a>'
                     for c in CATEGORIES if c["slug"] != cat["slug"])
    nav = f'<nav class=oth><h2>ほかのジャンル</h2>{others}</nav><p class=pr><a href="./">トップへ戻る</a> ・ <a href="about.html">このサイトについて</a></p>'
    return f"""<!doctype html><html lang=ja><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>{e(cat['title'])}｜TANKA</title>
<meta name=description content="{e(desc)}">
<link rel=canonical href="{url}">
<meta property=og:title content="{e(cat['title'])}"><meta property=og:description content="{e(desc)}">
<meta property=og:url content="{url}"><meta property=og:type content=article><meta property=og:site_name content="TANKA">
<meta property=og:image content="{e(rows[0]['img'] if rows else '')}"><meta name=twitter:card content=summary>
<script type="application/ld+json">{ld}</script>
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
.oth{{margin-top:24px}} .oth a{{display:inline-block;margin:0 6px 6px 0;padding:4px 10px;border:1px solid var(--line);border-radius:999px;color:inherit;text-decoration:none;font-size:.85rem}}
.bc{{font-size:.8rem;color:var(--mut)}} .bc a{{color:inherit}}
.promo{{margin-top:24px;padding:12px 14px;border:1px solid var(--line);border-radius:8px}} .promo h2{{margin:.2em 0}} .promo .pr{{margin:0}}
.pi{{display:grid;gap:2px;padding:8px 0;border-top:1px dashed var(--line)}} .pi span{{color:var(--mut);font-size:.85rem}} .pi a{{color:var(--acc);font-weight:600}}
</style></head><body><main>
<p class=pr>PR：このページは楽天アフィリエイトを利用しています</p>
<p class=bc><a href="./">TANKA</a> › {e(cat['title'])}</p>
<h1>{e(cat['title'])}</h1>
<p>楽天市場の商品を「価格 ÷ 内容量」で{per_text}に換算し、安い順に並べています。同じ商品はショップ違い・袋数違いをまとめ、1回あたり最安の出品だけを載せています。毎日自動更新（最終更新 {updated}）。価格は更新時点のもので、送料別の商品は送料を含みません。</p>
<table>{trs}</table>
{tips_html}
<p class=pr>内容量は商品名から自動で読み取っています。セット数の読み違いがある場合があるので、購入前に商品ページで確認してください。</p>
{nav}
</main></body></html>"""


def render_about():
    return """<!doctype html><html lang=ja><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>このサイトについて｜TANKA</title>
<meta name=description content="TANKAの運営方針・価格の計算方法・広告についての説明です。">
<style>:root{--bg:#fff;--fg:#1d1d1f;--mut:#6e6e73}
@media(prefers-color-scheme:dark){:root{--bg:#111;--fg:#f2f2f7;--mut:#a1a1a6}a{color:#8ab4ff}}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.8 system-ui,sans-serif}main{max-width:720px;margin:auto;padding:16px}
h2{font-size:1.1rem;margin-top:1.6em}.mut{color:var(--mut);font-size:.85rem}</style></head><body><main>
<p class=mut><a href="./">TANKA</a> › このサイトについて</p>
<h1>このサイトについて</h1>
<p>TANKAは、日用品・消耗品を「1回あたり」「1枚あたり」「100gあたり」などの単価で比べるサイトです。大容量やまとめ買いの商品は総額だけでは割安かどうか分かりにくいため、内容量で割った値段で並べています。</p>
<h2>価格の計算方法</h2>
<ul><li>楽天市場の商品検索APIから、価格・商品名・レビュー件数を毎日1回自動で取得しています。</li>
<li>内容量は商品名から自動で読み取り、「価格 ÷ 内容量」で単価を計算しています。</li>
<li>同じ商品がショップ違い・袋数違いで複数ある場合は、単価が最も安い出品だけを掲載しています。</li>
<li>レビューが少ない商品、内容量が読み取れない商品、サイズを選ぶ形式で価格と内容量が対応しない商品は掲載していません。</li>
<li>価格は取得時点のものです。送料別の商品は送料を含みません。購入前に必ず商品ページで価格と内容量をご確認ください。</li></ul>
<h2>広告について</h2>
<p>このサイトは楽天アフィリエイトを利用しています。商品リンクから購入されると、運営者に紹介料が支払われることがあります。紹介料の有無や料率によって掲載順を変えることはなく、並び順は単価のみで決めています。</p>
<h2>お問い合わせ</h2>
<p>掲載内容の誤り（内容量の読み違いなど）のご指摘は、<a href="https://github.com/ikkai-ikura/ikkai-ikura.github.io/issues" rel="noopener">こちら</a>からお知らせください。</p>
<p class=mut><a href="./">トップへ戻る</a></p>
</main></body></html>"""


GROUPS = [
    ("laundry", "洗濯・キッチン", ["dishwasher-tablet", "dish-soap-refill", "laundry-gelball", "liquid-laundry-refill", "softener-refill"]),
    ("paper", "紙・生活用品", ["toilet-paper-double", "toilet-paper-single", "tissue", "garbage-bag-45l", "mask",
                          "disinfect-wipes", "cotton-swab", "baby-wipes", "aa-battery"]),
    ("care", "バス・ケア", ["hand-soap-refill", "body-soap-refill", "shampoo-refill", "toothpaste",
                         "sonicare-brush-head", "oralb-brush-head"]),
    ("pet", "ペット", ["dog-food-dry", "cat-food-dry", "pet-sheet", "cat-litter"]),
    ("food", "食品・飲料", ["rice", "coffee-beans", "protein", "water-2l", "sparkling-water-500ml"]),
]


def render_index(summary, updated):
    e = html.escape
    by_slug = {c["slug"]: c for c in CATEGORIES}
    grouped = {sl for _, _, sls in GROUPS for sl in sls}
    groups = GROUPS + ([("other", "その他", [c["slug"] for c in CATEGORIES if c["slug"] not in grouped])]
                       if any(c["slug"] not in grouped for c in CATEGORIES) else [])

    def card(c):
        s = summary.get(c["slug"])
        best = (f"<p class=b>最安 <b>{s['unit_price']:.1f}円</b><small>/{e(c['unit'])}</small></p>"
                f"<p class=s>{e(s['name'])}</p>") if s else "<p class=s>集計中</p>"
        img = f"<img src='{e(s['img'])}' alt='' loading=lazy>" if s and s.get("img") else ""
        # 検索用の語: ジャンル名・検索キーワード・ブランド名
        words = " ".join([short(c), c["keyword"]] + c.get("keywords", []) + list(c.get("brands", {})))
        return (f"<a class=card href='{c['slug']}.html' data-k='{e(words.lower())}'>{img}"
                f"<div><h3>{e(short(c))}</h3>{best}</div></a>")

    chips = "".join(f"<a href='#{gid}'>{e(label)}</a>" for gid, label, _ in groups)
    sections = "".join(
        f"<section class=grp id='{gid}'><h2>{e(label)}</h2><div class=grid>"
        + "".join(card(by_slug[sl]) for sl in sls if sl in by_slug) + "</div></section>"
        for gid, label, sls in groups)
    return f"""<!doctype html><html lang=ja><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>TANKA｜日用品の1回あたり単価比較</title>
<meta name="google-site-verification" content="A-JyA2Us3KYpkTLgjEMxZSKUwAAWLqE7rWFsJdlSn9o">
<meta name=description content="洗剤・トイレットペーパー・ペットフード・お米など日用品{len(CATEGORIES)}ジャンルを、楽天の価格と内容量から1回あたりの値段に換算して毎日自動で比較。">
<style>
:root{{--bg:#f5f5f7;--card:#fff;--fg:#1d1d1f;--mut:#6e6e73;--acc:#bf0000;--line:#e5e5ea}}
@media(prefers-color-scheme:dark){{:root{{--bg:#111;--card:#1c1c1e;--fg:#f2f2f7;--mut:#a1a1a6;--acc:#ff6b6b;--line:#333}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.6 system-ui,sans-serif}}
main{{max-width:960px;margin:auto;padding:16px}} h1{{margin:.2em 0;font-size:1.6rem}}
.pr,.lead{{color:var(--mut)}} .pr{{font-size:.8rem}}
.bar{{position:sticky;top:0;z-index:5;background:var(--bg);padding:10px 0;border-bottom:1px solid var(--line);display:grid;gap:8px}}
.bar input{{font:inherit;padding:9px 12px;border:1px solid var(--line);border-radius:999px;background:var(--card);color:var(--fg);width:100%;box-sizing:border-box}}
.chips{{display:flex;gap:6px;overflow-x:auto;scrollbar-width:none}} .chips a{{flex:none;padding:4px 12px;border-radius:999px;border:1px solid var(--line);background:var(--card);color:inherit;text-decoration:none;font-size:.85rem}}
.chips a:hover{{border-color:var(--acc)}}
.grp{{scroll-margin-top:110px;margin-top:20px}} .grp h2{{font-size:1.05rem;margin:0 0 8px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:10px}}
.card{{display:flex;gap:12px;align-items:center;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px 12px;color:inherit;text-decoration:none}}
.card:hover,.card:focus-visible{{border-color:var(--acc)}} .card img{{width:56px;height:56px;object-fit:contain;flex:none;background:#fff;border-radius:8px}}
.card h3{{font-size:.95rem;margin:0}} .b{{margin:2px 0}} .b b{{color:var(--acc);font-size:1.1rem}}
.s{{margin:0;color:var(--mut);font-size:.72rem;line-height:1.4;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}} small{{color:var(--mut)}}
.none{{color:var(--mut);margin-top:16px}}
</style></head><body><main>
<p class=pr>PR：このサイトは楽天アフィリエイトを利用しています</p>
<h1>TANKA <span style="font-size:.9rem;font-weight:normal;color:var(--mut)">日用品の1回あたり単価比較</span></h1>
<p class=lead>日用品を「1回あたりの値段」で比べるサイトです。楽天市場の価格と内容量から自動で計算し、毎日更新しています（最終更新 {updated}）。</p>
<div class=bar><input id=q type=search placeholder="さがす（例：洗剤、猫、トイレットペーパー、キュキュット）" aria-label="ジャンルをさがす" autocomplete=off>
<nav class=chips aria-label="カテゴリ">{chips}</nav></div>
{sections}
<p class=none id=none hidden>見つかりませんでした。別の言葉でさがしてみてください。</p>
<p class=pr style="margin-top:24px"><a href="about.html">このサイトについて（計算方法・広告について）</a></p>
</main>
<script>
(function(){{
  var q=document.getElementById('q'), cards=[].slice.call(document.querySelectorAll('.card')), grps=[].slice.call(document.querySelectorAll('.grp'));
  function norm(t){{return t.toLowerCase().replace(/[ァ-ン]/g,function(c){{return String.fromCharCode(c.charCodeAt(0)-0x60)}})}}
  q.addEventListener('input',function(){{
    var w=norm(q.value.trim()), hit=0;
    cards.forEach(function(c){{var ok=!w||norm(c.dataset.k+' '+c.textContent).indexOf(w)>=0; c.hidden=!ok; if(ok)hit++;}});
    grps.forEach(function(g){{g.hidden=!g.querySelector('.card:not([hidden])');}});
    document.getElementById('none').hidden=hit>0;
  }});
}})();
</script></body></html>"""


def main():
    load_env()
    live = bool(os.environ.get("RAKUTEN_APP_ID"))
    OUT.mkdir(exist_ok=True)
    updated = datetime.now(JST).strftime("%Y-%m-%d %H:%M")
    failed = 0
    # トップページ用の「各ジャンルの最安」。取得に失敗したジャンルは前回の値を使う
    try:
        summary = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        summary = {}
    for cat in CATEGORIES:
        if live:
            try:
                # keywords があれば複数の検索語で集めて重複を除く（人気商品が検索上位に出ないジャンル向け）
                kws = cat.get("keywords") or [cat["keyword"]]
                items, seen_urls = [], set()
                for kw in kws:
                    for it in fetch(kw, pages=3 if len(kws) == 1 else 2):
                        if it.get("itemUrl") not in seen_urls:
                            seen_urls.add(it.get("itemUrl"))
                            items.append(it)
            except RuntimeError as e:
                # 1ジャンルの失敗で全体を止めない。前回のページはそのまま残る
                print(f"::warning::{cat['slug']}: {e}")
                failed += 1
                continue
        else:
            items = json.loads((ROOT / "sample_items.json").read_text(encoding="utf-8"))
        rows = rank(items, cat)
        (OUT / f"{cat['slug']}.html").write_text(render(cat, rows, updated), encoding="utf-8")
        if rows:
            top = rows[0]
            # 上位10件の「価格×報酬率」の中央値＝このジャンルで1件売れたときの報酬の目安
            fees = sorted(r["price"] * r["rate"] / 100 for r in rows[:10])
            summary[cat["slug"]] = {"unit_price": top["unit_price"], "name": top["name"][:40], "img": top["img"],
                                    "count": len(rows), "fee": round(fees[len(fees) // 2]),
                                    "rate": round(sorted(r["rate"] for r in rows[:10])[min(len(rows), 10) // 2], 1),
                                    "price": sorted(r["price"] for r in rows[:10])[min(len(rows), 10) // 2]}
        print(f"{cat['slug']}: 取得{len(items)}件 → 掲載{len(rows)}件 ({'本番' if live else 'サンプル'})")
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False), encoding="utf-8")
    (OUT / "index.html").write_text(render_index(summary, updated), encoding="utf-8")
    (OUT / "about.html").write_text(render_about(), encoding="utf-8")
    # 検索エンジン向けのサイトマップ
    site = os.environ.get("SITE_URL", "https://ikkai-ikura.github.io/")
    day = updated[:10]
    urls = [site, f"{site}about.html"] + [f"{site}{c['slug']}.html" for c in CATEGORIES]
    xml = "".join(f"<url><loc>{u}</loc><lastmod>{day}</lastmod></url>" for u in urls)
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>' + chr(10)
        + f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{xml}</urlset>' + chr(10), encoding="utf-8")
    (OUT / "robots.txt").write_text(chr(10).join(["User-agent: *", "Allow: /", f"Sitemap: {site}sitemap.xml", ""]),
                                    encoding="utf-8")
    if live and failed == len(CATEGORIES):
        print("::error::全ジャンルで取得に失敗しました")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
