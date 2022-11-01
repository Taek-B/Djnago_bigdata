from ast import IsNot
from re import TEMPLATE
from unittest import result
from urllib import response
from bs4 import BeautifulSoup
from numpy import equal
import requests
import pymysql

import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

import os
from myProject03.settings import STATIC_DIR, TEMPLATE_DIR

# 지도 import
from pandas import DataFrame
import folium

# wordcloud import
from wordcloud import WordCloud
from konlpy.tag import Okt
from collections import Counter
import re

# webtoon import
from myapp03.models import Board, Comment, Forecast, Webtoon


# 웹툰
def webtoon_crawing(webtoon):
    dayName = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    for i in range(0, 7):
        url = 'https://comic.naver.com/webtoon/weekdayList?week=' + dayName[i]

        # Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36
        header = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=header)
        html = response.text

        soup = BeautifulSoup(html, 'html.parser')

        # day ul 태그
        day_ul = soup.find('ul', {'class': 'category_tab'})
        # print(day_ul)
        web_ul = soup.find('ul', {'class': 'img_list'})

        day_li = soup.find('ul', {'class': 'img_list'}).find_all('li')
        # print(day_li)
        web_li = web_ul.find_all('li')
        # print(len(web_li))

        day_li = day_ul.find_all('li')
        days = day_li[i+1].text
        webtoon[days] = []
        # print(days)

        for j in web_ul.find_all('li'):
            datas = []
            # if len(lis) > 0:
            webtoon_name = j.find('dl').find('a').text
            webtoon_writter = j.find(
                'dd', {'class': 'desc'}).find('a').text
            webtoon_scope = j.find(
                'div', {'class': 'rating_type'}).find('strong').text
            # print('제목 :', webtoon_name)
            # print('작가 :', webtoon_writter)
            # print('별점 :', webtoon_scope)

            if Webtoon.objects.filter(title=webtoon_name).exists() == False:
                datas.append(webtoon_name)
                datas.append(webtoon_writter)
                datas.append(webtoon_scope)
                webtoon[days].append(datas)
            # print('-'*100)


#
def webtoon_wordcloud(datas):
    message = ''

    for item in datas:
        if 'message' in item.keys():
            message = message + re.sub(r'[^\w]', ' ', item['message'])+''

    nlp = Okt()
    # 명사 추출
    message_N = nlp.nouns(message)
    # 명사의 갯수 추출
    count = Counter(message_N)

    word_count = {}

    for tag, counts in count.most_common(80):
        if(len(str(tag)) > 1):
            word_count[tag] = counts
            # print("%s : %d" % (tag, counts))

    font_path = 'c:/Windows/fonts/malgun.ttf'
    wc = WordCloud(font_path, background_color='ivory', width=800, height=600)

    cloud = wc.generate_from_frequencies(word_count)

    plt.figure(figsize=(8, 8))
    plt.imshow(cloud)
    plt.axis('off')
    cloud.to_file('./static/images/webtoon_wordCloud.png')


############################################
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
        print(row)
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


# 지도
def map():
    ex = {'경도': [127.061026, 127.047883, 127.899220, 128.980455, 127.104071, 127.102490, 127.088387, 126.809957, 127.010861, 126.836078, 127.014217, 126.886859, 127.031702, 126.880898, 127.028726, 126.897710, 126.910288, 127.043189, 127.071184, 127.076812, 127.045022, 126.982419, 126.840285, 127.115873, 126.885320, 127.078464, 127.057100, 127.020945, 129.068324, 129.059574, 126.927655, 127.034302, 129.106330, 126.980242, 126.945099, 129.034599, 127.054649, 127.019556, 127.053198, 127.031005, 127.058560, 127.078519, 127.056141, 129.034605, 126.888485, 129.070117, 127.057746, 126.929288, 127.054163, 129.060972],
          '위도': [37.493922, 37.505675, 37.471711, 35.159774, 37.500249, 37.515149, 37.549245, 37.562013, 37.552153, 37.538927, 37.492388, 37.480390, 37.588485, 37.504067, 37.608392, 37.503693, 37.579029, 37.580073, 37.552103, 37.545461, 37.580196, 37.562274, 37.535419, 37.527477, 37.526139, 37.648247, 37.512939, 37.517574, 35.202902, 35.144776, 37.499229, 35.150069, 35.141176, 37.479403, 37.512569, 35.123196, 37.546718, 37.553668, 37.488742, 37.493653, 37.498462, 37.556602, 37.544180, 35.111532, 37.508058, 35.085777, 37.546103, 37.483899, 37.489299, 35.143421],
          '구분': ['음식', '음식', '음식', '음식', '생활서비스', '음식', '음식', '음식', '음식', '음식', '음식', '음식', '음식', '음식', '음식', '음식', '음식', '소매', '음식', '음식', '음식', '음식', '소매', '음식', '소매', '음식', '음식', '음식', '음식', '음식', '음식', '음식', '음식', '음식', '음식', '소매', '음식', '음식', '의료', '음식', '음식', '음식', '소매', '음식', '음식', '음식', '음식', '음식', '음식', '음식']}
    ex_data = DataFrame(ex)
    # print(ex_data)

    # 위도 and 경도
    lat = ex_data['위도'].mean()
    long = ex_data['경도'].mean()

    m = folium.Map([lat, long], zoom_start=10)

    for i in ex_data.index:
        sub_lat = ex_data.loc[i, '위도']
        sub_long = ex_data.loc[i, '경도']

        title = ex_data.loc[i, '구분']

        # 지도에 데이터 찍어서 보여주기
        folium.Marker([sub_lat, sub_long], tooltip=title).add_to(m)
        # 웹페이지로 저장
        m.save(os.path.join(TEMPLATE_DIR, 'bigdata/maptest.html'))


# wordCloud
def make_wordCloud(data):
    message = ''

    for item in data:
        if 'message' in item.keys():
            message = message + re.sub(r'[^\w]', ' ', item['message'])+''

    nlp = Okt()
    # 명사 추출
    message_N = nlp.nouns(message)
    # 명사의 갯수 추출
    count = Counter(message_N)

    word_count = {}

    for tag, counts in count.most_common(80):
        if(len(str(tag)) > 1):
            word_count[tag] = counts
            # print("%s : %d" % (tag, counts))

    font_path = 'c:/Windows/fonts/malgun.ttf'
    wc = WordCloud(font_path, background_color='ivory', width=800, height=600)

    cloud = wc.generate_from_frequencies(word_count)

    plt.figure(figsize=(8, 8))
    plt.imshow(cloud)
    plt.axis('off')
    cloud.to_file('./static/images/k_wordCloud.png')
