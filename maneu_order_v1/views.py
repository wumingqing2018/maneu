from django.shortcuts import HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import reverse

from common import verify
from common import common
from common import excel
from maneu_order_v1 import service
from maneu_order_v1.forms.BatchInsertForm import BatchInsertForm
import datetime
import uuid


def index(request):
    list = service.batch_all(admin_id=request.session.get('id'))  # 查找今日订单
    return render(request, 'maneu_order_v1/index.html', {'list': list})


def detail(request):
    if request.GET.get('id'):
        order = service.batch_detail(id=request.GET.get('id'))
        return render(request, 'maneu_order_v1/detail.html', {'order': order})
    else:
        return HttpResponseRedirect(reverse('maneu_order_v1:index'))


def delete(request):
    if request.GET.get('id'):
        # excel.excel_remove(order_id='新建 XLSX 工作表.xlsx')
        service.batch_delete(id=request.GET.get('id'))
    return HttpResponseRedirect(reverse('maneu_order_v1:index'))


def insert(request):
    msg = None
    if request.method == 'POST':
        form = BatchInsertForm(request.POST)
        xlsx = request.FILES.get('excel')
        if form.is_valid() and excel:
            order = excel.excel_save(excel=xlsx, order_id=uuid.uuid1())
            print(service.batch_insert(form.clean(), admin_id=request.session.get('id'), contents=order))
            return index(request)
        msg = '参数错误'
    return render(request, 'maneu_order_v1/insert.html', {'msg': msg})


def search(request):
    """查找指定订单"""
    date = verify.date_method_post(request)
    if date:
        orderlist = service.find_batch_date(date=date)  # 查找今日订单
        return render(request, 'maneu_order_v1/index.html', {'orderlist': orderlist})
    return HttpResponseRedirect(reverse('maneu_order_v2:order_list'))
