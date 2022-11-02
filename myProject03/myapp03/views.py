import django

# Create your views here.
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from myapp03.models import Board, Comment, Forecast, Webtoon
import math
import urllib.parse
from django.core.paginator import Paginator

from .forms import UserForm
from django.contrib.auth import authenticate, login

from myapp03 import bigdataProcess
from django.db.models.aggregates import Count
import pandas as pd
# 로그인 체크?
from django.contrib.auth.decorators import login_required

import json


# Create your views here.

UPLOAD_DIR = 'C:/Django_practice/upload/'


#################################
# webtoon
def webtoon(request):
    data = {}
    bigdataProcess.webtoon_crawing(data)
    # data
    for i in data:
        for j in data[i]:
            dto = Webtoon(webDay=i, title=j[0], writer=j[1], score=j[2])
            dto.save()

    # 검색
    word = request.GET.get('word', '')
    field = request.GET.get('field', 'title')

    if field == 'all':
        boardList = Webtoon.objects.filter(Q(title__contains=word) |
                                           Q(writer__contains=word)).order_by('-id')
    elif field == 'title':
        boardList = Webtoon.objects.filter(
            Q(title__contains=word)).order_by('-id')
    elif field == 'writer':
        boardList = Webtoon.objects.filter(
            Q(writer__contains=word)).order_by('-id')
    else:
        boardList = Webtoon.objects.all().order_by('-id')

    context = {'field': field,
               'word': word,
               'boardList': boardList}

    result = Webtoon.objects.filter(Q(title__contains=word))

    return render(request, 'bigdata/webtoon.html', {"result": result,  "context": context, "img_data": 'webtoon_wordCloud.png'})


#################################
# melon
def melon(request):
    melonList = bigdataProcess.melon_crawing()
    return render(request, 'bigdata/melon.html', {'melonList': melonList})


# weather
def weather(request):
    last_date = Forecast.objects.values('tmef').order_by('-tmef')[:1]
    print('last_date : ', len(last_date))
    weather = {}
    bigdataProcess.weather_crawing(last_date, weather)
    print("last_date query : ", str(last_date.query))
    for i in weather:
        for j in weather[i]:
            dto = Forecast(city=i, tmef=j[0], wf=j[1], tmn=j[2], tmx=j[3])
            dto.save()

    # 검색
    word = request.GET.get('word', '')

    result = Forecast.objects.filter(Q(city__contains=word))
    result_pd = Forecast.objects.filter(Q(city__contains=word)).values(
        'wf').annotate(dcount=Count('wf')).values("dcount", "wf")
    print("result_pd query : ", str(result_pd.query))

    df = pd.DataFrame(result_pd)
    image_dic = bigdataProcess.weather_make_chart(result_pd, df.wf, df.dcount)

    return render(request, 'bigdata/weather_chart.html', {"img_data": image_dic, "result": result})


# map
def map(request):
    bigdataProcess.map()
    return render(request, 'bigdata/map.html')


# wordcloud
def wordcloud(requset):
    w_path = "C:/Django_study03/myProject03/data/"
    # json 읽기
    data = json.loads(open(w_path+'4차 산업혁명.json',
                      'r', encoding='utf-8').read())
    # print(data)
    bigdataProcess.make_wordCloud(data)
    return render(requset, 'bigdata/wordchart.html', {'img_data': 'k_wordCloud.png'})
#################################

# index


def base(request):
    return render(request, 'base.html')


# write_form
@login_required(login_url='/login/')
def write_form(request):
    return render(request, 'board/insert.html')


