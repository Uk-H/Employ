"""기업별 최신 뉴스/보도자료를 구글 뉴스 RSS에서 가져와 news.json에 저장합니다."""
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

MAX_ITEMS = 6  # 기업당 보여줄 기사 수

def fetch(keyword):
    query = urllib.parse.quote(f"{keyword} 보도자료 OR 채용")
    url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as res:
        root = ET.fromstring(res.read())
    items = []
    for item in root.iter("item"):
        pub = item.findtext("pubDate") or ""
        try:
            date = parsedate_to_datetime(pub).astimezone(timezone(timedelta(hours=9)))
            date_str = date.strftime("%Y-%m-%d")
        except Exception:
            date_str = ""
        items.append({
            "title": item.findtext("title") or "",
            "link": item.findtext("link") or "",
            "source": item.findtext("source") or "",
            "date": date_str,
        })
        if len(items) >= MAX_ITEMS:
            break
    return items

def main():
    with open("companies.json", encoding="utf-8") as f:
        companies = json.load(f)
    result = {}
    for c in companies:
        try:
            result[c["name"]] = fetch(c.get("newsKeyword", c["name"]))
        except Exception as e:
            print(f"[실패] {c['name']}: {e}")
            result[c["name"]] = []
    kst = datetime.now(timezone(timedelta(hours=9)))
    out = {"updated": kst.strftime("%Y-%m-%d %H:%M"), "news": result}
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("완료:", out["updated"])

if __name__ == "__main__":
    main()
