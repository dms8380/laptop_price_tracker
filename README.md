# 💻 Laptop Price Tracker

A web scraping application that extracts **real refurbished laptop listings**
from [discountelectronics.com](https://discountelectronics.com/refurbished-laptops/)
and presents the data in a full-featured GUI with a summary statistics panel
and a live price distribution chart.

---

## Features

- **Real web scraping** — pulls live laptop names and prices from discountelectronics.com
- **Dark-themed GUI** — built with `tkinter`
- **Sortable table** — click any column header to sort by name, price, or rating
- **Summary statistics** — total count, avg/min/max price, avg rating, best value pick
- **Price distribution chart** — live matplotlib histogram updates after every scrape
- **Multi-page scraping** — configurable page count (default: 3 pages)

---

## Project Structure

```
laptop_tracker/
├── main.py              ← Entry point
├── requirements.txt     ← Dependencies
├── README.md
├── scraper/
│   ├── __init__.py
│   ├── scraper.py       ← Web scraping logic (requests + BeautifulSoup)
│   └── data_manager.py  ← Summary statistics calculations
└── gui/
    ├── __init__.py
    └── gui.py           ← tkinter GUI + matplotlib chart
```

---

## Setup Instructions

### 1. Install Python 3.11+
Download from [python.org](https://www.python.org/downloads/).
On Windows, check ✅ **"Add Python to PATH"** during install.

### 2. Clone this repository
```bash
git clone https://github.com/YOUR_USERNAME/laptop-price-tracker.git
cd laptop-price-tracker
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

Installs: `requests`, `beautifulsoup4`, `matplotlib`
(`tkinter` ships with Python — no separate install needed.)

### 4. Run
```bash
python main.py
```

---

## How to Use

1. Set **Pages to scrape** (1–10) in the control bar
2. Click **🔍 Scrape Laptops** — live data loads from discountelectronics.com
3. Click any **column header** (Name / Price / Rating) to sort
4. View **Summary Statistics** and the **Price Distribution** chart on the right

---

## Data Source

All data comes from:
> **https://discountelectronics.com/refurbished-laptops/**

This is a publicly accessible retail page for refurbished laptops.
The scraper targets product card elements using `requests` and `BeautifulSoup4`.
A 1-second polite delay is inserted between page requests.
