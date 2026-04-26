import requests
from bs4 import BeautifulSoup
import csv
import argparse

base_url = "https://books.toscrape.com"

rating_system = {
    'One':1,
    'Two':2,
    'Three':3,
    'Four': 4,
    'Five': 5
}

def get_soup(url):
    response = requests.get(url, timeout=10)
    return BeautifulSoup(response.text, 'lxml')

def scrape_books(pages, min_rating, max_price):
    all_data = []

    for page in range(1, pages + 1):
        print(f"Scraping page {page}...")

        url = f"https://books.toscrape.com/catalogue/page-{page}.html"
        soup = get_soup(url)
        books = soup.find_all('li', class_='col-xs-6 col-sm-4 col-md-3 col-lg-3')

        for book in books:
            name = book.find('h3').find('a')['title']

            price0 = book.find('p', class_='price_color').text
            price = float(price0.replace('Â£',''))

            rating0 = book.find('p', class_='star-rating')
            rating = rating_system[rating0['class'][1]]
            
            link0 = book.find('a')['href']
            link = f'https://books.toscrape.com/catalogue/{link0}'            
            if rating >= min_rating and price <= max_price:
                all_data.append({
                    'Name': name,
                    'Price': price,
                    'Rating': rating,
                    'Link':link
                })

    return all_data


def save_to_csv(data):
    with open('Book_Data_csv.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Name', 'Price', 'Rating','Link'])
        writer.writeheader()
        writer.writerows(data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pages', type=int, default=3)
    parser.add_argument('--min_rating', type=int, default=1)
    parser.add_argument('--max_price', type=float, default=100)
    args = parser.parse_args()

    data = scrape_books(args.pages, args.min_rating, args.max_price)
    save_to_csv(data)

    print(f"{len(data)} books were scraped")


if __name__ == "__main__":
    main()