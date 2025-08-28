MakroScraperBot

A Python project that scrapes product data from Makro and provides a LINE Bot to browse categories, search products, and view details.

Features

Scrape product name, price, image, and link

Get detailed product info (weight/quantity)

Browse product categories via LINE carousel

Search products by name

View detailed product info in LINE chat

Setup

Install dependencies:

pip install -r requirements.txt


Run ngrok to expose your local server:

ngrok http 5000


Copy the HTTPS URL from ngrok and set it as your LINE Bot webhook URL.

Run the Flask app:

python app.py

Usage

Send “hi” / “menu” in LINE to see product categories

Select a category to view products

Click a product to see detailed info

Built With

Python

Selenium & BeautifulSoup

Flask

LINE Messaging API
