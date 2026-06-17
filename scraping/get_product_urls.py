import asyncio
import random
import pandas as pd
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def get_hot_new_products():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        stealth = Stealth()
        await stealth.apply_stealth_async(page)
        
        all_product_urls = []
        base_url = "https://www.cosme.net.tw"

        # 遍歷 mindex 0 到 12 (13個月份)
        for mindex in range(13):
            url = f"{base_url}/newhot?mindex={mindex}"
            print(f"\n>>> 正在抓取第 {mindex} 個月份的排行: {url}")
            
            try:
                await page.goto(url, wait_until="domcontentloaded")
                await asyncio.sleep(random.uniform(2, 4))
                
                # 抓取產品清單中的連結與名稱 (info-anchors product-info 下的 a)
                # 我們只取前 10 個
                product_items = await page.query_selector_all(".info-anchors.product-info")
                
                count = 0
                for item in product_items:
                    if count >= 10: break # 只要前十名
                    
                    link_el = await item.query_selector("a")
                    name_el = await item.query_selector(".title-product-name")
                    
                    if link_el and name_el:
                        partial_url = await link_el.get_attribute("href")
                        product_name = (await name_el.inner_text()).strip()
                        
                        # 格式化成評論頁網址
                        full_review_url = f"{base_url}{partial_url}/reviews"
                        
                        all_product_urls.append({
                            "月份索引": mindex,
                            "排名": count + 1,
                            "商品名稱": product_name,
                            "評論網址": full_review_url
                        })
                        count += 1
                
                print(f"成功取得 {count} 個商品網址。")

            except Exception as e:
                print(f"抓取索引 {mindex} 時發生錯誤: {e}")
            
            # 換月份之間休息一下
            await asyncio.sleep(random.uniform(3, 5))

        await browser.close()

        # 儲存結果
        if all_product_urls:
            df = pd.DataFrame(all_product_urls)
            output_file = "target_products.csv"
            df.to_csv(output_file, index=False, encoding="utf-8-sig")
            print(f"\n✅ 成功收集網址！總共 {len(all_product_urls)} 筆。")
            print(f"結果已儲存至: {output_file}")
            
            # 同時印出所有網址，方便你直接複製
            print("\n你可以直接將以下網址列表複製到 cosme_spider.py 使用：")
            urls_only = df["評論網址"].tolist()
            print(urls_only)
        else:
            print("\n❌ 失敗：未抓取到任何網址。")

if __name__ == "__main__":
    asyncio.run(get_hot_new_products())
