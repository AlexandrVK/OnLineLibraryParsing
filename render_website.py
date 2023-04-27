import math
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
from livereload import Server
from more_itertools import chunked

def on_reload ():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')
    with open('descriptions.json ', 'r') as my_file:
        descriptions_json = my_file.read()

    books_in_page =  10
    descriptions = json.loads(descriptions_json)
    max_page =  math.ceil(len(descriptions) / books_in_page)

    descriptions = chunked(descriptions,books_in_page)
   

    for chunked_books in enumerate(descriptions,1):

        rendered_page = template.render(books=chunked_books[1], max_page=max_page, cur_page=chunked_books[0])

        with open(os.path.join('pages',f'index{chunked_books[0]}.html'), 'w', encoding='utf8') as file:
            file.write(rendered_page)

    print("Site rebuilt")

Path('pages').mkdir(parents=True, exist_ok=True)

on_reload()

server = Server()
server.watch('template.html', on_reload)
server.serve(root='.')        