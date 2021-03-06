import json
import os
import re
import time
from datetime import datetime, timezone

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

IS_PROXY = True
if IS_PROXY:
    proxy = 'http://127.0.0.1:7890'
    os.environ['http_proxy'] = proxy
    os.environ['HTTP_PROXY'] = proxy
    os.environ['https_proxy'] = proxy
    os.environ['HTTPS_PROXY'] = proxy

BASE_PATH = os.path.dirname(__file__)

REPOSITORY = 'tuot/Notes'
headers = {
    'content-type':
    'application/json',
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
}

MD_PATH = 'docs'
IMAGE_PATH = 'images'
ACCESS_TOKEN = ''


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def save_file(url):

    name = url.split('/')[-1]
    file_path = os.path.join(BASE_PATH, MD_PATH, IMAGE_PATH, name)
    r = requests.get(url, verify=False, stream=True)
    with open(file_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=32):
            f.write(chunk)


def save_image(body):

    pattern = 'https:\/\/user-images.*.png'
    res = re.findall(pattern, body)
    for i in res:
        save_file(i)


def save_mk(articles):
    for i in articles:
        title = i['title']
        body = i['body']
        save_image(body)

        file_name = '{}.md'.format(title)
        file_path = os.path.join(BASE_PATH, MD_PATH, file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(body)


def get_labels():
    url = 'https://api.github.com/repos/{}/labels?page=1&per_page=100&access_token={}'.format(
        REPOSITORY, ACCESS_TOKEN)
    res_json = requests.get(url, verify=False, headers=headers).json()

    return res_json


def get_articles():
    url = 'https://api.github.com/repos/{}/issues?page=1&per_page=100&access_token={}'.format(
        REPOSITORY, ACCESS_TOKEN)
    res_json = requests.get(url, verify=False, headers=headers).json()
    return res_json


def update_readme(articles):

    cur_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    labels_total = len(get_labels())
    articles_total = len(articles)

    with open('README_head.md', 'r', encoding='utf-8') as f:
        md_head = f.read()
        md_head = md_head.format(cur_time=cur_time,
                                 labels=labels_total,
                                 articles=articles_total,
                                 repository=REPOSITORY)

    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(md_head)
        for i in articles:
            title = i['title']
            url = i['html_url']

            t = datetime.strptime(i['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
            local_t = utc_to_local(t)

            lt_str = local_t.strftime('%Y-%m-%d %H:%M:%S')
            f.write('- [{}]({})  {}\n\n'.format(title, url, lt_str))


def main():
    print("update my Notes")
    articles = get_articles()

    update_readme(articles)
    save_mk(articles)


main()