# insert
@ csrf_exempt
def insert(request):
    fname = ''
    fsize = 0

    if 'file' in request.FILES:
        file = request.FILES['file']
        fname = file.name
        fsize = file.size

        fp = open('%s%s' % (UPLOAD_DIR, fname), 'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()

    dto = Board(writer=request.user,
                title=request.POST['title'],
                content=request.POST['content'],
                filename=fname,
                filesize=fsize
                )
    dto.save()
    return redirect('/')


# list
def list(request):
    page = request.GET.get('page', 1)
    word = request.GET.get('word', '')
    field = request.GET.get('field', 'title')

    # 페이지 번호 설정
    # boardCount
    if field == 'all':
        # Q
        # '__' : like랑 같다
        boardCount = Board.objects.filter(Q(writer__username__contains=word) |
                                          Q(title__contains=word) |
                                          Q(content__contains=word)).count()
    elif field == 'writer':
        boardCount = Board.objects.filter(
            Q(writer__username__contains=word)).count()
    elif field == 'title':
        boardCount = Board.objects.filter(
            Q(title__contains=word)).count()
    elif field == 'content':
        boardCount = Board.objects.filter(
            Q(content__contains=word)).count()
    else:
        boardCount = Board.objects.all().count()

    pageSize = 5    # 한 화면 게시글 수
    blockPage = 3   # 보이는 페이지 수
    currentPage = int(page)

    # 시작위치?
    start = (currentPage-1)*pageSize
    totPage = math.ceil(boardCount / pageSize)  # 전체페이지 // ceil : 올림
    startPage = math.floor((currentPage - 1)/blockPage) * \
        blockPage + 1   # floor : 버림
    endPage = startPage + blockPage - 1
    # 게시글의 전체 페이지 수 = math.ceil(게시글 수 / pageSize)

    # 마지막 페이지가 총 페이지 수 보다 클 때 마지막 페이지는 총 페이지 수의 값을 받음
    if endPage > totPage:
        endPage = totPage

    # 검색
    if field == 'all':
        boardList = Board.objects.filter(Q(writer__username__contains=word) |
                                         Q(title__contains=word) |
                                         Q(content__contains=word)).order_by('-id')[start: start + pageSize]
    elif field == 'writer':
        boardList = Board.objects.filter(
            Q(writer__username__contains=word)).order_by('-id')[start: start + pageSize]
    elif field == 'title':
        boardList = Board.objects.filter(
            Q(title__contains=word)).order_by('-id')[start: start + pageSize]
    elif field == 'content':
        boardList = Board.objects.filter(
            Q(content__contains=word)).order_by('-id')[start: start + pageSize]
    else:
        boardList = Board.objects.all().order_by(
            '-id')[start: start + pageSize]

    # dict형태
    context = {'boardList': boardList,
               'startPage': startPage,
               'blockPage': blockPage,
               'endPage': endPage,
               'totPage': totPage,
               'boardCount': boardCount,
               'currentPage': currentPage,
               'field': field,
               'word': word,
               'range': range(startPage, endPage+1)}
    return render(request, 'board/list.html', context)


# 다운로드 횟수
def download_count(request):
    id = request.GET['id']
    dto = Board.objects.get(id=id)
    dto.down_up()
    dto.save()
    count = dto.down
    # Spring에 있는 responsebody랑 같다
    # 데이터 값을 받기 위해 !!
    return JsonResponse({'id': id, 'count': count})


# 다운로드
def download(request):
    id = request.GET['id']
    dto = Board.objects.get(id=id)
    path = UPLOAD_DIR + dto.filename

    filename = urllib.parse.quote(dto.filename)
    # print('filename : ', filename)
    with open(path, 'rb') as file:
        response = HttpResponse(file.read(),
                                content_type='application/octet-stream')
        response['Content-Disposition'] = "attachment;filename*=UTF-8 '' {0}".format(
            filename)
    return response


# list_page
def list_page(request):
    page = request.GET.get('page', 1)
    word = request.GET.get('word', '')

    boardCount = Board.objects.filter(Q(writer__username__contains=word) |
                                      Q(title__contains=word) |
                                      Q(content__contains=word)).count()

    boardList = Board.objects.filter(Q(writer__username__contains=word) |
                                     Q(title__contains=word) |
                                     Q(content__contains=word)).order_by('-id')

    pageSize = 5

    # 페이징처리
    paginator = Paginator(boardList, pageSize)  # import
    page_obj = paginator.get_page(page)
    print('boardCount : ', boardCount)

    rowNo = boardCount - (int(page)-1) * pageSize  # 페이지 시작점 13 / 13- 5 / 13-10

    context = {'page_list': page_obj,
               'page': page,
               'word': word,
               'rowNo': rowNo,
               'boardCount': boardCount}
    return render(request, 'board/list_page.html', context)


# detail
def detail(request, board_id):
    dto = Board.objects.get(id=board_id)
    dto.hit_up()
    dto.save()
    return render(request, 'board/detail.html', {'dto': dto})


# update_form
def update_form(request, board_id):
    dto = Board.objects.get(id=board_id)
    return render(request, 'board/update.html', {'dto': dto})


# update
@ csrf_exempt
def update(request):

    # 파일을 업로드를 했었을 경우
    id = request.POST['id']
    dto = Board.objects.get(id=id)
    fname = dto.filename
    fsize = dto.filesize
    hitcount = dto.hit

    # 파일을 업로드를 안했을 경우 파일객체를 받아옴
    if 'file' in request.FILES:
        file = request.FILES['file']
        fname = file.name
        fsize = file.size

        fp = open('%s%s' % (UPLOAD_DIR, fname), 'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()

    update_dto = Board(id,
                       writer=request.user,
                       title=request.POST['title'],
                       content=request.POST['content'],
                       filename=fname,
                       filesize=fsize,
                       hit=hitcount
                       )
    update_dto.save()

    return redirect('/list')


# delete
def delete(request, board_id):
    dto = Board.objects.get(id=board_id)
    dto.delete()
    return redirect('/list')


# comment_insert
@ csrf_exempt
@login_required(login_url='/login/')
def comment_insert(request):
    id = request.POST['id']
    board = get_object_or_404(Board, pk=id)
    dto = Comment(writer=request.user,
                  content=request.POST['content'], board=board)
    dto.save()
    return redirect('/detail/'+id)


#################################
# sign up
def signup(request):
    if request.method == "POST":    # 회원가입 insert
        form = UserForm(request.POST)
        if form.is_valid():
            print('signup POST valid')
            form.save()

            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)

            login(request, user)
            return redirect('/')
        else:
            print('signup POST un_valid')
    else:  # 회원가입폼으로
        form = UserForm()

    return render(request, 'common/signup.html', {'form': form})
