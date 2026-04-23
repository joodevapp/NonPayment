import json
import os
from datetime import datetime
from playwright.sync_api import sync_playwright
 
def fetch_all_chebul():
    all_data = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='ko-KR',
            timezone_id='Asia/Seoul'
        )
        page = context.new_page()
        
        print("1페이지 로딩 중...")
        page.goto('https://www.moel.go.kr/info/defaulter/defaulterList.do')
        page.wait_for_load_state('networkidle')
        
        # 전체 페이지 수 파악
        total_pages = 1
        try:
            pager = page.query_selector('.pagination') or page.query_selector('#paging')
            if pager:
                links = pager.query_selector_all('a')
                for link in links:
                    try:
                        p_num = int(link.inner_text().strip())
                        if p_num > total_pages:
                            total_pages = p_num
                    except:
                        pass
        except:
            pass
        
        print(f"전체 페이지 수: {total_pages}")
        
        def parse_current_page():
            rows = page.query_selector_all('table.brd_list tr, table tr')
            results = []
            for row in rows:
                cols = row.query_selector_all('td')
                if len(cols) >= 5:
                    try:
                        results.append({
                            "name": cols[1].inner_text().strip(),
                            "age": cols[2].inner_text().strip(),
                            "company": cols[3].inner_text().strip(),
                            "address": cols[4].inner_text().strip(),
                            "amount": cols[5].inner_text().strip() if len(cols) > 5 else "",
                            "period": cols[6].inner_text().strip() if len(cols) > 6 else "",
                        })
                    except:
                        pass
            return results
        
        # 1페이지 파싱
        data = parse_current_page()
        all_data.extend(data)
        print(f"1페이지: {len(data)}건")
        
        # 2페이지부터 순회
        for p_num in range(2, total_pages + 1):
            try:
                print(f"{p_num}페이지 로딩 중...")
                page.evaluate(f"fn_egov_link_page({p_num})")
                page.wait_for_load_state('networkidle')
                data = parse_current_page()
                all_data.extend(data)
                print(f"{p_num}페이지: {len(data)}건")
            except Exception as e:
                print(f"{p_num}페이지 오류: {e}")
                continue
        
        browser.close()
    
    return all_data
 
data = fetch_all_chebul()
 
output = {
    "updated_at": datetime.now().strftime("%Y.%m.%d %H:%M"),
    "total": len(data),
    "data": data
}
 
os.makedirs("Result/chebul", exist_ok=True)
with open("Result/chebul/chebul.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
 
print(f"완료: 총 {len(data)}건 저장")
