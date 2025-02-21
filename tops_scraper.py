from seleniumbase import Driver
import time
import re
import pandas as pd
from tqdm import tqdm
import requests


def get_sidebar_item():
    """
    Scrapes the sidebar items and their URLs from the main page.
    Returns a DataFrame containing the sidebar item names and their corresponding URLs.
    """
    driver = Driver()
    print("Scraping sidebar item URLs")
    url = "https://www.tops.co.th/en"
    driver.open(url)
    # Find all sidebar item elements using XPath
    elements = driver.find_elements('((//div[@class = "item sidebar-item"])//a)', "xpath")
    # Extract URLs and names from the elements
    urls = [elem.get_attribute("href") for elem in elements]
    names = [elem.text for elem in elements]

    # Create a DataFrame to store the sidebar items and their URLs
    pages = {"side_bar_item": names, "url": urls}
    my_df = pd.DataFrame(pages)
    driver.quit()
    return my_df


def get_category_urls(df, url_xpath='//a[contains(text(), "View All")]', text_xpath='//h2[@class = "plp-carousel__title-name"]'):
    """
    Scrapes category URLs from the sidebar item URLs.
    Returns a DataFrame containing category names, category URLs, and their corresponding sidebar items.
    """
    driver = Driver()
    print("Scraping category URLs")
    urls = list(df["url"])
    side_bar_items = list(df["side_bar_item"])
    temp_df = pd.DataFrame()
    for i in tqdm(range(len(urls))):
        driver.open(urls[i])
        # Wait for the page to load by checking for a specific element
        driver.get_text('(//div[@class ="product-item mt-product-item"]//a[1])[1]', timeout=5)
        # Find all category URLs and their names using XPath
        url_elements = driver.find_elements(url_xpath, "xpath")
        cat_urls = [elem.get_attribute("href") for elem in url_elements]
        text_elements = driver.find_elements(text_xpath, "xpath")
        names = [elem.text for elem in text_elements]
        # Create a DataFrame for the current category
        my_df = pd.DataFrame({"category": names, "cat_url": cat_urls})
        my_df["side_bar_item"] = side_bar_items[i]
        my_df["side_bar_url"] = urls[i]
        # Concatenate the current category DataFrame with the main DataFrame
        temp_df = pd.concat([temp_df, my_df])
    driver.quit()
    return temp_df


def get_product_urls(df):
    """
    Scrapes product URLs from the category URLs.
    Returns two DataFrames: one with successful product URLs and one with failed category URLs.
    """
    driver = Driver()
    print("Scraping product URLs")
    urls = list(df['cat_url'])
    temp_df = pd.DataFrame()
    temp_df1 = pd.DataFrame()
    for url in tqdm(urls):
        try:
            driver.open(url)
        except:
            # If the driver fails, reinitialize it and try again
            driver.quit()
            driver = Driver()
            driver.open(url)
        try:
            # Scroll to the bottom of the page to load all products
            ini_elements = 0
            driver.get_text('(//div[@class ="product-item mt-product-item"]//a[1])[1]', timeout=5)
            while True:
                elements = driver.find_elements('//li[@class ="ais-InfiniteHits-item"]', "xpath")
                cur_elements = len(elements)
                if cur_elements == ini_elements:
                    break
                else:
                    driver.execute_script(f"window.scrollBy(0, 1200);")
                    time.sleep(2)
                    ini_elements = cur_elements

            # Extract product URLs
            elements = driver.find_elements('//li[@class ="ais-InfiniteHits-item"]//a', "xpath")
            product_urls = [elem.get_attribute("href") for elem in elements]
            # Create a DataFrame for the current product URLs
            my_df = pd.DataFrame({"cat_url": [url for i in range(len(product_urls))], "product_url": product_urls})
            temp_df = pd.concat([temp_df, my_df])
        except:
            # If scraping fails, log the failed category URL
            my_df = pd.DataFrame({"cat_url": [url]})
            temp_df1 = pd.concat([temp_df1, my_df])
    driver.quit()
    return temp_df, temp_df1


def extract_quantity_unit(text):
    """
    Extracts quantity and unit from a given text string.
    Returns a formatted string with quantity and unit if valid, otherwise returns None.
    """
    valid_units = {
        # Weight Units
        "mg", "g", "kg", "lb", "oz", "ton", "lbs",
        # Volume Units
        "ml", "l", "ltr", "gallon", "cc", "dl", "cl", "floz", "pt", "qt",
        # Length Units
        "mm", "cm", "m", "km", "inch", "inches", "metre", "meters", "feet", "ft", "yard", "yards",
        # Count-Based Units
        "pcs", "pieces", "pack", "packs", "set", "roll", "rolls", "sheets", "bags", "pairs",
        # Cooking Measurements
        "tbsp", "tsp", "cup", "cups", "stick", "sticks",
        # Thickness & Layers
        "ply", "layer", "layers",
        # Percent & Miscellaneous
        "percent", "%", "dozen", "servings", "portion", "portions"
    }
    # Use regex to find quantity and unit in the text
    match = re.search(r"(\d+\.?\d*)\s*([a-zA-Z%]+)", text)  # % included for percentage
    if match:
        quantity, unit = match.groups()
        unit = unit.lower().strip()  # Normalize unit
        if unit in valid_units:  # Keep only valid units
            return f"{quantity}{unit}"
    return None


