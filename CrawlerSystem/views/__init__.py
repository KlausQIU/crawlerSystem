#! /usr/bin/python
# -*- coding: utf-8 -*-
#
#主页,登录相关
#
#django 常用导入
#=========================================
from django.http import HttpResponse
from django.shortcuts import redirect,render_to_response,HttpResponseRedirect
#==========================================

import sys
import datetime, time
from urls.AutoUrl import Route
from settings import TITLE
from CrawlerSystem.models.admin import Admin
from .base import notauth
from CrawlerSystem.models.log import Log


class LoginError(Exception):pass

@Route()
def index(request):
    title = TITLE.split(" ")
    list_menu = request.admin.get_resource('menu').filter(is_show=1).order_by('order')
    now_timestamp = int(time.time())
    return render_to_response("index.html",locals())

def check_login_status(request):
    '''登录状态检测
    '''
    now = datetime.datetime.now()
    err_msg = ''
    err_count = request.session.setdefault('err_count', 0)
    max_count = 10
        
    if err_count >= max_count:
        lock_time = request.session.setdefault('lock_time',now + datetime.timedelta(minutes=max_count))
        if now < lock_time:
            request.session.clear()
            return '错误登录次数过多,请在  %s 后再登录！' % lock_time.strftime(TIMEFORMAT)
        else:
            del request.session['err_count']
            del request.session['lock_time']
    
    if request.POST.get('verify', '') != request.session.get('verify',''):#验证码
            return '验证码错误 !'   

@Route()
@notauth
def login(request):
    #登陆函数
    now = datetime.datetime.now()
    if request.method == 'POST':
        if not request.session.get('has_session'):
            request.session['has_session'] = True

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        request.COOKIES["username"] = username

        try:
            login_status_err_msg = check_login_status(request)
            if login_status_err_msg:
                raise LoginError(login_status_err_msg)

            if username == password :
                raise  LoginError( '请联系管理员修改密码!')
            if not username or not password :
                raise  LoginError( '账号或密码为空!')
            the_admins = Admin.objects.filter(username=username)
            if the_admins:
                the_admin = the_admins[0]
            else:
                raise  LoginError( '%s 账户不存在!' % username)
            if the_admin.status != Admin.Status.NORMAL:
                raise  LoginError( '账户已  %s' % the_admin.get_status_display())
            if the_admin.md5_password() == the_admin.md5_password(password):
                request.session.clear()
                request.session['admin_id'] = the_admin.id
                the_admin.login_count += 1
                the_admin.last_time = now
                the_admin.last_ip = request.real_ip
                the_admin.session_key = request.session.session_key if request.session.session_key else the_admin.session_key
                the_admin.save()
                redirect_url = request.GET.get('from_url','/index')
                return HttpResponseRedirect(redirect_url)
            else:
                raise  LoginError( '密码错误!')
        except LoginError,err_msg:   
            err_msg = err_msg
            request.session['err_count'] = request.session.get('err_count',0) +1
        
    return render_to_response('login.html', locals())

@Route('^logout$')
@notauth
def logout(request):
    '''登出
    '''
    request.session.clear()
    return HttpResponseRedirect("/login")

@Route()
def timeline(request):
    Log._meta.db_table = 'log_operate'
    events = Log.objects.filter(log_name="123").order_by('-log_time')[0]
    return render_to_response('timeline.html',locals())