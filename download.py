from pathlib import Path
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
        folder (str): Папка, куда сохранять.
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

for book in range(1,10):
    try:  
        response = requests.get(f"https://tululu.org/b{book}")
        check_for_redirect(response)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        title, autor = str.split(soup.find('h1').text,"::")
        print(f"{book}. ",download_txt(f"https://tululu.org/txt.php?id={book}", title.strip()))
    except: 
        pass
