from django.shortcuts import HttpResponseRedirect, reverse
from django.shortcuts import render

from common import verify
from maneu_users import serivce


def user_list(request):
    """_summary_

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    return render(request, 'maneu_users/user_list.html', {'user_list': serivce.find_user_all()})


def user_detail(request):
    """_summary_

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    user_id = verify.user_id_method_get(request)
    if user_id:
        return render(request, 'maneu_users/user_detail.html', {'user': serivce.find_user(user_id)})
    else:
        return render(request, 'maneu/error.html', {'msg': "请求出错"})


def user_delete(request):
    """_summary_

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    user_id = verify.user_id_method_get(request)
    if user_id:
        serivce.user_delete(user_id)
        return user_list(request)
    else:
        return render(request, 'maneu/error.html', {'msg': "请求出错"})


def user_insert(request):
    if request.method == 'POST':
        if request.POST['gift_password'] == '214772680':
            updata = serivce.user_insert(username=request.POST['username'],
                                         nickname=request.POST['nickname'], password=request.POST['password'],
                                         phone=request.POST['phone'], email=request.POST['email'],
                                         remark=request.POST['remark'])
            print(updata)
            return HttpResponseRedirect(reverse('login'))
    return render(request, 'maneu_users/user_insert.html')


def user_updata(request):
    user_id = request.session['id']
    msg = ''
    print(request.POST)
    if request.method == 'POST':
        updata = serivce.user_update(old_password=request.POST['old_password'], user_id=user_id,
                                     nickname=request.POST['nickname'], password=request.POST['password'],
                                     phone=request.POST['phone'], email=request.POST['email'],
                                     remark=request.POST['remark'])
        print(updata)
        if updata == None:
            msg = '密码验证错误，请正确输入登录密码'
        else:
            msg = '更新成功'
    user = serivce.find_user(user_id)
    return render(request, 'maneu_users/user_updata.html', {'user': user, 'msg': msg})
