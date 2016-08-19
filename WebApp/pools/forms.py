# -*- coding: utf-8  -*- 
from django import forms

from .models import *
#overide function...
class HorizRadioRenderer(forms.RadioSelect.renderer):
    """ this overrides widget method to put radio buttons horizontally
        instead of vertically.
    """
    def render(self):
            """Outputs radios"""
            return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))
            
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text',)

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
        