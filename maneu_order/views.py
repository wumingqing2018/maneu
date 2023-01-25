import datetime
import json

from django.shortcuts import render, reverse, HttpResponseRedirect

from common import common
from common.checkMobile import judge_pc_or_mobile
from maneu_alterSales import service as alter_server
from maneu_order import service


def order_list(request):
    """
    订单列表功能
    在session获取商家id 通过商家id查找订单列表
    """
    if request.POST:
        time = request.POST.get('time')
        date = datetime.datetime.strptime(time, '%Y-%m-%d')
        down_day = (date + datetime.timedelta(days=+1)).strftime("%Y-%m-%d")
        up_day = (date + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
    else:
        time = common.today()
        date = datetime.datetime.strptime(time, '%Y-%m-%d')
        down_day = (date + datetime.timedelta(days=+1)).strftime("%Y-%m-%d")
        up_day = (date + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
    orderlist = service.ManeuOrderV2_today(users_id=request.session.get('id'), time=time)  # 查找今日订单
    return render(request, 'maneu_order/order_list.html', {'orderlist': orderlist, 'time': time, 'up_day': up_day, 'down_day': down_day})


def order_delete(request):
    order_id = request.session.get('order_id')
    users_id = request.session.get('id')
    order = service.ManeuOrderV2_id(order_id=order_id, users_id=users_id)
    if order:
        store = service.ManeuStore_delete(id=order.store_id)
        visionsolutions = service.ManeuVisionSolutions_delete(id=order.visionsolutions_id)
        subjectiverefraction = service.ManeuSubjectiveRefraction_delete(id=order.subjectiverefraction_id)
        afterSales = service.ManeuAfterSales_delete(order_id=order_id)
        order = service.ManeuOrderV2_delete(users_id=users_id, id=order_id)
    return HttpResponseRedirect(reverse('maneu_order:order_list'))


def order_detail(request):
    """
    查看订单详情
    校验请求模式 GET 校验order_id是否符合
    true
        渲染order_detail页面并传输参数order_id
    false
        渲染error页面并传输错误参数
    """
    try:
        order_id = request.POST['order_id']
    except:
        order_id = request.session.get('order_id')
    order = service.ManeuOrderV2_id(order_id=order_id, users_id=request.session.get('id'))
    if order:
        users = service.ManeuUsers_id(id=order.users_id)
        guess = service.ManeuGuess_id(id=order.guess_id)
        store = service.ManeuStore_OrderID(OrderID=order.id)
        visionsolutions = service.ManeuVisionSolutions_orderID(order_id=order.id)
        if store==None:
            service.ManeuStore_update_orderID(orderID=order.id, id=order.store_id)
            store = service.ManeuStore_OrderID(OrderID=order.id)
        if visionsolutions==None:
            service.ManeuVisionSolutions_update_orderID(orderID=order.id, id=order.visionsolutions_id)
            visionsolutions = service.ManeuVisionSolutions_orderID(order_id=order.id)
        request.session['order_id'] = order_id
        ua = request.META.get("HTTP_USER_AGENT")
        mobile = judge_pc_or_mobile(ua)
        if mobile:
            return render(request, 'maneu_order/order_detail_phone.html', {'maneu_order': order, 'users': users, 'guess': guess,
                                                                        'maneu_store': json.loads(store.content),
                                                                        'visionsolutions': json.loads(visionsolutions.content),
                                                                           })
        else:
            return render(request, 'maneu_order/order_detail_pc.html', {'maneu_order': order, 'users': users, 'guess': guess,
                                                                        'maneu_store': json.loads(store.content),
                                                                        'visionsolutions': json.loads(visionsolutions.content),
                                                                        # 'subjectiverefraction': json.loads(subjectiverefraction.content)
                                                                        })
    else:
        alter_server.ManeuAfterSales_delete_order_id(order_id=order_id)
        return render(request, 'maneu/error.html', {'msg': order})


def order_search(request):
    if request.method == 'POST':
        """查找指定订单"""
        orderlist = service.ManeuOrderV2_Search(text=request.POST.get('text'), users_id=request.session.get('id'))
        return render(request, 'maneu_order/order_search.html', {'orderlist': orderlist})
    return HttpResponseRedirect(reverse('maneu_order:order_list'))


def order_insert(request):
    """添加订单"""
    if request.method == 'POST':
        order = json.loads(request.POST.get('order_json'))
        try:
            ManeuGuess_id = service.find_ManeuGuess_byPhone(phone=order['phone']).id
        except:
            ManeuGuess_id = ''
        order = service.ManeuOrderV2_insert(time=order['time'],
                                            name=order['name'],
                                            phone=order['phone'],
                                            users_id=request.session.get('id'),
                                            guess_id=ManeuGuess_id)
        ManeuStore_id = service.ManeuStore_insert(order_id=order.id, content=request.POST.get('Product_Orders'))
        ManeuVisionSolutions_id = service.ManeuVisionSolutions_insert(order_id=order.id, content=request.POST.get('Vision_Solutions'))
        if order:
            request.session['order_id'] = str(order.id)
            return HttpResponseRedirect(reverse('maneu_order:order_detail'))

    ua = request.META.get("HTTP_USER_AGENT")
    mobile = judge_pc_or_mobile(ua)
    if mobile:
        return render(request, 'maneu_order/order_insert_phone.html')
    else:
        return render(request, 'maneu_order/order_insert_pc.html')


def order_update(request):
    """更新订单"""
    order_id = request.session.get('order_id')
    users_id = request.session.get('id')
    if order_id and users_id:
        if request.method == 'GET':
            order = service.ManeuOrderV2_id(order_id=order_id, users_id=users_id)
            users = service.find_users_id(id=order.users_id)
            guess = service.find_guess_id(id=order.guess_id)
            store = service.find_store_id(id=order.store_id)
            # visionsolutions = service.ManeuVisionSolutions_id(id=order.visionsolutions_id)
            # subjectiverefraction = service.ManeuVisionSolutions_orderID(id=order.subjectiverefraction_id)
            return render(request, 'maneu_order/order_update.html', {'maneu_order': order, 'users': users, 'guess': guess,
                                                                     # 'maneu_store': json.loads(store.content),
                                                                     })
        if request.method == 'POST':
            order = service.ManeuOrderV2_id(order_id=order_id, users_id=users_id)
            ManeuGuess_id = service.ManeuGuess_update(id=order.guess_id, content=request.POST.get('Guess_information'))
            ManeuStore_id = service.ManeuStore_update(content=request.POST.get('Product_Orders'), id=order.store_id)
            ManeuVisionSolutions_id = service.ManeuVisionSolutions_update(id=order.visionsolutions_id,
                                                                          content=request.POST.get('Vision_Solutions'))
            ManeuSubjectiveRefraction_id = service.ManeuSubjectiveRefraction_update(id=order.subjectiverefraction_id,
                                                                                    content=request.POST.get(
                                                                                        'Subjective_refraction'))
            guess_content = json.loads(request.POST.get('Guess_information'))
            service.ManeuOrderV2_update(order_id=order.id,name=guess_content['guess_name'],phone=guess_content['guess_phone'], )
            return HttpResponseRedirect(reverse('maneu_order:order_detail'))
    return render(request, 'maneu/error.html', {'msg': '参数错误'})
