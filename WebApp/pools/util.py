#encoding: utf-8

from django.http import HttpResponseRedirect, HttpResponse

'''
真是頭昏了，連jsp function 都出現在這裡...

function mydiff(date1,date2,interval) {
    var second=1000, minute=second*60, hour=minute*60, day=hour*24, week=day*7;
    date1 = new Date(date1);
    date2 = new Date(date2);
    var timediff = date2 - date1;
    if (isNaN(timediff)) return NaN;
    switch (interval) {
        case "years": return date2.getFullYear() - date1.getFullYear();
        case "months": return (
            ( date2.getFullYear() * 12 + date2.getMonth() )
            -
            ( date1.getFullYear() * 12 + date1.getMonth() )
        );
        case "weeks"  : return Math.floor(timediff / week);
        case "days"   : return Math.floor(timediff / day); 
        case "hours"  : return Math.floor(timediff / hour); 
        case "minutes": return Math.floor(timediff / minute);
        case "seconds": return Math.floor(timediff / second);
        default: return undefined;
    }
}

'''
from datetime import datetime, timedelta
import simplejson

#多頁
from django.core.paginator import Paginator

import math

#以下的功能是用來將資料分成每頁５筆，然後每個畫面可以有１０頁
def pageNav(tblobj,currpage,perScreen=10,perPage=5):
	'''
	此處必須小心，Paginagtor是以１為基底，也就是第一頁的下標為１
	但是我們所使用的畫面是以0為基底，也就是第一個畫面的下標為0
	'''
	rtn={}
	link_list = Paginator(tblobj, perPage)
	pList = link_list.page(currpage)
	pages = link_list.num_pages
	totalScr = math.ceil(float(pages)/perScreen) -1
	curScr = int(currpage/perScreen)
	#必須讓整除時，仍停留在前一個畫面
	if currpage % perScreen == 0:
		curScr = curScr -1
	
	rtn['pageObj'] = pList
	rtn['pages'] = pages
	rtn['curpage']=currpage
	rtn['totalScr']= totalScr
	rtn['curScr'] = curScr
	rtn['perPage']= perPage
	if curScr == 0:
		rtn['preScr']=''
	else:
		rtn['preScr']=curScr -1
	if curScr > totalScr-1:
		rtn['nextScr']=''
	else:
		rtn['nextScr']=curScr +1
	#必須增加每頁的啟始頁以及結束頁的計算
	rtn['stpage']= curScr*perScreen+1
	if curScr <= totalScr-1:
		rtn['edpage']= (curScr+1)*perScreen
	else:
		rtn['edpage']=pages
	
	return rtn

#以下兩個函數是用來將場地的限制轉成陣列，以及轉回字串的功能，用於回寫資料庫

def ParseRule(sRule):
	aRule = sRule.split(';')
	aResult = []
	
	for rule in aRule:
		aRtn = {}
		items = rule.split('/')
		if(len(items) < 2 ):
			break
		aRtn['type'] = items[0]
		aRtn['week'] = items[1]
		aRtn['st_time'] = items[2]
		aRtn['ed_time'] = items[3]
		aResult.append(aRtn)
	return aResult

def PackRule(aRule):
	'''will packing the array into a formated string
	array ==> 0/none/08:00/1600;x/x/xx:xx/xx:xx;
	'''
	sResult=''
	aRule = []
	for rule in aRule:
		sTemp = ''
		if is_iter(rule):
			 sTemp = '/'.join(rule)
		aRule.append(sTemp)
	
	sResult = ';'.join(aRule)
	return sResult

def DspRule(aRule):
	# transfer the format for display
	aResult=[]
	for rule in aRule:
		sTemp = ''
		#echo 'the type :'.$rule['type'];
		if is_iter(rule):
			if rule['type'] == '1':
				rule['type'] = u'每週'
			elif rule['type'] == '2':
				rule['type'] = u'每天'
			else:
				rule['type'] = '----'
			
			if rule['week'] == '1':
				rule['week'] = u'一'
			elif rule['week'] == '2':
				rule['week'] = u'二'
			elif rule['week'] == '3':
				rule['week'] = u'三'
			elif rule['week'] == '4':
				rule['week'] = u'四'
			elif rule['week'] == '5':
				rule['week'] = u'五'
			else:
				rule['week'] = '--'
			sTemp = rule['type']+' / '+rule['week']+u'　：　'+rule['st_time']+ u'　～　'+rule['ed_time']
		aResult.append(sTemp)
	#return the array for display
	return aResult


#以下為檢查用function....
from types import *


def is_iter(obj):
   if isinstance(obj,ListType): return 1
   if isinstance(obj,TupleType): return 1
   if isinstance(obj,DictType): return 1
   if isinstance(obj,FileType): return 1
   try: 
     iter(obj)
     return -1
   except TypeError:
     return 0

def is_list(obj):
   if isinstance(obj,ListType): return 1
   if is_seq(obj):
       if check_type(obj,callables=['append','extend','pop']): 
       	return -1
   return 0

def is_seq(obj):
   if isinstance(obj,ListType): return 1
   if isinstance(obj,TupleType): return 1
   if is_iter(obj):
      try: 
         obj[0:0]
         return -1
      except TypeError:
         pass
   return 0  

def check_type(obj,atts=[],callables=[]):
	got_atts=True
	for att in atts:
		if not hasattr(obj,att):
			got_atts=False;break
	got_callables=True
	for call in callables:
			if not hasattr(obj,call):
				got_callables=False;break
			the_attr=getattr(obj,call)
			if not callable(the_attr):
				got_callables=False;break
	if got_atts and got_callables: return -1
	return 0

#以下為時間處理函數
def compDateBlock(nt,ne,ot,oe):
	'''
   nt : new start date
   ne : new end  date
   ot : old start date
   oe : old end  date 
   the old date was the date period for comparing
   
   return value:
   the new date block was totally different with the old date block  => return true
	這是改寫自php函數	
	'''
	#transfer all the datetime format
	if not isinstance(nt, datetime):
		nt = datetime.strptime(nt,"%Y-%m-%d %H:%M:%S")
	if not isinstance(ne, datetime):
		ne = datetime.strptime(ne,"%Y-%m-%d %H:%M:%S")
	if not isinstance(ot, datetime):
		ot = datetime.strptime(ot,"%Y-%m-%d %H:%M:%S")
	if not isinstance(oe, datetime):
		oe = datetime.strptime(oe,"%Y-%m-%d %H:%M:%S")
	
	if (nt > ot and ne > oe and nt > oe and ne > oe):
		return True
	if (nt < ot and ne < ot and nt < oe and ne < oe):
		return True
	
	return False

#計算每週的起算日
def WeekStart(sDate):
	'''
	找出該所在週別的第一天
	sDate format "%Y-%m-%d %H:%M:%S"
	'''
	dCurr = datetime.strptime(sDate,"%Y-%m-%d %H:%M:%S")
	wkSt = dCurr-timedelta(days=dCurr.weekday())
	out = wkSt.date().isoformat() + ' 08:00:00'
	return datetime.strptime(out,"%Y-%m-%d %H:%M:%S")

def WeekEnd(sDate):
	'''
	找出該所在週別,週五的日期
	sDate format "%Y-%m-%d %H:%M:%S"
	will return a datetime object
	'''
	dCurr = datetime.strptime(sDate,"%Y-%m-%d %H:%M:%S")
	ds = 4-dCurr.weekday()
	wkend = dCurr+timedelta(days=ds)
	out = wkend.date().isoformat() + ' 21:00:00'
	return datetime.strptime(out,"%Y-%m-%d %H:%M:%S")
