# Web Scraping Script for Tops.co.th

## Overview
This script is designed to scrape product data from the [Tops.co.th](https://www.tops.co.th) website. It extracts key product details, such as name, image URL, price, category, barcode, and more. The script is optimized for JavaScript-heavy websites and efficiently avoids redundant requests by skipping already processed URLs.

# Product Scraper

This script is designed to scrape product URLs while ensuring that previously processed and failed URLs are not retried. It includes mechanisms to handle failures due to redirections and logs issues for future analysis.

## Features
- **Resumes from Last Successful Execution**: The script tracks completed URLs and avoids reprocessing them.
- **Handles Redirect Failures**: URLs that failed due to redirections are excluded from future runs.
- **Logs Failures for Analysis**: Instead of outright excluding redirected URLs, they are logged separately with timestamps to monitor if the issue persists.


## Approach Used for Scraping
### 1. **Sidebar Items Scraping**
- Extracts sidebar items and their URLs from the main page.
- Uses **SeleniumBase** to interact with the website and retrieve data.

### 2. **Category URLs Scraping**
- Navigates to each sidebar URL and extracts the "View All" URLs.
- These URLs provide access to the full product list in each category.

### 3. **Product URLs Scraping**
- Scrolls dynamically through each category page to load all product listings.
- Extracts individual product page URLs.

### 4. **Product Details Scraping**
- For each product URL, extracts:
  - `name`, `image_url`, `product_detail`, `price`, `price_label`, `category`, `bar_code`, `label`, `quantity`
- Missing fields are handled gracefully, and errors are logged in a separate CSV file.

## Data Storage
The extracted data is saved in multiple files:
- `product_url.csv` - Contains scraped product URLs along with category and sidebar details.
- `product_data.csv` - Stores successfully scraped product information.
- `failed_product.csv` - Logs URLs that failed to scrape along with error messages.
- `final_data.json` - JSON version of the extracted product data.

## Dependencies
To run this script, ensure you have the following Python packages installed:

```txt
pandas==2.2.3
requests==2.32.3
tqdm==4.67.1
seleniumbase==4.34.17
```

You can install them using:

```bash
pip install -r requirements.txt
```

## Installation & Execution
### Step 1: Clone the Repository
```bash
git clone <repository_url>
cd <repository_directory>
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Script
```bash
python tops_scraper.py
```

## Challenges Faced & Solutions
### 1. **JavaScript-Heavy Website**
- **Problem:** Traditional `requests`-based scraping does not work.
- **Solution:** Used **SeleniumBase** to interact with JavaScript-rendered content.

### 2. **Bot Protection & Redirections**
- **Problem:** Occasional redirections to extensions or unrelated pages.
- **Solution:** SeleniumBase handles many of these automatically. The script also reinitializes the driver when necessary.

### 3. **Dynamic Product URL Loading**
- **Problem:** Products load dynamically as the page scrolls.
- **Solution:** The script simulates scrolling and waits for elements to load before extracting URLs.

### 4. **Handling Missing Data**
- **Problem:** Some products have missing fields (e.g., quantity, label).
- **Solution:**
  - If `label` exists, it is extracted; otherwise, it is set to `None`.
  - `quantity` is extracted using regex from the product name.


## Sample Output (First 5 Products)

[
    {
        "url": "https://www.tops.co.th/en/otop-doikham-savoury-strawberry-30g-8850773551115",
        "name": "(OTOP) Doikham Savoury Strawberry 30g.",
        "image_url": [
            "https://assets.tops.co.th/DOIKHAM-DoikhamSavouryStrawberry30g-8850773551115-1?$JPEG$",
            "https://assets.tops.co.th/DOIKHAM-DoikhamSavouryStrawberry30g-8850773551115-2?$JPEG$"
        ],
        "product_detail": "The product received may be subject to package modification and quantity from the manufacturer. We reserve the right to make any changes without prior notice. *The images used are for advertising purposes only.",
        "price": "30.00",
        "price_label": "/ pcs.",
        "category": "Snacks & Desserts / Nuts & Dried Fruit / Dried Fruit",
        "bar_code": "SKU 8850773551115",
        "label": "OTOP Product",
        "quantity": "30g"
    },
    {
        "url": "https://www.tops.co.th/en/otop-doikham-dried-mango-140g-8850773550262",
        "name": "(OTOP) Doikham Dried Mango 140g.",
        "image_url": [
            "https://assets.tops.co.th/DOIKHAM-DoikhamDriedMango140g-8850773550262-1?$JPEG$",
            "https://assets.tops.co.th/DOIKHAM-DoikhamDriedMango140g-8850773550262-2?$JPEG$",
            "https://assets.tops.co.th/DOIKHAM-DoikhamDriedMango140g-8850773550262-3?$JPEG$",
            "https://assets.tops.co.th/DOIKHAM-DoikhamDriedMango140g-8850773550262-4?$JPEG$"
        ],
        "product_detail": "The product received may be subject to package modification and quantity from the manufacturer. We reserve the right to make any changes without prior notice. *The images used are for advertising purposes only.",
        "price": "80.00",
        "price_label": "/ pcs.",
        "category": "Snacks & Desserts / Nuts & Dried Fruit / Dried Fruit",
        "bar_code": "SKU 8850773550262",
        "label": "OTOP Product",
        "quantity": "140g"
    }
]



### `product_data.csv`
| URL | Name | Image URL | Product Detail | Price | Price Label | Category | Barcode | Label | Quantity |
|---|---|---|---|---|---|---|---|---|---|
| [Product 1](https://www.tops.co.th/en/otop-doikham-savoury-strawberry-30g-8850773551115) | (OTOP) Doikham Savoury Strawberry 30g. | Image Links | Properties description | 30.00 | / pcs. | Snacks & Desserts /// Nuts & Dried Fruit /// Dried Fruit | SKU 8850773551115 | OTOP Product | 30g |
| [Product 2](https://www.tops.co.th/en/otop-doikham-dried-mango-140g-8850773550262) | (OTOP) Doikham Dried Mango 140g. | Image Links | Properties description | 80.00 | / pcs. | Snacks & Desserts /// Nuts & Dried Fruit /// Dried Fruit | SKU 8850773550262 | OTOP Product | 140g |
| [Product 3](https://www.tops.co.th/en/otop-doikham-dried-strawberry-140g-8850773550279) | (OTOP) Doikham Dried Strawberry 140g. | Image Links | Properties description | 155.00 | / pcs. | Snacks & Desserts /// Nuts & Dried Fruit /// Dried Fruit | SKU 8850773550279 | OTOP Product | 140g |
| [Product 4](https://www.tops.co.th/en/otop-tongtinlalafarm-sweet-milk-tablets-15g-8857124514072) | (OTOP) TongtinLalafarm Sweet Milk Tablets 15g | Image Links | Properties description | 10.00 | / pcs. | Snacks & Desserts /// Candies & Chewing Gum /// Children's Candies | SKU 8857124514072 | OTOP Product | 15g |
| [Product 5](https://www.tops.co.th/en/otop-tongtin-lalafarm-cocoa-milk-tablets-15g-8859639300102) | (OTOP) Tongtin Lalafarm Cocoa Milk Tablets 15g | Image Links | Properties description | 10.00 | / pcs. | Snacks & Desserts /// Candies & Chewing Gum /// Children's Candies | SKU 8859639300102 | OTOP Product | 15g |

## Notes
 - Ensure you have a stable internet connection while running the script.
 - The script is designed to respect the website's load by avoiding unnecessary requests and reusing already scraped data.
 - If the website structure changes, the XPaths and logic may need to be updated.

