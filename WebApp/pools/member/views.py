# encoding: utf-8
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
#from django.utils import simplejson
from pools.functions import web_login_required
# encoding: utf-8
'''

'''

#using Jinja2
#from jinja2 import Environment
#from jinja_helper import render_to_response

#load db
from pools.models import *

#load forms 
from pools.model_forms import *

#others
from types import *

import sys
import os
import datetime

def droptables(tblname):
	'''delete the table contents
	'''
	from db import models
	tbl = getattr(models,tblname)
	stR = tbl.objects.all()
	for m in stR:
		m.delete()

def tbl_write(flname,tblname):
	#import the tables...
	from db import models
	import datetime
	
	path = os.path.join(os.path.split(__file__)[0],flname)
	fl = open(path,'rb')
	idx = 0
	for line in fl.readlines():
		line = line.replace('"', '').strip()
		if idx == 0:
			fields = line.split(",")
		else:
			item = line.split(",")
			tbl = getattr(models,tblname)
			tmp_inst = tbl()
			ndx = 0
			for field in fields:
				fdtype = tmp_inst._meta.get_field(field).get_internal_type() 
				if item[ndx]:
						if fdtype == 'AutoField' or fdtype == 'BooleanField' or fdtype =='IntegerField':
							ins_value = int(item[ndx])
						elif fdtype == 'CharField':
							ins_value = item[ndx]
						elif fdtype == 'TextField':
							ins_value = item[ndx]
						elif fdtype == 'DateField':
							ins_value = item[ndx]
						elif fdtype == 'DateTimeField':
							dateObj =datetime.datetime.strptime(item[ndx],'%m-%d-%Y; %H:%M')
							dateS = datetime.datetime.strftime(dateObj,'%Y-%m-%d %H:%M')
							ins_value = dateS
						elif fdtype == 'ForeignKey':
							if field == 'place_no':
								fkobj = getattr(models, 'place')
								fkinst = fkobj.objects.get(place_no = int(item[ndx]))
							elif field == 'u_id':
								fkobj = getattr(models, 'who')
								fkinst = fkobj.objects.get(u_id = int(item[ndx]))
							ins_value = fkinst
						else:
							ndx = ndx + 1
							continue
						setattr(tmp_inst, field, ins_value )
				ndx = ndx + 1
			tmp_inst.save()
		idx = idx + 1
	fl.close()
	
def tbl_inserts(request):
	'''
	this function: 用來將所有資料回寫到資料表中
	'''
	#try to write 
	#droptables('place')
	#tbl_write('place.csv','place')
	#droptables('who')
	#tbl_write('who.csv','who')
	#droptables('reserve')
	
	#tbl_write('reserve.csv','reserve')
	#tbl_write('messages.csv','messages')
	tbl_write('User.csv','members')
	msg = u'資料寫入完成...'
	return render_to_response('OK.html',{'msg':msg})

def index(request):
	'''
	main screen for admin
	'''
	try:
		if request.session['usrid']:
			pass
		else:
			return HttpResponseRedirect('/place_manage/')
	except:
		return HttpResponseRedirect('/place_manage/')
	
	try:
		usrRight = request.session['usrRight']
	except:
		usrRight = 0
	if usrRight != 99:
		msg = u'無管理者權限...'
		return render_to_response('OK.html',{'msg':msg})
	
	msg = u'管理者功能主頁'
	
	return render_to_response('/member/index.htm',{'msg':msg})

def message(request):
	'''
	發佈消息
	'''
	msg = u'發佈消息'
	cForm = messagesAdminForm()
	if request.method == 'POST':
		#valid the value
		cForm = messagesAdminForm(request.POST)
		if cForm.is_valid():
			cForm.save()
			msg = u'消息發佈成功...'
			return render_to_response('OK.html',{'msg':msg})
	return render_to_response('/member/message.html',{'msg':msg,'form':cForm})

def place_add(request):
	'''
	新增場地
	'''
	msg = u'新增場地及使用規則'
	if request.method == 'POST':
		if request.POST['submit']:
			placeobj = place()
			placeobj.name =request.POST['Name']
			placeobj.location = request.POST['location']
			placeobj.regulation=request.POST['regulation']
			pgroups=''
			try:
				if request.POST['place_m_groups']:
					pgroups = request.POST['place_m_groups']
			except:
				pass
			if request.POST['place_groups'] != 'none':
				pgroups = request.POST['place_groups']
			placeobj.place_groups = pgroups
			placeobj.save()
			msg = u'場地資訊新增成功...'
			return render_to_response('OK.html',{'msg':msg})
	cForm = placeAdminForm()
	#要找出群組場地...
	#因為不支援distinct()，只好自行做一個distinct功能...
	#原理是利用 dict 的key 必須是unique, 因此會自動濾除重複值
	places = place.objects.all().values("place_groups").order_by("place_groups")
	pvalues = []
	for item in places:
		pvalues.append(item['place_groups'])
	uniqlist = dict.fromkeys(pvalues).keys() 
	return render_to_response('/member/place_add.html',{'msg':msg,'form':cForm,'pgroup':uniqlist})

from pools.util import *

