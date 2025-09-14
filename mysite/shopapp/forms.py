from django import forms

from .models import Order, Product
from .widgets import MultipleFileField


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("name", "price", "description", "discount", "preview")

    images = MultipleFileField()



class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("delivery_address", "promocode", "user", "products")
        widgets = {
            "products": forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['products'].queryset = Product.objects.filter(archived=False)


class CSVImportForm(forms.Form):
    csv_file = forms.FileField()
