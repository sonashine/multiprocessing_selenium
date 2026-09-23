# multiprocessing_selenium

#### Setup
pip install selenium
Google Chrome must be installed; Selenium 4.6+ downloads the driver automatically.

##### Run
   python multiprocessing_example.py urls.txt --workers 4 --o books.json

   python multithreading_example.py urls.txt -w 4 -o books.json

###### A few practical notes

Selectors may break. If Goodreads changes its markup. It is recommende to add comprehensive logging so that these changes are detected easily. If a field comes back empty, inspect the page and update the CSS selector.
Be polite. Add a random 1-3 second delay between requests and don't crank up the worker count. Each worker is a full Chrome instance, roughly 300-500 MB of RAM.
Check the terms of service. Goodreads restricts automated scraping. Keep this to small personal projects and don't redistribute the data.

Happy Tinkering, if you can please consider donating: https://ko-fi.com/goodreadsepilogue