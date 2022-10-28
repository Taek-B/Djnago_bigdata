from unittest import result
from urllib import response
from bs4 import BeautifulSoup
import requests
import pymysql

import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

import os
from myProject03.settings import STATIC_DIR

# 노래


def melon_crawing():
    datas = []

    url = "https://www.melon.com/chart/week/index.htm"

    header = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=header)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    # print(soup)

    tbody = soup.select_one('#frm > div > table > tbody')
    # print(tbody)
    for chart in tbody.select('tr'):
        tds = chart.find_all('td')

        if len(tds) > 0:
            ranking = tds[1].text
            music_name = tds[5].select_one(
                'div > div > div.ellipsis.rank01 > span > a').text
            singer = tds[5].select_one(
                'div > div > div.ellipsis.rank02 > a').text
            album = tds[6].select_one('div > div > div > a').text

        datas.append([ranking, music_name, singer, album])
        # print('순위 :', ranking)
        # print('곡 :', music_name)
        # print('가수 :', singer)
        # print('앨범 :', album)
        # print('-'*100)

    return datas


# 날씨
def weather_crawing(last_date, weather):

    url = 'https://www.weather.go.kr/weather/forecast/mid-term-rss3.jsp?stnld=108'
    response = requests.get(url)
    html = response.text
    # xml형식의 사이트를 가져오므로 'lxml'를 사용
    soup = BeautifulSoup(html, 'lxml')

    for i in soup.find_all('location'):
        city = i.find('city').string
        weather[city] = []
        for j in i.find_all('data'):
            temp = []
            if(len(last_date) == 0) or (last_date[0]['tmef'] < j.find('tmef').text):
                temp.append(j.find('tmef').text)
                temp.append(j.find('wf').text)
                temp.append(j.find('tmn').text)
                temp.append(j.find('tmx').text)
                # print('temp :', temp)
                weather[i.find('city').string].append(temp)


def weather_make_chart(result, wfs, dcounts):

    # 한글
    font_path = 'c:/Windows/fonts/malgun.ttf'
    font_name = font_manager.FontProperties(fname=font_path).get_name()
    rc('font', family=font_name)

    # 최고기온
    high = []
    # 최저기온
    low = []
    # 날짜(tmef)
    xdata = []

    for row in result.values_list():
        high.append(row[5])
        low.append(row[4])
        xdata.append(row[2].split('-')[2])

    # 이미지 청소한 후 이미지 넣기 위해
    plt.cla()
    plt.figure(figsize=(10, 6))
    plt.plot(xdata, low, label='최저기온')
    plt.plot(xdata, high, label='최고기온')
    plt.legend()
    # 이미지 저장
    plt.savefig(os.path.join(STATIC_DIR, 'images\\weather_busan.png'), dpi=300)

    plt.cla()
    plt.bar(wfs, dcounts)
    plt.savefig(os.path.join(STATIC_DIR, 'images\\weather_bar.png'), dpi=300)

    plt.cla()
    plt.pie(dcounts, labels=wfs, autopct='%.1f%%')
    plt.savefig(os.path.join(STATIC_DIR, 'images\\weather_pie.png'), dpi=300)

    image_dic = {
        'plot': 'weather_busan.png',
        'bar': 'weather_bar.png',
        'pie': 'weather_pie.png',
    }

    return image_dic
