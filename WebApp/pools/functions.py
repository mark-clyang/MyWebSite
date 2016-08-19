# encoding: utf-8
'''
 這個功能是在每個function 之前加入可以檢測是否登入的@敍述，寫法有點難懂，需要時間來理解。
 不過很好用，可以在每一個需要驗證的頁面之前加入，非常類似之前在php coding 時，所寫的header.php
 在這裡，只要是沒登入系統的，會直轉向/login/，而且將目前所在的路徑傳過去。
 若是已登入，則直接打開該url, 亦即 view_function.
 
'''
from django.http import HttpResponse
from django.http import HttpResponseRedirect

#import simplejson

def web_login_required(view_function):
    def wrap(request, *arguments, **keywords):
        try:
            if request.session['usrid']:
                return view_function(request, *arguments, **keywords)
        except:
            pass
        return HttpResponseRedirect('/login/?next=%s' % request.path)
    wrap.__doc__ = view_function.__doc__
    wrap.__dict__ = view_function.__dict__
    return wrap
