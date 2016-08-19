from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from .forms import PostForm
from django.template import RequestContext
    
from functions import web_login_required

#using Jinja2
#from jinja2 import Environment
#from jinja_helper import render_to_response

#load db
from .models import *

#load forms 
from model_forms import *

#others
#from types import *

import sys
import os
import datetime

# Create your views here.

def post_list(request):
    posts = Post.objects.filter(published_date__isnull=False).order_by('published_date')
    return render(request, 'pools/post_list.html', {'posts': posts})

def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            #return redirect('blog.views.post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'pools/post_edit.html', {'form': form})


def index(request):
    #加入頁次計算，每頁5筆
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    prepage = ''
    nextpage = ''
    
    msg = u'站台消息'
    link_list = Paginator(messages.objects.all().order_by('-start_date'), 5)
    pList = link_list.page(int(page))
    has_previous = pList.has_previous()
    pages = link_list.num_pages
    if has_previous:
        prepage = int(page)-1
    has_next = pList.has_next()
    if has_next:
        nextpage = int(page)+1
    return render_to_response('home.html',{'msg':msg,'messgs':pList, 'pre':prepage,'next':nextpage})

#使用者註冊
def signin(request):
    #if logined...
    try:
        if request.session['usrid']:
            return HttpResponseRedirect('/')
    except:
        pass
    msg = u'使用者註冊'
    cForm = whoAdminForm()
    if request.method=="POST":
        if request.POST['cmdSubmit']:
            #要自行輸入表格
            whoObj = who()
            whoObj.s_id = request.POST['s_id']
            whoObj.name = request.POST['name']
            whoObj.department = request.POST['department']
            whoObj.email = request.POST['email']
            whoObj.phone = request.POST['phone']
            whoObj.passwd = request.POST['Passwd']
            whoObj.allowed = 1
            whoObj.br_date = request.POST['br_date']
            whoObj.save()
            msg = whoObj.name +u'會員資料已寫入'
            return render_to_response('OK.html',{'msg':msg})
    return render_to_response('register.html',{'msg':msg, 'form':cForm},context_instance=RequestContext(request))

def login(request):
    msg = 'hi, there '
    nexturl = '/'
    try:
        if request.GET['next']:
            nexturl = request.GET['next']
    except:
        pass
    if request.method == 'POST':
        #check the login info
        usr = request.POST['usrid']
        pwd = request.POST['usrpw']
        try:
            user = who.objects.get(s_id = usr, passwd = pwd)
        except:
            user = ''
        if user:
            #got the user and put the info into session
            request.session['usrid'] = user.u_id
            request.session['usrName']= user.name
            request.session['usrRight']  = 10    # 10: for normal user 
            return HttpResponseRedirect(nexturl)
        else:
            #no info, transfer to singin
            return HttpResponseRedirect('/signin/')        
    return render(request, 'login.html',{'next':nexturl,'msg':msg})
    #return render_to_response('login.html',{'next':nexturl,'msg':msg}, context_instance=RequestContext(request))

from util import *

def place_status(request):
    #加入頁次計算，每頁5筆，每個畫面１０頁
    next = request.path
    currpage = 1
    perPage = 10
    curScr = 0
    try:
        if request.GET['page']:
            currpage = int(request.GET.get('page', '1'))
            perPage = int(request.GET.get('perpage','0'))
    except:
        pass
    try:
        if request.GET['preScr']:
            curScr = int(request.GET.get('preScr','0'))
            currpage = int(curScr)*10+1
            perPage = int(request.GET['perpage'])
    except:
        pass
    try:
        if request.GET['nextScr']:
            nextScr = int(request.GET['nextScr'])
            currpage = int(nextScr)*10+1
            perPage = int(request.GET['perpage'])
    except:
        nextScr = 1
    msg = u'場地使用情形'
    resObj = reserve.objects.all().order_by('-start_date')
    perScr = 10
    if request.method == 'POST':
        #got the perpage
        if request.POST['perpage']:
            perPage = int(request.POST['perpage']) 
    
    curScrObj = pageNav(resObj,currpage,perScr,perPage)
    
    return render_to_response('status.html',{'msg':msg,'messgs':curScrObj['pageObj'], 'navobj':curScrObj,'next':next, 'range': range(curScrObj['stpage'],curScrObj['edpage']+1)})

