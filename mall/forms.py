from django import forms

from mall.models import Product


class ProductAdminForm(forms.ModelForm):
    """ 商品编辑 """

    class Meta:
        model = Product
        exclude = ['created_at', 'updated_at']

        widgets = {
            # 自定义表单的输入界面(下拉、radio)
            'types': forms.RadioSelect
        }

    def clean_price(self):
        price = self.cleaned_data['price']
        if int(price) <= 0:
            raise forms.ValidationError('销售价格不能小于0')
        return price