def setup_csv_files():
    """
    Sets up CSV files for storing product details and failed product URLs.
    Creates the files if they do not already exist.
    """
    # creating a product details csv file
    try:
        product_details_df = pd.read_csv('product_data.csv')
    except:
        column_names = ["url", "name", "image_url", "product_detail", "price", "price_label", "category", "bar_code", "label", "quantity"]
        product_details_df = pd.DataFrame(columns=column_names)
        product_details_df.to_csv('product_data.csv', index=False)

    # creating failed product csv file
    try:
        failed_product_df = pd.read_csv('failed_product.csv')
    except:
        column_names = ["url", "error"]
        failed_product_df = pd.DataFrame(columns=column_names)
        failed_product_df.to_csv('failed_product.csv', index=False)


def update_failed_csv():
    """
    Updates the failed product CSV file by removing URLs that have been successfully processed.
    """
    failed_product_df = pd.read_csv('failed_product.csv')
    product_details_df = pd.read_csv('product_data.csv')
    completed = set(product_details_df['url'])
    cleaned_failed_product_df = failed_product_df[~failed_product_df['url'].isin(completed)]
    # Save the cleaned failed_product.csv back
    cleaned_failed_product_df.to_csv('failed_product.csv', index=False)


def check_redirection(url):
    """
    Checks if a URL redirects to another URL.
    Returns the redirected URL if redirection occurs, otherwise returns None.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }
    response = requests.get(url, allow_redirects=True, headers=headers)
    if response.history:
        return f"URL was redirected to: {response.url}"


def scrap_products(to_scrap_df):
    """
    Scrapes product details from the provided DataFrame of product URLs.
    Saves the scraped data to CSV files and updates the failed product CSV.
    """
    to_scrap_df['product_url'] = to_scrap_df['product_url'].str.replace("/th/", "/en/")

    setup_csv_files()
    product_details_df = pd.read_csv('product_data.csv')
    failed_df = pd.read_csv('failed_product.csv')
    # Filtering out those URLs which are already processed
    completed = set(product_details_df['url'])
    to_process = set(to_scrap_df['product_url'])  # URLs from main source
    failed = set(failed_df[failed_df['error'].str.contains("URL was redirected to:")]['url'])
    # URLs to process = (not completed)
    product_urls = (to_process - completed) - failed

    print(f"{len(product_urls)} products to be scrapped")
    driver_count = 0

    driver = Driver()
    for url in tqdm(product_urls):
        try:
            if driver_count >= 400:  # After every 400 iterations, reinitialize the driver
                driver.quit()
                driver = Driver()
                driver_count = 0
            try:
                driver.open(url)
            except:
                # If the driver fails, reinitialize it and try again
                driver = Driver()
                driver.open(url)
                print("Re-initialising the driver")

            # Extract product details
            name = driver.get_text('//div[@class = "product-Details-name"]', timeout=2)
            image_elems = driver.find_elements('//div[@class = "xzoom-thumbs"]//a', "xpath")
            image_url = ", ".join([elem.get_attribute("href") for elem in image_elems])

            try:
                product_detail = driver.get_text('//div[@class = "accordion-body"]', timeout=0.1)
            except:
                product_detail = ''

            price = driver.get_text('//span[@class = "product-Details-current-price"]')
            price_label = driver.get_text('//span[@class = "product-Details-price-label"]')
            category = driver.get_attribute('//div[@class = "product-Details-page-root"]', "data-product-categories", "xpath")
            barcode_number = driver.get_text('//div[@class = "product-Details-sku"]')

            try:
                label = driver.get_text('//p[@class = "product-Details-seasonal-label"]', timeout=0.1)
            except:
                label = ''

            quantity = extract_quantity_unit(name)

            # Create a DataFrame for the current product details
            product_details_df = pd.DataFrame({"url": [url], "name": [name], "image_url": [image_url], "product_detail": [product_detail], "price": [price], "price_label": [price_label], "category": [category], "bar_code": [barcode_number], "label": [label], "quantity": [quantity]})
            product_details_df.to_csv('product_data.csv', index=False, mode="a", header=False)

        except Exception as e:
            # If an exception occurs, log the error
            status = check_redirection(url)
            if status is None:
                status = e

            failed_product_df = pd.DataFrame({"url": [url], "exception": [status]})
            failed_product_df.to_csv('failed_product.csv', index=False, mode="a", header=False)

        driver_count += 1

    driver.quit()

    # Save the final data as a JSON file
    json_data = product_details_df.to_json(orient="records", indent=4)
    with open("final_data.json", "w") as json_file:
        json_file.write(json_data)
    print('JSON uploaded')


if __name__ == "__main__":
    # Main execution block
    try:
        to_scrap_df = pd.read_csv('product_url.csv')
    except:
        # If the product URL CSV does not exist, scrape the sidebar items, categories, and product URLs
        side_items = get_sidebar_item()
        category_df = get_category_urls(side_items)
        prdouct_url_df, failed_df = get_product_urls(category_df)
        to_scrap_df = pd.merge(prdouct_url_df, category_df, how="inner", on="cat_url")
        to_scrap_df.to_csv("product_url.csv", index=False)

    # Scrape product details
    scrap_products(to_scrap_df)

    # Update the failed CSV file
    update_failed_csv()