import argparse
import json
import random
import time
from concurrent.futures import ThreadPoolExecutor
 
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
 
 
def make_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1280,900")
    return webdriver.Chrome(options=opts)
 
 
def _text(drv, selector):
    return drv.find_element(By.CSS_SELECTOR, selector).text.strip()
 
 
def scrape_data(url):
    """Open a fresh browser for this one URL, then close it. No state is
    shared between threads, so there's nothing to lock or reuse."""
    result = {"url": url}
    drv = make_driver()
    try:
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
    finally:
        drv.quit()
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
 
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        results = list(ex.map(scrape_data, urls))  # keeps input order
 
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
 
    ok = sum("error" not in r for r in results)
    print(f"Done: {ok}/{len(results)} succeeded -> {args.output}")