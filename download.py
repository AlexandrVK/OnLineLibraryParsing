import pathlib
import requests

def books_downloader(filename,path,url,params=""):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True) 
    response = requests.get(url,params=params)
    response.raise_for_status()
    with open(f"{path}/{filename}", 'w') as file:
        file.write(response.text)

path="books"
# url = "https://tululu.org/txt.php?id=32168"

for book in range(10):
    url="https://tululu.org/txt.php"
    params={"id": f"{book+1}"}
    filename =f"id{book+1}"
    books_downloader(filename,path,url,params)
