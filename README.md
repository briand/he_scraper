# he_scraper
Scraper for HamEstate's product store

# Setup
1. Install Python if your platform of choice doesn't already have it. You'll also need Beatiful Soup, install with `pip install bs4`.

2. Edit the source and add entries to skip_categories for those you wish to skip. The phrases will match subset, case-insensitive. The default is books.

_example:_ `skip_categories = ['books', 'tower']` 

# Usage

_Create a table of the current products across the store_
```bash
python ./he_scrape.py
```
_Products are collected and output to all_he_products.html. Store ids are stored in all_products.json_

---
_Use a json file to detect new products_
```bash
python ./he_scrape.py all_products.json
```
The scraper will read in the json, scrape the website, and output file new_he_products.html contains only those newer than the json
(the json file is updated with the complete store contents)

I have no association with HamEstate, their content is their own. Please use responsibly and don't abuse the HE web site by scraping any more frequently than you would browse the site manually.