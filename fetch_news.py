import requests
import json
import os
from datetime import datetime
 
CLIENT_ID = os.environ['NAVER_CLIENT_ID']
CLIENT_SECRET = os.environ['NAVER_CLIENT_SECRET']
 
def fetch_news(query, display=10):
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }
    params = {
        "query": query,
        "display": display,
        "sort": "date"
    }
    res = requests.get(url, headers=headers, params=params)
    return res.json().get("items", [])
 
def clean(text):
    return text.replace("<b>", "").replace("</b>", "").replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&#39;", "'")
 
def deduplicate(items):
    seen = set()
    result = []
    for item in items:
        url = item.get("link", "")
        if url not in seen:
            seen.add(url)
            result.append(item)
    return result
 
all_news = fetch_news("임금체불", 20)
chebul_news = fetch_news("임금체불 사업장", 10)
labor_news = fetch_news("노동법 근로기준법", 10)
 
def format_items(items):
    result = []
    for item in items:
        result.append({
            "title": clean(item.get("title", "")),
            "url": item.get("link", ""),
            "source": item.get("originallink", ""),
            "date": item.get("pubDate", "")
        })
    return result
 
output = {
    "updated_at": datetime.now().strftime("%Y.%m.%d %H:%M"),
    "all": format_items(deduplicate(all_news)),
    "chebul": format_items(deduplicate(chebul_news)),
    "labor": format_items(deduplicate(labor_news))
}
 
with open("news.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
 
print(f"완료: {output['updated_at']}")
