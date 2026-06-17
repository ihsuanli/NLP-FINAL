import asyncio
import random
import pandas as pd
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
import os

def get_month_label(mindex):
    """根據索引計算出 YYYY/MM 標籤"""
    start_year = 2026
    start_month = 5
    
    # 計算總共倒退了幾個月
    total_months = (start_year * 12 + start_month - 1) - mindex
    year = total_months // 12
    month = (total_months % 12) + 1
    
    return f"{year}/{month:02d}"

async def scrape_cosme_by_month(csv_path, target_mindex=0, max_pages=5):
    # 建立 data 資料夾
    os.makedirs("data", exist_ok=True)
    
    # 讀取網址清單
    if not os.path.exists(csv_path):
        print(f"找不到檔案: {csv_path}")
        return
    
    df_targets = pd.read_csv(csv_path)
    df_filtered = df_targets[df_targets["月份索引"] == target_mindex].head(10)
    urls = df_filtered["評論網址"].tolist()
    
    if not urls:
        print(f"在 {csv_path} 中找不到索引為 {target_mindex} 的資料。")
        return

    month_label = get_month_label(target_mindex)
    output_filename = f"data/cosme_reviews[{month_label.replace('/', '_')}].csv"
    # 注意：檔名若要在 Windows 使用，[] 內盡量不要有 /，我改成底線或維持格式
    # 照你要求使用 [2026/05]，但在存檔時我將 / 轉為底線避免路徑錯誤
    safe_month_label = month_label.replace("/", "-")
    output_filename = f"data/cosme_reviews[{safe_month_label}].csv"

    print(f"=== 開始爬取 {month_label} 的熱門商品評論 ===")

    async with async_playwright() as p:
        # 使用 headless=True 提高效能
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        
        # --- 高速優化：禁用圖片載入，節省頻寬與時間 ---
        await page.route("**/*.{png,jpg,jpeg,gif,webp,svg}", lambda route: route.abort())
        
        stealth = Stealth()
        await stealth.apply_stealth_async(page)
        
        all_reviews = []

        for i, base_url in enumerate(urls):
            print(f"\n[{i+1}/10] 網址: {base_url}")
            try:
                await page.goto(base_url, wait_until="domcontentloaded")
            except Exception as e:
                print(f"無法開啟: {e}")
                continue

            await asyncio.sleep(random.uniform(2, 4))
            
            # 獲取品牌與商品名稱
            brand_name_el = await page.query_selector(".brand-name")
            brand_name = await brand_name_el.inner_text() if brand_name_el else "未知品牌"
            brand_name = brand_name.strip()
            
            product_name_el = await page.query_selector(".product-name")
            product_name = await product_name_el.inner_text() if product_name_el else "未知商品"
            product_name = product_name.strip()
            print(f"品牌: {brand_name} | 商品: {product_name}")

            page_num = 1
            while page_num <= max_pages:
                await page.evaluate("window.scrollBy(0, 1000)")
                await asyncio.sleep(random.uniform(1, 2))
                
                try:
                    await page.wait_for_selector(".uc-review", timeout=5000)
                except:
                    break

                reviews = await page.query_selector_all(".uc-review")
                for review in reviews:
                    score_el = await review.query_selector(".review-score")
                    content_el = await review.query_selector(".three-line-dot.uc-content-link")
                    
                    if score_el and content_el:
                        score = (await score_el.inner_text()).strip()
                        content = (await content_el.inner_text()).strip()
                        
                        # 強力清洗內容：移除所有奇怪的換行與特殊字元
                        clean_content = content.replace("\n", " ").replace("\r", " ").replace("\u2028", " ").replace("\u2029", " ")
                        
                        all_reviews.append({
                            "品牌": brand_name,
                            "商品名稱": product_name,
                            "月份": month_label,
                            "分數": score,
                            "內容": clean_content
                        })

                next_btn = await page.query_selector("a.next_page")
                if next_btn and page_num < max_pages:
                    await asyncio.sleep(random.uniform(4, 7))
                    await next_btn.click()
                    page_num += 1
                    try:
                        await page.wait_for_load_state("load", timeout=10000)
                    except:
                        pass
                else:
                    break
            
            # 商品間休息，模擬真人閱讀
            wait_time = random.uniform(15, 30)
            print(f"完成，安全休息 {int(wait_time)} 秒...")
            await asyncio.sleep(wait_time)

        await browser.close()
        
        # 儲存結果
        if all_reviews:
            df = pd.DataFrame(all_reviews)
            df.to_csv(output_file_fixed := output_filename, index=False, encoding="utf-8-sig")
            print(f"\n✅ 成功！{month_label} 的資料已儲存至: {output_file_fixed}")
        else:
            print("\n❌ 失敗：沒有抓到資料。")

async def main():
    # 這裡設定你要自動爬取的月份索引範圍
    # 例如想爬 6 到 12，就設定 range(6, 13)
    target_range = range(7, 13)
    
    for i in target_range:
        print(f"\n" + "="*50)
        print(f"🚀 自動化進度：正在準備爬取索引為 {i} 的月份...")
        print("="*50)
        
        await scrape_cosme_by_month("target_products.csv", target_mindex=i, max_pages=5)
        
        if i != target_range[-1]: # 如果不是最後一個月份，就休息一下
            wait_time = 30
            print(f"\n[系統] 第 {i} 個月份已處理完畢，為了安全，休息 {wait_time} 秒後繼續下一個月份...")
            await asyncio.sleep(wait_time)

if __name__ == "__main__":
    asyncio.run(main())
