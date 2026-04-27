import requests
from bs4 import BeautifulSoup
import csv
import argparse
import sqlite3
import time

def init_db():
    conn = sqlite3.connect('books1.db')
    cursor = conn.cursor()
    cursor.execute("""
                CREATE TABLE IF NOT EXISTS books1 (
                    id INTEGER PRIMARY KEY,
                    name TEXT, 
                    price REAL,
                    rating INTEGER,
                    link TEXT UNIQUE)
                """)
    
    conn.commit()
    return conn, cursor


base_url = "https://books.toscrape.com"

rating_system = {
    'One':1,
    'Two':2,
    'Three':3,
    'Four': 4,
    'Five': 5
}

def get_soup(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        return BeautifulSoup(response.text, 'lxml')
    except requests.RequestException as e:
        print(f'Request failed: {e}')
        return None
def scrape_books(pages, min_rating, max_price,cursor):
    books_scraped=0

    for page in range(1, pages + 1):
        print(f"Scraping page {page}...")

        url = f"https://books.toscrape.com/catalogue/page-{page}.html"
        soup = get_soup(url)
        if not soup:
            continue
        books = soup.find_all('li', class_='col-xs-6 col-sm-4 col-md-3 col-lg-3')
        time.sleep(0.5)
        for book in books:
            name = book.find('h3').find('a')['title']

            price0 = book.find('p', class_='price_color').text
            price = float(price0.replace('Â£',''))

            rating0 = book.find('p', class_='star-rating')
            rating = rating_system[rating0['class'][1]]
            
            link0 = book.find('a')['href']
            link = f'https://books.toscrape.com/catalogue/{link0}'            
            if rating >= min_rating and price <= max_price:
                cursor.execute("""
                               INSERT OR IGNORE INTO books1 (name, price, rating,link)
                               values (?,?,?,?)
                               """,(name,price,rating,link))
                books_scraped +=1
    print(f"Total Books Scraped: {books_scraped}")


def view_books():
    conn = sqlite3.connect("books1.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books1")
    rows= cursor.fetchall()
    print(f"{'ID':<5} {'Name':<40} {'Price':<10} {'Rating':<8}")
    print("-" * 70)

    for row in rows:
        print(f"{row[0]:<5} {row[1][:37]:<40} {row[2]:<10} {row[3]:<8}")


# def save_to_csv(data):
#     with open('Book_Data_csv.csv', 'w', newline='', encoding='utf-8') as f:
#         writer = csv.DictWriter(f, fieldnames=['Name', 'Price', 'Rating','Link'])
#         writer.writeheader()
#         writer.writerows(data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pages', type=int, default=3)
    parser.add_argument('--min_rating', type=int, default=1)
    parser.add_argument('--max_price', type=float, default=100)
    args = parser.parse_args()

    conn, cursor = init_db()
    scrape_books(args.pages, args.min_rating, args.max_price,cursor)
    conn.commit()
    view_books()    
    print(cheapest_books(cursor=cursor))
    conn.close()


    
def cheapest_books(cursor):
    cursor.execute("""
                   SELECT name, price from books1
                   ORDER BY price ASC LIMIT 5
                   """)
    rows=  cursor.fetchall()
    print("\n \n Cheapest Books: \n ")
    for row in rows:
        print(f"{row[0][:35]:<40} {row[1]:<10}")



if __name__ == "__main__":
    main()
    