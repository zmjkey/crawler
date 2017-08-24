#coding:utf8
import json
from urllib import urlencode

import re
from bs4 import BeautifulSoup
from pip._vendor import requests
from pip._vendor.requests import RequestException


def get_page_index(offset,keyword):
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'cur_tab': 1
    }
    url = 'https://www.toutiao.com/search_content/?' + urlencode(data)

    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print("请求索引页出错")
        return None

def get_page_detail(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print("请求详情页出错")
        return None

def parse_page_detail(html,url):
    soup = BeautifulSoup(html, 'lxml')
    title = soup.select('title')[0].get_text()
    print(title)
    images_pattern = re.compile(r"var BASE_DATA = {.*?};", re.S)
    result = re.search(images_pattern, html)
    if result:
        print(result.group(1))
        data = json.loads(result.group(1))
        if data and 'articleInfo' in data.keys():
            content = data.get('articleInfo').get('content')
            url_content = re.search(re.compile('http'),content)
            image = [item.get() for item in url_content]
            return {
                'title': title,
                'url': url,
                'image': image
            }

    else:
        images_pattern = re.compile('gallery: {.*?}', re.S)
        result = re.search(images_pattern, html)
        if result:
            data = json.loads(result.group(1))
            if data and 'sub_images' in data.keys():
                content = data.get('sub_images')
                image = [item.get('url') for item in content]
                return {
                    'title':title,
                    'url':url,
                    'image':image
                }

def parse_page_index(html):
    data = json.loads(html)
    if data and 'data' in data.keys():
        for item in data.get('data'):
            yield item.get('article_url')

def main():
    html = get_page_index(0, '街拍')
    for url in parse_page_index(html):
        html = get_page_detail(url)
        if html:
            parse_page_detail(html,url)

if __name__ == '__main__':
    main()