def details(request):
    nexturl = '/'
    try:
        if request.GET['next']:
            nexturl = request.GET['next']
    except:
        pass
    #detail for reserved place...
    try:
        if request.GET['rid']:
            rid = request.GET['rid']
    except:
        rid = 1
    revObj = reserve.objects.get(r_id =rid)
    
    #need to prepare the regulation rule...
    dspObj={}
    dspObj['department']=revObj.u_id.department
    dspObj['usrname']=revObj.u_id.name
    dspObj['usrphone']=revObj.u_id.phone
    dspObj['start_date']=revObj.start_date
    dspObj['end_date']=revObj.end_date
    dspObj['name']=revObj.place_no.name
    rule = revObj.place_no.regulation
    dspRule = DspRule(ParseRule(rule))
    dspObj['regulation']=dspRule
    dspObj['application']=revObj.application
    dspObj['approve']=revObj.approve
    dspObj['remarks']=revObj.remarks
    
    msg = u'顯示細項資料'
    return render_to_response('details.html',{'dspobj':dspObj,'msg':msg,'next':nexturl})

@web_login_required
def apply(request):
    '''
    message...
    '''
    msg = u'場地預約申請'
    #prepare the user's info
    usrid = request.session['usrid']
    usrinfo = {}
    usrinfo['usrid']= usrid
    usrinfo['usrRight']=request.session['usrRight']
    try:
        usrObj = who.objects.get(u_id = usrid)
        if usrObj:
            usrinfo['name'] =usrObj.name
            usrinfo['phone']=usrObj.phone
            usrinfo['dept'] = usrObj.department
    except:
        pass
    try:
        usrObj = members.objects.get(User_id = usrid)
        if usrObj:
            usrinfo['name'] =usrObj.User_name
            usrinfo['phone']="sys\'s phone"
            usrinfo['dept'] = "sysop"
    except:
        pass
    if request.method == 'POST':
        if request.POST['sent']:
            #ready to write back, and because had FK, only can be written maneaully...
            placeno = request.POST['location']
            placeObj = place.objects.get(place_no=placeno)
            st_date = request.POST['start_date']
            ed_date = request.POST['end_date']
            apps = request.POST['application']
            #write back
            revObj = reserve()
            revObj.u_id = usrObj
            revObj.place_no = placeObj
            revObj.approve = 1
            revObj.start_date = st_date
            revObj.end_date = ed_date
            revObj.application = apps
            revObj.save()
            
            msg = u'場地預約已寫入資料庫...'
            return render_to_response('OK.html',{'msg':msg})
    
    #prepare the place for choose
    places = place.objects.all().values('place_no','name').order_by('name')
    
    return render_to_response('apply.html',{'usrinfo':usrinfo,'places':places,'msg':msg})

#ajax function，用來檢查場地申請的場地限制
 
def place_manage(request):
    '''
    管理者功能...
    '''
    msg = u'管理者專用頁面'
    try:
        if request.session['usrid']:
            return HttpResponseRedirect('/member/')
    except:
        pass
    if request.method == 'POST':
        #check the user and redirect to /member/
        usrid = request.POST['userid']
        usrpw = request.POST['userpw']
        try:
            usrobj = members.objects.get(User_id=usrid, User_password=usrpw)
        except:
            usrobj=''
        if usrobj:
            #got it
            request.session['usrid']=usrid
            request.session['usrname']=usrobj.User_name
            request.session['usrRight']=usrobj.User_right
            return HttpResponseRedirect('/member/')
        else:
            #cannot login correctly
            msg = '登入錯誤，請查明帳號及密碼'
            return render_to_response('OK.html',{'msg':msg})
    return render(request, 'manage.html',{'msg':msg})
    #return render_to_response('manage.html',{'msg':msg})

def logout_view(request):
    try:
        del request.session['usrid']
        del request.session['usrname']
        del request.session['usrRight']
    except:
        pass
    return HttpResponseRedirect('/')

#以下為ajax functions...
#ajax function for checking the user 
def check_user(request):
    msg = ''
    m_id = request.POST['usrid']
    m_status = True
#    print m_id
    try:
        memberR = who.objects.get(s_id = m_id)
        if memberR:
            msg = u'帳號已被使用，請重新輸入'
            m_status = False            
        else:
            msg = u'此帳號可使用'
    except:
        msg = u'此帳號可使用'
    result={}
    result['msg']=msg
    result['m_status']=m_status
    response = HttpResponse(simplejson.dumps(result),mimetype="Content-Type='application/javascript'")
    return response
#    return render_to_response('member_check_result.htm',
#      {'msg':msg,'chk_status':m_status})

def get_placeinfo(request):
    '''
    ajax function for get the rule of the place
    '''
    msg = ''
    p_no = request.POST['placeno']
    try:
        placeObj = place.objects.get(place_no=p_no)
        if placeObj:
            rule = placeObj.regulation
            dspRule = DspRule(ParseRule(rule))
    except:
        dspRule=''
    response = HttpResponse(simplejson.dumps(dspRule),mimetype="Content-Type='application/javascript'")
    return response

