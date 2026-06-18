# @cosme Product Review Dataset Description

This dataset consists of product reviews crawled and analyzed from @cosme Taiwan, a major local cosmetics and beauty community platform. Below is a detailed description of the dataset, including its data sources and inherent limitations.

## 1. Dataset Overview

*   **Total Volume:** A total of 7,855 review records.
*   **Time Range:** May 2025 to May 2026 (13 months in total, spanning a complete window from 2025 H2 to 2026 H1).
*   **Column Schema:** 
*   **Brand and Product Coverage:**
    *   **Unique Brands:** 50 brands (e.g., Neogence, POLA, Cellina, Shiseido, Estée Lauder, etc.).
    *   **Unique Products:** 93 trending/newcomer products.

## 2. Data Source & Crawling Methodology

### 2.1 Data Source
Data was collected from @cosme Taiwan, the largest cosmetics and beauty review website in Taiwan. The user ratings and reviews on this platform carry significant benchmark value within the beauty industry.

### 2.2 Crawling Logic and Sampling Design

1.  **Target Product Filtering:**
    *   Accesses the "Monthly Newcomers/Hot Rankings" pages (`https://www.cosme.net.tw/newhot?mindex={mindex}`) via the `mindex` URL parameter (ranging from 0 to 12, corresponding to the current month back to the past 13 months).
    *   Only the top 10 trending newcomer products for each month were sampled, excluding off-season or less popular items.
    *   A total of 130 product page URLs were collected (deduplicated to 93 unique products due to repeat appearances across months or web structural changes).
2.  **Review Crawling:**
    *   Utilizes Playwright (an asynchronous browser automation tool) for web page rendering to fully load dynamic content.
    *   Implements the `playwright-stealth` evasion mechanism to bypass anti-scraping detection.
    *   To prevent performance bottlenecks and minimize server load on the target website, the crawler enforces a cap of 5 pages of reviews per product (`max_pages=5`).
    *   The crawler simulates human behavior by pausing randomly for 4-7 seconds before clicking to the next page, and for 15-30 seconds between different products.

## 3. Data Preprocessing

Data preprocessing is divided into three major stages: crawler-level cleansing, natural language processing (NLP), and feature & label engineering.

### 3.1 Crawler-level Cleansing
*   **HTML/Whitespace Trimming:** Strips leading and trailing whitespaces using `.strip()` right after element extraction.
*   **Newline Removal:** Replaces all line breaks and special characters (such as `
`, ``, ` `, ` `) in the review content with standard spaces. This ensures each review is correctly stored as a single line in the CSV file, preventing malformed row parsing.

## 4. Limitations & Potential Biases

When leveraging this dataset for analytics or training machine learning models, the following caveats should be taken into account:

### 4.1 Selection Bias & Capping Limit
*   **Ranking Bias:** The dataset covers only the top 10 "newcomer/trending" products per month. Consequently, this dataset represents market reactions to newly launched or high-hype products and does not capture long-standing evergreen products or niche segments in the broader skincare/cosmetics market.
*   **Page Truncation:** A maximum of 5 pages of reviews were scraped per product. For viral products with hundreds of review pages, this dataset only captures newer feedback and fails to span the entire product life cycle.

### 4.2 Extreme Class Imbalance
*   **Overwhelmingly Positive Reviews:** During sentiment analysis evaluation on a test sample of 1,571 records, positive reviews (Label 1) accounted for 1,426 records (~90.7%), whereas negative reviews (Label 0) accounted for only 145 records.

### 4.3 Sponsorship & Promotional Campaign Noise
*   **High Ratio of Sponsored Reviews:** Because @cosme regularly coordinates product trials and sampling campaigns, the dataset contains a substantial amount of promotional boilerplate phrasing, such as "thank you for the trial opportunity" or "received product for review."
*   **Inflated Tone and Ratings:** Reviews tied to these sampling events tend to cluster in the high 5-7 star range due to courtesy bias or psychological reciprocity. This is the primary driver behind both the "extreme class imbalance" and the keyword lists being heavily saturated with words like "trial," "thank you," and "opportunity."

### 4.4 Temporal Constraints
*   The dataset spans only 13 months. While sufficient for tracking seasonal transitions (e.g., sun protection/oil-control in spring/summer vs. hydration/anti-aging in autumn/winter), it remains inadequate for observing long-term (e.g., 3-5 years) market technological upgrades or shifts in consumer macro-preferences.
