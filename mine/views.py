from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F, Sum, Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, ListView

from mall.models import Product
from mine.models import Order, Cart
from utils import constants, tools


@login_required()
def index(request):
    """ 个人中心的首页 """
    return render(request, 'mine.html', {
        'constants': constants
    })


class OrderDetailView(DetailView):
    """ 订单详情 """
    # html的object就是这个
    model = Order
    # 指定url中的参数为下
    slug_field = 'sn'
    # 上述参数根据表中的下面数据进行搜索
    slug_url_kwarg = 'sn'
    template_name = 'order_info.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['constants'] =constants
        return context

@login_required
@transaction.atomic()
def cart_add(request, prod_uid):
    """ 添加商品到购物车 写接口 算接口不算一个页面 """
    user = request.user
    product = get_object_or_404(Product, uid=prod_uid, is_valid=True, status=constants.PRODUCT_STATUS_SELL)
    # 购买数量
    count = int(request.POST.get('count', 1))
    # 校验库存
    if product.remain_count < count:
        return HttpResponse('no')
    # 从库存中减去购买数量
    product.update_store_count(count)
    # 生成购物车记录
    # 如果已经添加到购物车，就把购买数量和价格更新
    try:
        cart = Cart.objects.get(product=product, user=user, status=constants.ORDER_STATUS_INIT)
        # 更新价格和数量
        count = cart.count + count
        cart.count = count
        cart.amount = count * cart.price
        cart.save()
    except Cart.DoesNotExist:
        # 没有加入到过购物车
        Cart.objects.create(product=product, user=user, name=product.name, img=product.img, price=product.price,
                            origin_price=product.origin_price, count=count, amount=count * product.price)
    return HttpResponse('ok')


@login_required
def cart(request):
    """ 我的购物车 """
    user = request.user
    # 购物车中的商品列表
    prod_list = user.carts.filter(status=constants.ORDER_STATUS_INIT)
    if request.method == 'POST':
        # 提交订单
        # 1.保存用户的地址快照
        default_addr = user.default_addr
        if not default_addr:
            # 消息通知
            messages.warning(request, '请选择地址信息')
            return redirect('accounts:address_list')
        # 计算订单总额
        cart_total = prod_list.aggregate(sum_amount=Sum('amount'), sum_count=Sum('count'))
        order = Order.objects.create(
            user=user,
            sn=tools.gen_trans_id(),
            buy_amount=cart_total['sum_amount'],
            buy_count=cart_total['sum_count'],
            to_user=default_addr.username,
            to_area=default_addr.get_region_format(),
            to_address=default_addr.address,
            to_phone=default_addr.phone
        )
        # 2.修改购物车的商品状态 已提交
        # 3.生成订单，关联到购物车
        prod_list.update(
            status=constants.ORDER_STATUS_SUBMIT,
            order=order
        )
        # 4.跳转到订单详情
        messages.success(request, '下单成功,请支付')
        return redirect('mine:order_detail', sn=order.sn)

    return render(request, 'cart.html', {
        'prod_list': prod_list
    })


@login_required()
def order_pay(request):
    """ 提交订单 """
    user = request.user
    sn = None
    if request.method == 'POST':
        sn = request.POST.get('sn', None)
        # 1.查询订单信息
        order = get_object_or_404(Order, sn=sn, user=user, status=constants.ORDER_STATUS_SUBMIT)
        # 2.验证积分够不够
        if order.buy_amount > user.integral:
            messages.error(request, '积分余额不足')
            return redirect('mine:order_detail', sn=sn)
        # 3.积分足够就扣积分
        user.ope_integral_account(0, order.buy_amount)
        # 4.修改订单状态
        order.status = constants.ORDER_STATUS_PAIED
        order.save()
        # 5.修改购物车关联的状态
        order.carts.all().update(status=constants.ORDER_STATUS_PAIED)
        messages.success(request, '支付成功')
    return redirect('mine:order_detail', sn=sn)


# 改用类的方法写
# @login_required()
# def order_list(request):
#     """ 我的订单列表 """
#     status = request.GET.get('status', '')
#     try:
#         status = int(status)
#     except ValueError:
#         status = ''
#     return render(request, 'order_list.html', {
#         'constants': constants,
#         'status': status
#     })


# class-based
class OrderListView(ListView):
    """ 基于类的方法来编写OrderList """
    model = Order
    template_name = 'order_list.html'

    def get_queryset(self):
        """ 查询订单 """
        status = self.request.GET.get('status', '')
        user = self.request.user
        query = Q(user=user)
        if status:
            query = query & Q(status=status)
        return Order.objects.filter(query).exclude(
            status=constants.ORDER_STATUS_DELETED
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        status = self.request.GET.get('status', '')
        try:
            status = int(status)
        except ValueError:
            status = ''
        context['status'] = status
        context['constants'] = constants
        return context


@login_required()
def prod_collect(request):
    """ 我的收藏 """
    return render(request, 'prod_collect.html')
