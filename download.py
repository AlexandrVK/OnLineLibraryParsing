from pathlib import Path
import pprint
from urllib.parse import urljoin, urlsplit,unquote
import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

def check_for_redirect(response):
     if any(r.status_code == 302 for r in response.history):
        raise requests.exceptions.HTTPError()

def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять. (по умолчанию "books" )
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    Path(folder).mkdir(parents=True, exist_ok=True)
    try:  
        response = requests.get(url)
        check_for_redirect(response)
        response.raise_for_status()
        filepath=os.path.join(folder,f"{sanitize_filename(filename)}.txt")
        with open(filepath, 'w') as file:
            file.write(response.text)
        return filepath  
    except: 
        return "No FILE!!!"

def download_image(url,filename,folder='images/'):
    """Скачивает изображения по указанному URL.
    Args:
        filename (str): имя файла, которое присвоится скачанному файлу
        url (str): URL для скачивания файла
        folder (str): Папка, куда сохранять. (по умолчанию "images" )
    """
    Path(folder).mkdir(parents=True, exist_ok=True) 
    try: 
        response = requests.get(url)
        check_for_redirect(response)
        response.raise_for_status()
        with open(os.path.join("images",filename), 'wb') as file:
            file.write(response.content)
        return True    
    except: 
        return False

def parse_book_page(soup):
    """Возвращает словарь со всеми данными о книге.
    Args:
        soup : принимает html-контент страницы
    Returns:
        Cловарь со всеми данными о книге:
    """ 
    title, author = [string.strip() for string in str.split(soup.find('h1').text, "::")]

    genres = [string.text.strip() for string in soup.find('span',class_='d_book').find_all('a')]
    
    comments = [string.find('span',class_ ='black' ).text.strip() for string in soup.find_all('div',class_ ='texts')]
            
    return {"Название"      : title,
            "Автор"         : author,
            "Жанры"         : genres,
            "Комментарии"   : comments
           } 

def main():
    for book in range(1,10):
        try:  
            
            response = requests.get(f"https://tululu.org/b{book}")
            check_for_redirect(response)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')

            book_data=parse_book_page(soup)

                   
            print(f"{book}.",download_txt(f"https://tululu.org/txt.php?id={book}", book_data["Название"]))

            url = urljoin("https://tululu.org/",soup.find(class_ ='bookimage').find('img')['src'])
            filename =  unquote(urlsplit(url).path.split("/")[-1])
            
            download_image(url,filename)
           
            pprint.PrettyPrinter().pprint(book_data)

        except: 
            pass

if __name__ == '__main__':
    main()