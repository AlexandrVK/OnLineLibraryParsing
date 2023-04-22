import argparse
from pathlib import Path
import pprint
from urllib.parse import urljoin, urlsplit, unquote
import requests
import os
import sys
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import time
from download import download_txt, download_image, parse_book_page, check_for_redirect
import json


def main():
    # parser = argparse.ArgumentParser()
    # parser.description = "Этот скрипт скачивает страницы в диапазоне от 'start_id' до 'end_id' с сайта tululu.org"
    # parser.add_argument("-s", "--start_id", type=int, default=1, help="Начальный номер страницы для скачивания. По умолчанию: 1.")
    # parser.add_argument("-e", "--end_id", type=int, default=10, help="Конечный номер страницы для скачивания. По умолчанию: 10.")
    # args = parser.parse_args()
    scifi_url = "https://tululu.org/l55/"
    site_url = urlsplit(scifi_url)._replace(path='', query='', fragment='').geturl()
    pages=[]
    for i in range(4):
        url = urljoin(scifi_url,str(i+1))
        response = requests.get(url)
        check_for_redirect(response)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        pages.extend([urljoin(site_url, table_tag.select_one("a")["href"]) for table_tag in soup.select("table.d_book")])

    descriptions = []
    for url in pages:
        try:  
            
            response = requests.get(url)
            check_for_redirect(response)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            
            parsed_page = parse_book_page(soup,url)
            
            download_txt(url, {"id": url.split('b')[-1]}, parsed_page["title"])

            filename =  unquote(urlsplit(parsed_page["img_url"]).path.split("/")[-1])
            
            download_image(parsed_page["img_url"],filename)

            parsed_page["book_path"] = f"books/{sanitize_filename(parsed_page['title'])}.txt"
            parsed_page["img_url"] = f"images/{sanitize_filename(parsed_page['img_url'].split('/')[-1])}"
            
            descriptions.append(parsed_page)

        except requests.exceptions.HTTPError as e:
            print(f"Ошибка при скачивании книги: {e}", file=sys.stderr)
        except requests.exceptions.ConnectionError as e:
            print(f"Ошибка соединения: {e}. Повторная попытка через 5 секунд...", file=sys.stderr)
            time.sleep(5) 
            continue
  
    with open('descriptions.json', 'w') as file:
        json.dump(descriptions, file,ensure_ascii=False)


if __name__ == "__main__":
    main()