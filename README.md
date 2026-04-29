#Laptop Price Tracker

A web scraping application that extracts reaal laptop listings
from webscraper.io/test-sites/e-commerce/static/computers/laptops
and presents the data in a GUI with a summary stats panel and a live price distribution chart

#Features

-Real web scraping — pulls live laptop names and prices from discountelectronics.com
-Dark-themed GUI with tkinter
-Sortable table — click any column header to sort by name, price, rating
-Summary statistics— total count, avg/min/max price, avg rating, best value pick
-Price distribution chart — live matplotlib histogram updates after every scrape
-Multi-page scraping — configurable page count (default: 3 pages)

#Setup Instructions

#1. Install Python 3.11+
#2. Clone this repository
#3. Install dependencies:

pip install -r requirements.txt
Install: `requests`, `beautifulsoup4`, `matplotlib`

#4. Run it:
python main.py

#How to Use

1. Set Pages to scrape (1–10) in the control bar
2. Click Scrape Laptops for live data loads from the scraping website
3. Click any column header(Name / Price / Rating) to sort
4. View Summary Statistics and the Price Distribution chart on the right

#Data Source

All data comes from:
> webscraper.io/test-sites/e-commerce/static/computers/laptops 

- specifically designed for scraping practice 

#Other Requirements: 

requests - 2.31.0 version
matplotlib - 3.7.0 version
