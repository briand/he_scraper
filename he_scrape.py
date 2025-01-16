import requests
from bs4 import BeautifulSoup
import json
import sys
import os
from datetime import datetime

# Base URL of the website
BASE_URL = "https://www.hamestate.com/product-category/ham_equipment/"
skip_categories = ['books']

# Function to scrape product categories
def get_categories(base_url):
    print("Fetching product categories...")
    response = requests.get(base_url)
    print(f'Main page fetch was ok: {response.ok}, returned {len(response.content)} bytes')
    soup = BeautifulSoup(response.content, "html.parser")
    categories = []
    category_list = soup.find("ul", class_="products")
    if category_list:
        for li in category_list.find_all("li", class_=lambda x: x and x.startswith("product-category product")):
            link = li.find("a")
            if link:
                categories.append((link.text.split('(')[0].strip(), link["href"]))
    print(f"Found {len(categories)} categories.")
    return categories

# Function to scrape products from a category
def get_products(category_url):
    #print(f"Fetching products for category URL: {category_url}")
    response = requests.get(category_url)
    soup = BeautifulSoup(response.content, "html.parser")
    products = []
    for product in soup.select(".product"):  # Adjust selector as needed
        try:
            title = product.select_one(".woocommerce-loop-product__title").text.strip()
        except AttributeError:
            title = "unknown"
        try:
            price = product.select_one(".price").text.strip()
        except AttributeError:
            price = "unknown"
        try:
            link = product.select_one("a")["href"]
        except (AttributeError, TypeError):
            link = "unknown"
        try:
            post_id = next(cls.split('-')[1] for cls in product["class"] if cls.startswith("post-"))
        except (AttributeError, StopIteration):
            post_id = "unknown"
        products.append({"title": title, "price": price, "link": link, "post_id": post_id})
    print(f"Found {len(products)} products.")
    return products

# Main scraping routine
def main():
    input_file = None
    if len(sys.argv) > 1:
        input_file = sys.argv[1]

    existing_post_ids = set()
    if input_file:
        print(f"Reading existing post IDs from {input_file}...", end='')
        try:
            with open(input_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                existing_post_ids = {item["post_id"] for item in data if "post_id" in item}
            print(f'found {len(existing_post_ids)} existing products')
        except Exception as e:
            print(f"Error reading input file: {e}")
            return

    print("Starting scraping process...")
    categories = get_categories(BASE_URL)
    all_products = []
    new_products = []
    new_post_ids = set()

    for category_name, category_url in categories:
        if any(skip_term.lower() in category_name.lower() for skip_term in skip_categories):
            print(f"Skipping category: {category_name}")
            continue

        print(f"Processing category: {category_name}: ", end='')
        category_products = get_products(category_url + "?orderby=date&ppp=100")
        for product in category_products:
            product["category"] = category_name
            all_products.append(product)
            if product["post_id"] != "unknown" and product["post_id"] not in existing_post_ids:
                new_products.append(product)
                new_post_ids.add(product["post_id"])

    print(f'Found {len(all_products)} total products')

    if input_file:
        try:
            timestamp = datetime.fromtimestamp(os.path.getmtime(input_file)).strftime('%Y-%m-%d %H:%M:%S')
            title = f"New HamEstate Products Since {timestamp}"
        except Exception as e:
            print(f"Error fetching timestamp: {e}")
            title = "New HamEstate Products"

        if not len(new_products):
            print(f'No new products found since input file timestamp at {timestamp}. Not writing html or json.')
            return

    # Save all products to a JSON file
    output_all_products_file = input_file if input_file else "all_products.json"
    print(f"Saving all products to {output_all_products_file}...")
    with open(output_all_products_file, "w", encoding="utf-8") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=4)


    if input_file:
        print(f'Found {len(new_products)} new products since input file timestamp at {timestamp}')
        print("Generating HTML output for new products...")
        exclude_text = f'excluding categories ({", ".join(skip_categories)})'
        html_output = f"""<html>
<head><title>{title} {exclude_text}</title></head>
<body>
    <h1>{title} {exclude_text}</h1>
    <table border="1">
        <thead>
            <tr>
                <th>Category</th>
                <th>Product Title</th>
                <th>Price</th>
                <th>Product Link</th>
            </tr>
        </thead>
        <tbody>
"""

        for product in new_products:
            html_output += f"""
                <tr>
                    <td>{product.get('category', 'unknown')}</td>
                    <td>{product['title']}</td>
                    <td>{product['price']}</td>
                    <td><a href='{product['link']}'>View Product</a></td>
                </tr>
            """

        html_output += """        </tbody>
    </table>
</body>
</html>"""

        # Save HTML to a file
        output_file = "new_he_products.html"
        print(f"Saving HTML output to {output_file}...")
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(html_output)

    else:

        # Generate HTML output for all products
        print("Generating HTML output for all products...")
        exclude_text = f'excluding categories ({", ".join(skip_categories)})'
        html_output = f"""<html>
<head><title>All HamEstate Products {exclude_text}</title></head>
<body>
    <h1>All HamEstate Products {exclude_text}</h1>
    <table border="1">
        <thead>
            <tr>
                <th>Category</th>
                <th>Product Title</th>
                <th>Price</th>
                <th>Product Link</th>
            </tr>
        </thead>
        <tbody>
"""

        for product in all_products:
            html_output += f"""
                <tr>
                    <td>{product.get('category', 'unknown')}</td>
                    <td>{product['title']}</td>
                    <td>{product['price']}</td>
                    <td><a href='{product['link']}'>View Product</a></td>
                </tr>
            """

        html_output += """        </tbody>
    </table>
</body>
</html>"""

        # Save HTML to a file
        output_file = "all_he_products.html"
        print(f"Saving HTML output to {output_file}...")
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(html_output)

    print("Scraping completed. HTML file has been created.")

if __name__ == "__main__":
    main()
