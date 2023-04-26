import argparse
import json
import os
import pathlib
import sys
import time
from urllib.parse import unquote, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

from download import check_for_redirect, download_image, download_txt, parse_book_page


def create_parser():
    parser = argparse.ArgumentParser()
    parser.description = "Этот скрипт скачивает страницы SCIFI  с сайта tululu.org в диапазоне от 'start_page' до 'end_page'"
    parser.add_argument("-s", "--start_page", type=int, default=1, help="Начальный номер страницы для скачивания. По умолчанию: 1.")
    parser.add_argument("-e", "--end_page", type=int, default=sys.maxsize, help="Конечный номер страницы для скачивания. ")
    parser.add_argument("-d", "--dest_folder", type=pathlib.Path, default="", help="Путь к каталогу с результатами парсинга: картинкам, книгам, JSON.")
    parser.add_argument("-si", "--skip_imgs", action="store_true", help="Не скачивать картинки.")
    parser.add_argument("-st", "--skip_txt", action="store_true", help="Не скачивать книги.")
    parser.add_argument("-jp", "--json_path", type=pathlib.Path, default="", help="json_path — указать свой путь к json файлу с результатами.")
    return parser

def get_last_page_number(scifi_url):
    response = requests.get(scifi_url)
    check_for_redirect(response)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    lastpage = int(soup.select_one('p.center a.npage:last-child').text)
    return lastpage


def main():

    parser = create_parser()
    args = parser.parse_args()

    scifi_url = "https://tululu.org/l55/"
    site_url = urlsplit(scifi_url)._replace(path='', query='', fragment='').geturl()
   
    lastpage = get_last_page_number(scifi_url)

    if args.end_page < lastpage:
        lastpage = args.end_page

    pages=[]
    for numpage in range(args.start_page,lastpage):
        try: 
            url = urljoin(scifi_url,str(numpage))
            response = requests.get(url)
            check_for_redirect(response)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            pages.extend([urljoin(site_url, table_tag.select_one("a")["href"]) for table_tag in soup.select("table.d_book")])
        except requests.exceptions.HTTPError as e:
            print(f"Ошибка при скачивании страницы: {e}", file=sys.stderr)
        except requests.exceptions.ConnectionError as e:
            print(f"Ошибка соединения: {e}. Повторная попытка через 5 секунд...", file=sys.stderr)
            time.sleep(5) 
            continue

    descriptions = []
    for url in pages:
        try:  
            response = requests.get(url)
            check_for_redirect(response)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            parsed_page = parse_book_page(soup,url)
            if not args.skip_txt:
                parsed_page["book_path"] = download_txt(url, {"id": url.split('b')[-1]}, parsed_page["title"],os.path.join(args.dest_folder,"books")).replace(os.sep, '/')
            if not args.skip_imgs:
                filename =  unquote(urlsplit(parsed_page["img_url"]).path.split("/")[-1])
                parsed_page["img_url"] =  download_image(parsed_page["img_url"],filename,os.path.join(args.dest_folder,"image")).replace(os.sep, '/')
            descriptions.append(parsed_page)
        except requests.exceptions.HTTPError as e:
            print(f"Ошибка при скачивании книги: {e}", file=sys.stderr)
        except requests.exceptions.ConnectionError as e:
            print(f"Ошибка соединения: {e}. Повторная попытка через 5 секунд...", file=sys.stderr)
            time.sleep(5) 
            continue
      
    if args.json_path.as_posix() == "." :
       json_path = pathlib.Path.cwd() / args.dest_folder 
    else:
        json_path = pathlib.Path.cwd() / args.json_path

    json_path.mkdir(parents=True, exist_ok=True) 
  
    with open(os.path.join(json_path,'descriptions.json'), 'w') as file:
        json.dump(descriptions, file,ensure_ascii=False)


if __name__ == "__main__":
    main()