def user_mgm(request):
	'''
	使用者管理
	'''
	msg = u'使用者管理'
	next = request.path
	
	#加入頁次計算，每頁15筆，每個畫面１０頁
	next = request.path
	currpage = 1
	try:
		if request.GET['page']:
			currpage = int(request.GET.get('page', '1'))
	except:
		currpage = 1
	try:
		if request.GET['preScr']:
			curScr = int(request.GET.get('preScr','0'))
			currpage = int(curScr)*10+1
	except:
		curScr = 0
	try:
		if request.GET['nextScr']:
			nextScr = int(request.GET.get('nextScr','1'))
			currpage = int(nextScr)*10+1
	except:
		nextScr = 1
	whoObj = who.objects.all().order_by('-u_id')
	perScr = 10
	perPage = 15
	curScrObj = pageNav(whoObj,currpage,perScr,perPage)
	return render_to_response('/member/user_mgm.html',{'msg':msg,'messgs':curScrObj['pageObj'], 'navobj':curScrObj,'next':next})

def user_detail(request):
	'''
	這個細項頁面可以用來核發使用權
	'''
	if request.method == 'POST':
		if request.POST['submit']:
			uid = request.POST['u_id']
			whoObj = who.objects.get(u_id=uid)
			cForm = whoAdminForm(request.POST,instance=whoObj)
			if cForm.is_valid():
				cForm.save()
				msg = u'使用者資料更新成功...'
				return render_to_response('OK.html',{'msg':msg})
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
	whoObj = who.objects.get(u_id =rid)
	cForm = whoAdminForm(instance=whoObj)
	#need to prepare the regulation rule...
	
	msg = u'顯示使用者資料,並且可以核發使用權'
	return render_to_response('/member/user_detail.html',{'dspobj':whoObj,'form':cForm,'next':nexturl,'rid':rid})


def place_mgm(request):
	'''
	場地管理
	'''
	msg = u'場地管理'
	next = request.path
	
	#加入頁次計算，每頁5筆，每個畫面１０頁
	next = request.path
	currpage = 1
	try:
		if request.GET['page']:
			currpage = int(request.GET.get('page', '1'))
	except:
		currpage = 1
	try:
		if request.GET['preScr']:
			curScr = int(request.GET.get('preScr','0'))
			currpage = int(curScr)*10+1
	except:
		curScr = 0
	try:
		if request.GET['nextScr']:
			nextScr = int(request.GET.get('nextScr','1'))
			currpage = int(nextScr)*10+1
	except:
		nextScr = 1
	placeObj = place.objects.all().order_by('-place_no')
	perScr = 10
	perPage = 5
	curScrObj = pageNav(placeObj,currpage,perScr,perPage)
	return render_to_response('/member/place_mgm.html',{'msg':msg,'messgs':curScrObj['pageObj'], 'navobj':curScrObj,'next':next})

def place_detail(request):
	'''
	這個細項頁面可以用來更改場地資訊
	'''
	if request.method == 'POST':
		if request.POST['submit']:
			p_no = request.POST['placeno']
			placeobj = place.objects.get(place_no=p_no)
			placeobj.name =request.POST['name']
			placeobj.location = request.POST['location']
			placeobj.regulation=request.POST['regulation']
			pgroups=''
			try:
				if request.POST['place_m_groups']:
					pgroups = request.POST['place_m_groups']
			except:
				pass
			if request.POST['place_groups'] != 'none':
				pgroups = request.POST['place_groups']
			placeobj.place_groups = pgroups
			placeobj.save()
			msg = u'場地資訊新增成功...'
			return render_to_response('OK.html',{'msg':msg})
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
	placeObj = place.objects.get(place_no =rid)
	cForm = placeAdminForm(instance=placeObj)
	#got the regulations
	rule = placeObj.regulation
#	dspRule = DspRule(ParseRule(rule))
	dspRule = ParseRule(rule)
	places = place.objects.all().values("place_groups").order_by("place_groups")
	pvalues = []
	for item in places:
		pvalues.append(item['place_groups'])
	uniqlist = dict.fromkeys(pvalues).keys() 
	msg = u'場地資訊更新'
	return render_to_response('/member/place_detail.html',{'msg':msg,'form':cForm,'pgroup':uniqlist,'rid':rid,'dspRule':dspRule})


def place_approve(request):
	'''
	場地申請審核
	'''
	msg = u'場地申請審核'
	#加入頁次計算，每頁15筆，每個畫面１０頁
	next = request.path
	currpage = 1
	try:
		if request.GET['page']:
			currpage = int(request.GET.get('page', '1'))
	except:
		currpage = 1
	try:
		if request.GET['preScr']:
			curScr = int(request.GET.get('preScr','0'))
			currpage = int(curScr)*10+1
	except:
		curScr = 0
	try:
		if request.GET['nextScr']:
			nextScr = int(request.GET.get('nextScr','1'))
			currpage = int(nextScr)*10+1
	except:
		nextScr = 1
	msg = u'場地使用情形'
	resObj = reserve.objects.all().order_by('-end_date')
	perScr = 10
	perPage = 5
	curScrObj = pageNav(resObj,currpage,perScr,perPage)
	
	return render_to_response('/member/place_approve.html',{'msg':msg,'messgs':curScrObj['pageObj'], 'navobj':curScrObj,'next':next})

def approve_detail(request):
	'''
	場地使用審核
	'''
	if request.method == 'POST':
		if request.POST['submit']:
			rid = request.POST['rev_id']
			revObj = reserve.objects.get(r_id =rid)
			revObj.approve =request.POST['approve']
			revObj.remarks = request.POST['remarks']
			revObj.save()
			msg = u'場地使用申請審核完成...'
			return render_to_response('OK.html',{'msg':msg})
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
	
	cForm = reserveAdminForm(dspObj)
	msg = u'場地使用申請細項資料'
	return render_to_response('/member/approve_detail.html',{'form':cForm,'dspobj':dspObj,'msg':msg,'next':nexturl,'revid':rid})
