from urllib import response
from bs4 import BeautifulSoup
import requests
import pandas as pd


url = "https://www.melon.com/chart/week/index.htm"

header = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=header)
html = response.text

soup = BeautifulSoup(html, 'html.parser')
# print(soup)

tbody = soup.select_one('#frm > div > table > tbody')
# print(tbody)

datas = []

for chart in tbody.select('tr'):
    tds = chart.find_all('td')

    if len(tds) > 0:
        ranking = tds[1].text
        music_name = tds[5].select_one(
            'div > div > div.ellipsis.rank01 > span > a').text
        singer = tds[5].select_one('div > div > div.ellipsis.rank02 > a').text
        album = tds[6].select_one('div > div > div > a').text

    datas.append([ranking, music_name, singer, album])
    # print('순위 :', ranking)
    # print('곡 :', music_name)
    # print('가수 :', singer)
    # print('앨범 :', album)
    # print('-'*100)

# print(datas)


def melon_crawing(datas):
    datas[i][0]
    Board.objects.filter
    return
