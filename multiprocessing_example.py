import argparse
import json
import multiprocessing
import multiprocessing.util
import os
import random
import time
 
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def make_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,900")
    return webdriver.Chrome(options=opts)

def get_driver():
    """Create this worker's browser on first use, then reuse it."""
    global driver
    if "driver" not in globals():
        driver = None
    if driver is None:
        driver = make_driver()
        # Close Chrome when this worker process exits
        multiprocessing.util.Finalize(None, driver.quit, exitpriority=10)
    return driver
 
 
def _text(drv, selector):
    return drv.find_element(By.CSS_SELECTOR, selector).text.strip()
 
 
def scrape_data(url):
    result = {"url": url}
    try:
        drv = get_driver()
        drv.get(url)
        WebDriverWait(drv, 15).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'h1[data-testid="bookTitle"]')
            )
        )
        result["title"] = _text(drv, 'h1[data-testid="bookTitle"]')
        result["author"] = _text(drv, 'span[data-testid="name"]')
        result["rating"] = _text(drv, "div.RatingStatistics__rating")
        result["ratings_count"] = _text(drv, 'span[data-testid="ratingsCount"]')
    except (TimeoutException, WebDriverException) as e:
        result["error"] = f"{type(e).__name__}: {str(e).splitlines()[0]}"
    time.sleep(random.uniform(1, 3))  # be polite
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("urls_file", help="text file, one Goodreads book URL per line")
    parser.add_argument("-w", "--workers", type=int, default=4)
    parser.add_argument("-o", "--output", default="books.json")
    args = parser.parse_args()
 
    with open(args.urls_file) as f:
        urls = [line.strip() for line in f if line.strip()]
 
    pool = multiprocessing.Pool(processes=args.workers)
    try:
        results = pool.map(scrape_data, urls, chunksize=1)
    finally:
        pool.close()
        pool.join()
 
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
 
    ok = sum("error" not in r for r in results)
    print(f"Done: {ok}/{len(results)} succeeded -> {args.output}")