#check the timing ...
def chk_place_ready(request):
    '''
    ajax function for get the rule of the place
    '''
    from datetime import datetime, timedelta
    from util import *
    
    result = {}   #put the result here...
    dStart=''
    dEnd=''
    usrRight=''
    lCheck = 1
    
    try:
        usrid = request.POST['usrid']
        dStart = request.POST['dStart']+':00'  #因為傳入值並沒 '秒', 要自行加上
        dEnd = request.POST['dEnd']+':00'
        usrRight = request.POST['usrRight']
        usrDept = request.POST['usrDept']
        placeno = request.POST['placeno']
    except:
        pass
    #用來檢查的法則...
    if usrRight == 99:
        #don't check any rull, just pass
        result['msg']='管理者專用，不會做任何檢查....'
    else:
        #check if any other occupied...
        revObj=reserve.objects.select_related().filter(place_no = placeno,approve = 1)
        if revObj:
            for revplace in revObj:
                ot = revplace.start_date
                oe = revplace.end_date
                if not compDateBlock(dStart,dEnd,ot,oe):
                    lCheck = -1
                    break
        #the 3rd part, check the regulation...
        placeObj = place.objects.get(place_no = placeno)
        if placeObj:
            rules = ParseRule(placeObj.regulation)
            result['checkpoint2'] = rules
            if rules:
                for rule in rules:
                    if rule['type'] == '1':
                        #per week, so need to find out whether in the same week
                        nWeek = int(rule['week']) -1
                        objNow = datetime.strptime(dStart,"%Y-%m-%d %H:%M:%S")
                        #檢查是否同一天
                        result['checkingmsg']= str(nWeek) +'/'+str(objNow.weekday())
                        if nWeek == objNow.weekday():
                            #在同一天，然後再做時段比較
                            out = objNow.date().isoformat()
                            nowSt =out + ' '+rule['st_time']+':00'
                            out = objNow.date().isoformat()
                            nowEd = out + ' '+rule['ed_time']+':00'
                            if not compDateBlock(dStart,dEnd,nowSt,nowEd):
                                lCheck = -3
                                break
                    elif rule['type'] == '2':
                        #per day
                        objNow = datetime.strptime(dStart,"%Y-%m-%d %H:%M:%S")
                        result['checkingmsg']= objNow()
                        out = objNow.date().isoformat()
                        nowSt = out + ' '+rule['st_time']+':00'
                        out = objNow.date().isoformat()
                        nowEd = out + ' '+rule['ed_time']+':00'
                        if not compDateBlock(dStart,dEnd,nowSt,nowEd):
                            lCheck = -4
                            break
        #check the group limit within 4 hrs
        #找出群組場地
        placeObj = place.objects.get(place_no=placeno)
        lstPlaceNo = []
        lstPlaceNo.append(placeno)
        if placeObj:
            pgroups=placeObj.place_groups
            pgrpObj = place.objects.filter(place_groups = pgroups)
            if pgrpObj:
                for item in pgrpObj:
                    lstPlaceNo.append(item.place_no)
        #計算使用的總時數，因為每個單位每週有４小時的場地預約限制
        if lstPlaceNo:
            result['checkpoint3']= 'grouping places'
        usrRev=[]
        users = who.objects.filter(department=usrDept)
        if users:
            for user in users:
                revObj = reserve.objects.select_related().filter(u_id = user, approve=1)
                if revObj:
                    for revplace in revObj:
                        revR ={}
                        if revplace.place_no in lstPlaceNo:
                            #in the place groups
                            revR['start_date']= revplace.start_date
                            revR['end_date']= revplace.end_date
                            revR['user_id']= revplace.u_id
                            usrRev.append(revR)
        if usrRev:
            result['checkpoint4']= 'had many users'
        wkStart = WeekStart(dStart)
        wkEnd = WeekEnd(dStart)
        Hours = 0
        for item in usrRev:
            st_date = item['start_date']
            st_date = datetime.strptime(st_date,"%Y-%m-%d %H:%M:%S")
            if st_date > wkStart and st_date < wkEnd:
                #within the same week
                ed_date = datetime.strptime(item['end_date'],"%Y-%m-%d %H:%M:%S")
                timeS =ed_date - st_date
                Hours += timeS.seconds/3600
        # the hours for this time
        nowSt = datetime.strptime(dStart,"%Y-%m-%d %H:%M:%S")
        nowEd = datetime.strptime(dEnd,"%Y-%m-%d %H:%M:%S")
        timeS = nowEd - nowSt
        Hours += timeS.seconds/3600
        if Hours > 4:
            lCheck = -2
        
        result['key']= lCheck
        if lCheck == -1:
            result['msg'] = u'場地已被申請...'
        elif lCheck == -2:
            result['msg'] = u'超過每個單位每週至多4小時限制...'
        elif lCheck == -3:
            result['msg']= u'違反場地限制（每週)...'
        elif lCheck == -4:
            result['msg']= u'違反場地限制（每天)...'
        else:
            result['msg']= u'資料沒問題'
    
    response = HttpResponse(simplejson.dumps(result),mimetype="Content-Type='application/javascript'")
    return response