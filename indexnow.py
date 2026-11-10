"""IndexNow: 更新したページをBing等の検索エンジンにすぐ知らせる（毎日のActionsの最後に実行）"""
import json, re, urllib.request
from pathlib import Path

KEY = "6192421a66bd4fffb27b0a7bca777d35"
HOST = "tankahikaku.com"
urls = re.findall(r"<loc>([^<]+)</loc>", Path("docs/sitemap.xml").read_text(encoding="utf-8"))
body = json.dumps({"host": HOST, "key": KEY, "keyLocation": f"https://{HOST}/{KEY}.txt", "urlList": urls[:10000]}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                             headers={"Content-Type": "application/json; charset=utf-8"})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print("IndexNow", r.status, len(urls), "URLs")
except Exception as ex:
    print("IndexNow 失敗（サイト更新には影響なし）:", ex)
