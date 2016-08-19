# -*- coding: utf-8  -*- 
#這個檔案用來寫每張表格，在對應在表單上時要做的資料限制，也就是用來做資料檢查用

from django import forms
from django.db import models 
from django.forms import ModelForm
#from customwidgets  import SliderWidget,DatePickerWidget
from django.utils.safestring import mark_safe

#overide function...
class HorizRadioRenderer(forms.RadioSelect.renderer):
    """ this overrides widget method to put radio buttons horizontally
        instead of vertically.
    """
    def render(self):
            """Outputs radios"""
            return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))	

#read the tables...
from .models import *

class whoAdminForm(forms.ModelForm):
	class Meta:
		model = who
		fields=['s_id','name','email','phone','department','passwd','allowed','br_date']

class messagesAdminForm(forms.ModelForm):
	class Meta:
		model = messages
		fields =['message','start_date','end_date']

class placeAdminForm(forms.ModelForm):
	class Meta:
		model = place
		fields =['name','location','regulation','place_groups']


APPRV_CHOICES= (
	('1','核准'),
	('0','拒發'),
	('-1','其他'),
)

class reserveAdminForm(forms.ModelForm):
	approve = forms.CharField(widget=forms.RadioSelect(renderer=HorizRadioRenderer,choices=APPRV_CHOICES))
	class Meta:
		model = reserve
		fields = ['remarks','approve','start_date','end_date','application']