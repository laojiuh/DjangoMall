import re

from django import forms
from django.contrib.auth import authenticate
# from django.contrib.auth.models import User
from accounts.models import User, UserAddress
from django.contrib.auth import login
from django.shortcuts import redirect

from utils.verify import VerifyCode


class LoginForm(forms.Form):
    """ 自定义表单 """
    SEX_CHOICES = (
        (1, '男'),
        (2, '女')
    )

    username = forms.CharField(label='用户名', max_length=64)
    email = forms.EmailField(label='电子邮箱')
    sex = forms.ChoiceField(label='性别', choices=SEX_CHOICES)
    birth = forms.DateField(label='生日')
    remark = forms.CharField(label='备注', max_length=200, widget=forms.Textarea)
    age = forms.IntegerField(label='年龄', widget=forms.NumberInput)
    password = forms.CharField(label='密码', widget=forms.PasswordInput)


class UserLoginForm(forms.Form):
    """ 用户登录表单 """
    username = forms.CharField(label='用户名', max_length=64, error_messages={
        'required': '请输入用户名'
    })
    password = forms.CharField(label='密码', max_length=64, widget=forms.PasswordInput,
                               error_messages={
                                   'required': '请输入密码'
                               })
    verity_code = forms.CharField(label='验证码', max_length=4, error_messages={
        'required': '请输入验证码'
    })

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    # def clean_username(self):
    #     """ 验证用户名 hook 钩子函数"""
    #     username = self.cleaned_data['username']
    #     print(username)
    #     # 判断用户名是否为手机号码
    #     pattern = r'^0{0,1}1[0-9]{10}$'
    #     if not re.search(pattern, username):
    #         raise forms.ValidationError('请输入正确的手机号码')
    #     return username

    def clean_verity_code(self):
        """ 验证用户输入的验证码是否正确 """
        verity_code = self.cleaned_data['verity_code']
        if not verity_code:
            raise forms.ValidationError('请输入验证码')
        client = VerifyCode(self.request)
        if not client.validate_code(verity_code):
            raise forms.ValidationError('您输入的验证码不正确')
        return verity_code

    def clean(self):
        """ 多字段的验证 """
        cleaned_data = super().clean()
        # 如果username丢失只会返回password
        print(cleaned_data)
        # 上面username返回异常，字段丢失了，用下面这种[]方法直接报错
        # username = cleaned_data['username']
        # 用这种方法取不到就返回None
        username = cleaned_data.get('username', None)
        password = cleaned_data.get('password', None)
        if username and password:
            # 查询用户名匹配的用户
            # -------------------------------------
            # 自己创建的用户库的查询
            count = User.objects.filter(username=username).count()
            if count == 0:
                raise forms.ValidationError('用户名不存在')
            # else:
            #     # 查询用户名和密码匹配的用户
            #     count = User.objects.filter(username=username, password=password).count()
            #     if count == 0:
            #         raise forms.ValidationError('密码错误')
            # -----------------------------------------

            if not authenticate(self.request, username=username, password=password):
                raise forms.ValidationError('密码错误')

        return cleaned_data


class UserRegisterForm(forms.Form):
    """ 用户注册表单 """
    username = forms.CharField(label='用户名', max_length=64, error_messages={
        'required': '请输入用户名'
    })
    nickname = forms.CharField(label='昵称', max_length=64, error_messages={
        'required': '请输入昵称'
    })
    password = forms.CharField(label='密码', max_length=64, widget=forms.PasswordInput, error_messages={
        'required': '请输入密码'
    })
    password2 = forms.CharField(label='再次密码', max_length=64, widget=forms.PasswordInput, error_messages={
        'required': '请再次输入密码'
    })
    verity_code = forms.CharField(label='验证码', max_length=4, error_messages={
        'required': '请输入验证码'
    })

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_username(self):
        """ 验证用户名是否已经注册 """
        data = self.cleaned_data['username']
        # print(data)
        if User.objects.filter(username=data).exists():
            raise forms.ValidationError('用户名已存在')
        return data

    def clean_verity_code(self):
        """ 验证用户输入的验证码是否正确 """
        verity_code = self.cleaned_data['verity_code']
        if not verity_code:
            raise forms.ValidationError('请输入验证码')
        client = VerifyCode(self.request)
        if not client.validate_code(verity_code):
            raise forms.ValidationError('您输入的验证码不正确')
        return verity_code

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password', None)
        password2 = cleaned_data.get('password2', None)
        if password and password2:
            if password != password2:
                raise forms.ValidationError('两次密码输入不一致')
        return cleaned_data

    def register(self):
        """ 注册的方法 """
        data = self.cleaned_data
        # print(data)
        # 1.创建用户
        User.objects.create_user(username=data['username'], password=data['password'],
                                 level=0, nickname=['nickname'])
        # email = '{}@qq.com'.format(data['username'])
        # 2.自动登录

        user = authenticate(self.request, username=data['username'], password=data['password'])
        login(self.request, user)
        return user


class UserAddressForm(forms.ModelForm):
    """地址新增|修改"""

    region = forms.CharField(label='大区域选项', max_length=64, required=True, error_messages={
        'required': '请选择地址'
    })

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    class Meta:
        model = UserAddress
        fields = ['address', 'username', 'phone', 'is_default']
        widgets = {
            'is_default': forms.CheckboxInput(attrs={
                'class': 'weui-switch'
            })
        }

    def clean_phone(self):
        """ 验证用户输入的手机号码 """
        phone = self.cleaned_data['phone']
        # 判断用户名是否为手机号码
        pattern = r'^0{0,1}1[0-9]{10}$'
        if not re.search(pattern, phone):
            raise forms.ValidationError('请输入正确的手机号码')
        return phone

    def clean(self):
        cleaned_data = super().clean()
        # 查询当前登录的用户地址数据
        addr_list = UserAddress.objects.filter(is_valid=True, user=self.request.user)
        if addr_list.count() > 20:
            raise forms.ValidationError('最多只能添加20个地址')
        return cleaned_data

    def save(self, commit=True):
        obj = super().save(commit=False)
        region = self.cleaned_data['region']
        # 省市区的数据
        (province, city, area) = region.split(' ')
        obj.province = province
        obj.city = city
        obj.area = area
        obj.user = self.request.user

        # 修改的时候，如果已经有了默认地址，当前也勾选了默认地址
        # 我们需要把以前的地址改为非默认地址
        if self.cleaned_data['is_default']:
            UserAddress.objects.filter(is_valid=True, user=self.request.user,
                                       is_default=True).update(is_default=False)

        obj.save()
