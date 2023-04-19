import argparse
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote
import requests
import os
import sys
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import time


def check_for_redirect(response):
     
     if response.history:
        raise requests.exceptions.HTTPError()

def download_txt(url, payload, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который требуется скачать.
        payload: параметры URL.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять. (по умолчанию "books" )
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    Path(folder).mkdir(parents=True, exist_ok=True)
    url = urljoin(urlsplit(url)._replace(path='', query='', fragment='').geturl(), "txt.php")
    response = requests.get(url,params = payload )
    check_for_redirect(response)
    response.raise_for_status()
    filepath=os.path.join(folder,f"{sanitize_filename(filename)}.txt")
    with open(filepath, "w") as file:
        file.write(response.text)
    return filepath  

def download_image(url,filename,folder="images/"):
    """Скачивает изображения по указанному URL.
    Args:
        filename (str): имя файла, которое присвоится скачанному файлу.
        url (str): URL для скачивания файла.
        folder (str): Папка, куда сохранять. (по умолчанию "images" )
    """
    Path(folder).mkdir(parents=True, exist_ok=True) 
    response = requests.get(url)
    check_for_redirect(response)
    response.raise_for_status()
    with open(os.path.join("images",filename), "wb") as file:
        file.write(response.content)
       

def parse_book_page(soup,site_url):
    """Возвращает словарь со всеми данными о книге.
    Args:
        soup : принимает html-контент страницы
    Returns:
        Cловарь со всеми данными о книге:
    """ 
    img_url = urljoin(site_url,soup.find(class_ ='bookimage').find('img')['src'])

    title, author = [string.strip() for string in str.split(soup.find("h1").text, "::")]

    genres = [string.text.strip() for string in soup.find("span",class_="d_book").find_all("a")]
    
    comments = [string.find("span",class_ ="black" ).text.strip() for string in soup.find_all("div",class_ ="texts")]
            
    return {"img_url" : img_url, "title" : title, "author" : author, "genres" : genres, "comments" : comments } 

def main():
    parser = argparse.ArgumentParser()
    parser.description = "Этот скрипт скачивает страницы в диапазоне от 'start_id' до 'end_id' с сайта tululu.org"
    parser.add_argument("-s", "--start_id", type=int, default=1, help="Начальный номер страницы для скачивания. По умолчанию: 1.")
    parser.add_argument("-e", "--end_id", type=int, default=10, help="Конечный номер страницы для скачивания. По умолчанию: 10.")

    args = parser.parse_args()
    
    for book_id in range(args.start_id,args.end_id+1):
        try:  
            url = f"https://tululu.org/b{book_id}/"
            response = requests.get(url)
            check_for_redirect(response)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            
            parsed_page = parse_book_page(soup,url)
            
            download_txt(url, {"id": book_id}, parsed_page["title"])

            filename =  unquote(urlsplit(parsed_page["img_url"]).path.split("/")[-1])
            
            download_image(parsed_page["img_url"],filename)
        except requests.exceptions.HTTPError as e:
            print(f"Ошибка при скачивании книги: {e}", file=sys.stderr)
        except requests.exceptions.ConnectionError as e:
            print(f"Ошибка соединения: {e}. Повторная попытка через 5 секунд...", file=sys.stderr)
            time.sleep(5) 
            continue


if __name__ == "__main__":
    main()