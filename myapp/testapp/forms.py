from django import forms
from .models import Test
from .models import Request
from .models import Requester

class TestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ( 'username', 'test_details','template')


