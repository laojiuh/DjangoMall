from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from accounts.forms import UserLoginForm, UserRegisterForm, UserAddressForm
from accounts.models import User, UserAddress
from utils import constants
from utils.verify import VerifyCode


def user_login(request):
    """ 用户登录 """
    # 如果登录是从其他页面跳转来的，会带next参数，
    # 如果有next参数，登陆完成后，需要跳转到next所对应的地址，如果没有next参数要跳转到首页
    next_url = request.GET.get('next', 'index')
    # 第一次访问URL GET 展示表单，供用户输入
    # 第二次访问URL POST
    if request.method == 'POST':
        form = UserLoginForm(request=request, data=request.POST)
        client = VerifyCode(request)
        code = request.POST.get('verity_code', None)
        rest = client.validate_code(code)
        print('验证结果', rest)
        # 表单是否通过了验证
        if form.is_valid():
            # 执行登录
            data = form.cleaned_data
            # ----------------------------------------
            # # #### 使用自定义的方式实现登录 !!!!
            # # 查询用户信息
            # user = User.objects.get(username=data['username'], password=data['password'])
            # # 设置用户id到session
            # request.session[constants.LOGIN_SESSION_ID] = user.id
            # # 登录后的跳转
            # return redirect('index')
            # --------------------------------------

            # ###使用django-auth来实现登录
            user = authenticate(request, username=data['username'], password=data['password'])
            if user is not None:
                login(request, user)
                request.session['user_id'] = user.id
                # 登录后的跳转
                return redirect(next_url)
        else:
            print(form.errors)
    else:
        form = UserLoginForm(request)
    return render(request, 'login.html', {
        'form': form,
        'next_url': next_url
    })


def user_register(request):
    """用户注册"""
    # 第一次访问URL GET 展示表单，供用户输入
    # 第二次访问URL POST
    if request.method == 'POST':
        form = UserRegisterForm(request=request, data=request.POST)
        if form.is_valid():
            # 调用注册的方法
            form.register()
            return redirect('index')
        else:
            print(form.errors)
    else:
        form = UserRegisterForm(request=request)

    return render(request, 'register.html', {
        'form': form
    })


def user_logout(request):
    """ 用户退出登录 """
    logout(request)
    return redirect('index')


@login_required
def address_list(request):
    """ 地址列表 """
    my_addr_list = UserAddress.objects.filter(user=request.user, is_valid=True)

    return render(request, 'address_list.html', {
        'my_addr_list': my_addr_list,
    })


@login_required()
def address_edit(request, pk):
    """ 地址的修改和编辑 """
    user = request.user
    addr = None
    initial = {}
    # 如果pk是数字则修改地址信息
    if pk.isdigit():
        # 查询相关的地址信息
        addr = get_object_or_404(UserAddress, pk=pk, user=user, is_valid=True)
        initial['region'] = addr.get_region_format()
    if request.method == 'POST':
        form = UserAddressForm(request=request, data=request.POST, instance=addr, initial=initial)
        if form.is_valid():
            # 保存到数据库
            form.save()
            return redirect('accounts:address_list')
    else:
        form = UserAddressForm(request=request, instance=addr, initial=initial)
    return render(request, 'address_edit.html', {
        'form': form
    })


@login_required()
def address_delete(request, pk):
    """ 删除地址 """
    addr = get_object_or_404(UserAddress, pk=pk, is_valid=True, user=request.user)
    addr.is_valid = False
    addr.save()
    return HttpResponse('ok')
