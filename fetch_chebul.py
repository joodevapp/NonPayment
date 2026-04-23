import requests
from bs4 import BeautifulSoup
import json
import os
import time
from datetime import datetime
 
BASE_URL = "https://www.moel.go.kr/info/defaulter/defaulterList.do"
 
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.moel.go.kr/info/defaulter/defaulterList.do",
    "Content-Type": "application/x-www-form-urlencoded"
}
 
def fetch_page(page):
    data = {
        "pageIndex": page,
        "searchWrnamNm": "",
        "searchAddrSido": "",
    }
    res = requests.post(BASE_URL, headers=HEADERS, data=data, timeout=10)
    res.encoding = 'utf-8'
    return res.text
 
def parse_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = []
 
    table = soup.find('table', {'class': 'brd_list'})
    if not table:
        table = soup.find('table')
    
    if not table:
        return results, 0
 
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 5:
            results.append({
                "no": cols[0].get_text(strip=True),
                "name": cols[1].get_text(strip=True),
                "age": cols[2].get_text(strip=True),
                "company": cols[3].get_text(strip=True),
                "address": cols[4].get_text(strip=True),
                "amount": cols[5].get_text(strip=True) if len(cols) > 5 else "",
                "period": cols[6].get_text(strip=True) if len(cols) > 6 else "",
            })
 
    # 전체 페이지 수 파악
    total_pages = 1
    pager = soup.find('div', {'class': 'pagination'})
    if not pager:
        pager = soup.find('div', {'id': 'paging'})
    if pager:
        page_links = pager.find_all('a')
        for link in page_links:
            try:
                p = int(link.get_text(strip=True))
                if p > total_pages:
                    total_pages = p
            except:
                pass
 
    return results, total_pages
 
all_data = []
print("1페이지 수집 중...")
html = fetch_page(1)
data, total_pages = parse_page(html)
all_data.extend(data)
print(f"전체 페이지 수: {total_pages}")
 
for page in range(2, total_pages + 1):
    print(f"{page}/{total_pages} 페이지 수집 중...")
    try:
        html = fetch_page(page)
        data, _ = parse_page(html)
        all_data.extend(data)
        time.sleep(0.5)
    except Exception as e:
        print(f"페이지 {page} 오류: {e}")
        continue
 
output = {
    "updated_at": datetime.now().strftime("%Y.%m.%d %H:%M"),
    "total": len(all_data),
    "data": all_data
}
 
os.makedirs("Result/chebul", exist_ok=True)
with open("Result/chebul/chebul.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
 
print(f"완료: 총 {len(all_data)}건 저장")
