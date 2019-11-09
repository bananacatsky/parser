"""
Программе в качестве аргумента передаётся ссылка на сайт,
который она обходит и извлекает данные с возможностью
проксирования через гуглкэш

Usage:
    crawler.py <url> [options]

Options:
    -h --help               справка
    --use-google-cache      использовать гуглкэш для парсинга сайта
    --root-url=URL          не выходить за рамки указанной ссылки (по умолчанию совпадает с первой ссылкой)
    --output-file=FILE      сохранять извлеченные данные в указанный файл [default: output.txt]
    --regex=REGEX           извлекать из страниц указанное регулярное выражение и сохранять в файл [default: <title>.*</title>]
    --max-count=NUMBER      перейти не более чем по указанному числу ссылок [default: ]
    --logging=LEVEL         уровень логгирования программы [default: INFO]
    --not-found=STRING      считать страницу не найденной, если в html присутствует указанная строка [default: Error 404 (Not Found)]
"""
from docopt import docopt
import urllib.parse as up
import re
import requests
import logging


def extract_data(html, regex_string, output_file):
    data = re.findall(regex_string, html, re.IGNORECASE | re.DOTALL)
    with open(output_file, 'a', encoding='utf-8') as f:
        for line in data:
            f.write(line)
            f.write('\n')
            logging.info(line)


def find_links(html):
    reg = r'''href\s*=\s*['"](.+?)['"]'''  # check greedy
    result = set(re.findall(reg, html))
    return result


def get_html(url, use_google_cache, not_found_text):
    if use_google_cache:
        response = requests.get(google_cache_pattern + url)
    else:
        response = requests.get(url)

    html = response.text

    if response.status_code == 200:
        if not_found_text in html:
            logging.error(f"PAGE HAS NOT FOUND TEXT: {response.status_code} {url}")
            html = ''
        else:
            logging.debug(url, response.status_code)

    else:
        logging.error(f"{response.status_code} {url}")
        logging.debug(html)
        html = ''

    return html


def abs_links(list_of_links, base_url):
    for rel in list_of_links:
        full = up.urljoin(base_url, rel)
        yield full


def crawler(root, url, use_google_cache, not_found_text, regex_string, output_file, max_count):
    if max_count and len(visited) > max_count:
        return

    logging.info(url)
    html = get_html(url, use_google_cache, not_found_text)
    extract_data(html, regex_string, output_file)
    links = find_links(html)
    for l in abs_links(links, url):
        if l.startswith(root):
            if l not in visited:
                visited.add(l)
                crawler(root, l, use_google_cache, not_found_text, regex_string, output_file, max_count)


visited = set()
google_cache_pattern = r'http://webcache.googleusercontent.com/search?q=cache:'

if __name__ == "__main__":
    args = docopt(__doc__)
    logging.basicConfig(level=getattr(logging, args["--logging"]))
    crawler(
        root=args["--root-url"] or args["<url>"],
        url=args["<url>"],
        use_google_cache=args["--use-google-cache"],
        not_found_text=args["--not-found"],
        regex_string=args["--regex"],
        output_file=args["--output-file"],
        max_count=int(args["--max-count"] or 0),
    )
