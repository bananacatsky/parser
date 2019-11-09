"""
Программе в качестве аргумента передаётся ссылка на сайт,
который она обходит и извлекает данные проксируя через гуглкэш
"""
import urllib.parse as up
import re
import requests
import logging
import sys


def extract_data(html):
    reg = r'<td>(.*?)</td>'
    data = re.findall(reg, html, re.S)
    data = [data[i:i + 7] for i in range(0, len(data), 7)]
    # print(data)
    # data = [[] for i in range(len( ]
    with open(r'C:\Users\Restricted\Desktop\table.txt', 'a') as f:
        for name, phone_number, birth_date, street, house, building, flat in data:
            f.write(' | '.join((name, phone_number, birth_date.strip(), street, house, building, flat)) + '\n\n')
            print(name, phone_number, birth_date.strip(), street, house, building, flat)


def find_links(html):
    links = set()
    reg = r'''href\s*=\s*['"](.+?)['"]'''  # check greedy
    result = set(re.findall(reg, html))
    # print(result)
    return result


assert find_links("""
<a href="/uy">
""") == {"/uy"}


def get_html(url):
    response = requests.get(google_cache_pattern + url)
    html = response.text

    if response.status_code == 200:
        # print(html)
        if 'Error 404 (Not Found)!!' in html:
            logging.error(f"в гугл кэше такого нет {response.status_code} {url}")
            html = ''

    else:
        logging.error(html)
        logging.error(f"{response.status_code} {url}")
        html = ''
    print(url, response.status_code)
    return html


def abs_links(list_of_links, base_url):
    for rel in list_of_links:
        full = up.urljoin(base_url, rel)
        # print('abs_link', rel, base_url, full)
        yield full


visited = set()
root = ''
google_cache_pattern = r'http://webcache.googleusercontent.com/search?q=cache:'


def crawler(url):
    print(url)
    # url = google_cache_pattern + url
    html = get_html(url)
    # print(html)
    extract_data(html)
    links = find_links(html)
    for l in abs_links(links, url):
        if l.startswith(root):
            # l = google_cache_pattern + l
            if l not in visited:
                visited.add(l)
                crawler(l)


if len(sys.argv) == 2:
    root = sys.argv[1]
    crawler(root)
else:
    logging.critical("Укажите в качестве единственного аргумента ссылку на сайт для парсинга")
    exit(1)
