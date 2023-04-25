import argparse
import pathlib
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
    parser = argparse.ArgumentParser()
    parser.description = "Этот скрипт скачивает страницы SCIFI  с сайта tululu.org в диапазоне от 'start_page' до 'end_page'"
    parser.add_argument("-s", "--start_page", type=int, default=1, help="Начальный номер страницы для скачивания. По умолчанию: 1.")
    parser.add_argument("-e", "--end_page", type=int, default=sys.maxsize, help="Конечный номер страницы для скачивания. ")
    parser.add_argument("-d", "--dest_folder", type=pathlib.Path, default="", help="Путь к каталогу с результатами парсинга: картинкам, книгам, JSON.")
    parser.add_argument("-si", "--skip_imgs", action="store_true", help="Не скачивать картинки.")
    parser.add_argument("-st", "--skip_txt", action="store_true", help="Не скачивать книги.")
    parser.add_argument("-jp", "--json_path", type=pathlib.Path, default="", help="json_path — указать свой путь к json файлу с результатами.")
    args = parser.parse_args()

    scifi_url = "https://tululu.org/l55/"
    site_url = urlsplit(scifi_url)._replace(path='', query='', fragment='').geturl()
   
    response = requests.get(scifi_url)
    check_for_redirect(response)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    lastpage = int(soup.select_one('p.center a.npage:last-child').text) 
    if args.end_page < lastpage:
        lastpage = args.end_page

    pages=[]
    for numpage in range(args.start_page,lastpage):
        url = urljoin(scifi_url,str(numpage))
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
            if not args.skip_txt:
                download_txt(url, {"id": url.split('b')[-1]}, parsed_page["title"],os.path.join(args.dest_folder,"books"))
            if not args.skip_imgs:
                filename =  unquote(urlsplit(parsed_page["img_url"]).path.split("/")[-1])
                download_image(parsed_page["img_url"],filename,os.path.join(args.dest_folder,"image"))
            parsed_page["book_path"] = f"books/{sanitize_filename(parsed_page['title'])}.txt"
            parsed_page["img_url"] = f"images/{sanitize_filename(parsed_page['img_url'].split('/')[-1])}"
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