import datetime
import json

from django.shortcuts import render, HttpResponseRedirect, reverse

from common import common
from common import verify
from maneu_guest import service
from maneu_order_v2 import service as orderService
from maneu_admin import serivce as usersService


def index(request):
    if request.GET.get('time'):
        time = request.GET.get('time')
    else:
        time = common.today()
    list = service.guess_time(time=time, admin_id=request.session.get('id'))
    date = datetime.datetime.strptime(time, '%Y-%m-%d')
    down_day = (date + datetime.timedelta(days=+1)).strftime("%Y-%m-%d")
    up_day = (date + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
    return render(request, 'maneu_guest/index.html', {'list': list,
                                                       'time': time,
                                                       'down_day': down_day,
                                                       'up_day': up_day})


def detail(request):
    guess = service.guess_id(id=request.POST.get('id'))
    users = usersService.find_user(admin_id=request.session.get('id'))
    Subjective = service.subjectiverefraction_guessID(guessid=guess.id)
    subjectiverefraction = json.loads(Subjective.content)
    try:
        clientAge = int(guess.age)
        if clientAge > 20:
            stand_ax = '24.0'
        else:
            data = ['16.2', '17.0', '17.7', '18.2', '18.7', '19.1', '19.6', '20.0', '20.3', '20.7', '21.1', '21.6',
                    '22.0', '22.4', '22.7', '23.0', '23.3', '23.5', '23.7', '23.8', '24.0', '24.0', ]
            stand_ax = data[clientAge - 1]
    except:
        stand_ax = '24.0'

    if verify.judge_pc_or_mobile(ua=request.META.get("HTTP_USER_AGENT")):
        return render(request, 'maneu_guest/detail_phone.html', {'guess': guess,
                                                                  'users': users,
                                                                  'subjectiverefraction': subjectiverefraction,
                                                                  'stand_ax': stand_ax,
                                                                  'list_r': subjectiverefraction['OD_AL'],
                                                                  'list_l': subjectiverefraction['OS_AL']})
    else:
        return render(request, 'maneu_guest/detail_pc.html', {'guess': guess,
                                                               'users': users,
                                                               'subjectiverefraction': subjectiverefraction,
                                                               'stand_ax': stand_ax,
                                                               'list_r': subjectiverefraction['OD_AL'],
                                                               'list_l': subjectiverefraction['OS_AL']})

def detail_phone(request):
    guess = service.guess_phone(phone=request.POST.get('phone'))
    users = usersService.find_user(admin_id=request.session.get('id'))
    Subjective = service.subjectiverefraction_id(id=guess.subjective_id)
    if Subjective:
        subjectiverefraction = json.loads(Subjective.content)
    else:
        subjectiverefraction = {}
        subjectiverefraction['OD_AL'] = ''
        subjectiverefraction['OS_AL'] = ''

    try:
        clientAge = int(guess.age)
        if clientAge > 20:
            stand_ax = '24.0'
        else:
            data = ['16.2', '17.0', '17.7', '18.2', '18.7', '19.1', '19.6', '20.0', '20.3', '20.7', '21.1', '21.6',
                    '22.0', '22.4', '22.7', '23.0', '23.3', '23.5', '23.7', '23.8', '24.0', '24.0', ]
            stand_ax = data[clientAge - 1]
    except:
        stand_ax = '24.0'

    if verify.judge_pc_or_mobile(ua=request.META.get("HTTP_USER_AGENT")):
        return render(request, 'maneu_guest/detail_phone.html', {'guess': guess,
                                                                  'users': users,
                                                                  'subjectiverefraction': subjectiverefraction,
                                                                  'stand_ax': stand_ax,
                                                                  'list_r': subjectiverefraction['OD_AL'],
                                                                  'list_l': subjectiverefraction['OS_AL']})
    else:
        return render(request, 'maneu_guest/detail_pc.html', {'guess': guess,
                                                               'users': users,
                                                               'subjectiverefraction': subjectiverefraction,
                                                               'stand_ax': stand_ax,
                                                               'list_r': subjectiverefraction['OD_AL'],
                                                               'list_l': subjectiverefraction['OS_AL']})


def insert(request):
    today = common.today()
    if request.method == 'POST':
        ManeuGuess = service.guess_insert(time=today, contents=request.POST.get('Guess_information'), admin_id=request.session.get('id'))
        ManeuSubjectiveRefraction = service.subjectiverefraction_insert(guess_id=ManeuGuess.id, content=request.POST.get('Subjective_refraction'))
        return HttpResponseRedirect(reverse('maneu_guest:index'))
    return render(request, 'maneu_guest/insert.html', {'today': today})


def delete(request):
    if request.method == 'POST':
        service.guess_delete(id=request.POST.get('id'))
    return HttpResponseRedirect(reverse('maneu_guest:index'))


def update(request):
    if request.method == 'GET':
        guess = service.guess_id(id=request.GET.get('id'))
        Subjective = service.subjectiverefraction_id(id=guess.subjective_id)
        subjectiverefraction = json.loads(Subjective.content)
        return render(request, 'maneu_guest/update.html', {'guess': guess, 'Subjective': subjectiverefraction})
    if request.method == 'POST':
        id = service.guess_id(id=request.POST.get('id')).subjective_id
        guess = service.guess_update(id=request.POST.get('id'), content=request.POST.get('Guess_information'))
        Subjective = service.subjective_update(id=id, content=request.POST.get('Subjective_refraction'))
    return HttpResponseRedirect(reverse('maneu_guest:index'))


def search(request):
    """查找指定订单"""
    if request.method == 'POST':
        orderlist = service.guess_search(text=request.POST.get('text'), admin_id=request.session.get('id'))
        return render(request, 'maneu_guest/search.html', {'orderlist': orderlist})
    else:
        return HttpResponseRedirect(reverse('maneu_guest:index'))


def order_list(request):
    if request.method == 'POST':
        guess_id = request.POST.get('id')
        guess_phone = request.POST.get('phone')
        orderlist = orderService.find_order_phone(phone=guess_phone)
        return render(request, 'maneu_guest/orderList.html', {'orderlist': orderlist, 'guess_id': guess_id})
    return HttpResponseRedirect(reverse('maneu_guest:index'))
