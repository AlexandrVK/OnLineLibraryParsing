# Онлайн библиотека фантастики

Каталог фантастических произведений, с возможностью как скачивания полностью и чтения Offline так и чтения Online.
Информация о книгах и их тексты взяты с сайта [tululu.org](https://tululu.org).

## Использование

Библиотека содержит карточки фантастических книг с обложкой, информацией и ссылкой `Читать`, которая открывает выбранную книгу для чтения. 

Библиотека предусматривает 2 сценария использования:
- Вы можете использовать OnLine версию библиотеки по [ссылке](https://alexandrvk.github.io/OnLineLibraryParsing).
- Вы можете скачать библиотеку и использовать её OffLine. Для этого сохраните себе архив репозитория, распакуйте и запустите файл `index.html` находящийся в корневом каталоге архива. 

## Дополнительные возможности
Электронная библиотека содержит скрипт `parse_tululu_category.py`  для скачивания информации с сайта [tululu.org](https://tululu.org) и скрипт `render_website.py` для верстки страниц электронной библиотеки на основе информации из предыдущего скрипта

### Установка

Python3 должен быть уже установлен. 
Затем используйте `pip` (или `pip3`, есть есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```
Для скачивания информации и верстки страниц сайта необходимо перейти в папку со скриптом и выполнить команды:
```
python parse_tululu_category.py 
python render_website.py
```
После чего по адресу http://127.0.0.1:5500 вы получите доступ к сформированной библиотеке. В дальнейшем доступ можно получить путем запуска файла `index.html` находящегося в корневом каталоге.

Скрипт `render_website.py` использует файл шаблона `template.html`, данные о книгах из `descriptions.json` тексты книг из папки `books` и картинки к книгам из папки 'images'. Страницы каталога книг формируются в папке `pages`.

### Аргументы запуска parse_tululu_category.py
Внимание: Изменение параметров `dest_folder` и `json_path` нарушит работу скрипта `render_website.py`.

- `-h, --help`: выводит сообщение со справочной информацией.
- `-s, --start_page`: начальный номер страницы для скачивания. По умолчанию: 1.
- `-e, --end_page`: конечный номер страницы для скачивания. По умолчанию: максимальное значение, доступное на сайте.
- `-d, --dest_folder`: путь к каталогу с результатами парсинга: картинкам, книгам, JSON. По умолчанию: текущая директория.
- `-si, --skip_imgs`: не скачивать картинки.
- `-st, --skip_txt`: не скачивать книги.
- `-jp, --json_path`: указать свой путь к json файлу с результатами. По умолчанию: текущая директория.


## Цель проекта.

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).