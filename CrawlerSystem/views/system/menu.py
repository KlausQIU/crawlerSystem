# -*- coding: utf-8 -*-
# 
#菜单相关
#
#=========================================
from django.core.urlresolvers import reverse  
from django.db import connection,connections
from django.utils.html import conditional_escape 
from django.http import HttpResponse
from django.shortcuts import redirect,render_to_response,HttpResponseRedirect
from django.views.generic import ListView,View
from django.core.urlresolvers import reverse  

from django.db.models import Q
#==========================================


from CrawlerSystem.models.admin import Admin, Menu
from urls.AutoUrl import Route,reverse_view
from CrawlerSystem.views.base import notauth
from CrawlerSystem.models.menu import UserDefinedMenu
from util import trace_msg
            
class MenuTree(object):
    def __init__(self,menu_objs):
        self.tree_node_map = {}
        self.parent_list = []
        for m in menu_objs:
            m.tt_ids = []
            m.tt_parent_ids = []
            self.tree_node_map[m.id] = m
            if m.parent_id == 0:
                self.parent_list.append(m)
        self.list_record = []
        
    def set_tt_ids(self,parent):
        child_num = 0
        for v in self.tree_node_map.values():
                if parent.id ==  v.parent_id:
                    child_num += 1
                    v.tt_ids += parent.tt_ids+[child_num]
                    v.tt_parent_ids = parent.tt_ids
                    self.list_record.append(v)
                    self.set_tt_ids(v)
    
    def get_list_record(self):
        parent_num = 0
        for parent in self.parent_list:
            parent_num +=1
            parent.tt_ids.append(parent_num)
            self.list_record.append(parent)
            self.set_tt_ids(parent)
        for m in self.list_record:
            m.tt_id = '-'.join([str(i) for i in m.tt_ids])
            m.tt_parent_id = '-'.join([str(i) for i in m.tt_parent_ids])
        return self.list_record
    

@Route()
def menu_list(request,is_menu=1):
    '''菜单列表
    '''
    parent_id = int(request.GET.get('parent_id','0'))
    #if parent_id:
    #    parent_menu = request.admin.get_resource('menu').get(id=parent_id)
    list_record = []
    menus = request.admin.get_resource('menu').all().order_by('parent_id')
    menu_tree = MenuTree(menus)
    list_record = menu_tree.get_list_record()

    return render_to_response('system/menu_list.html', locals())


@Route()
def menu_getMenuList(request):
    menu_tree = MenuTree(menus)
    list_record = menu_tree.get_list_record()
    return list_record

@Route()
def menu_save(request):
    '''菜单/权限保存
    '''
    import pdb;pdb.set_trace()
    try:
        id = int(request.REQUEST.get('id', '0'))
        menu = request.admin.get_resource('menu').using('write').get(id=id) if id else Menu.objects.using('write').create(name=request.REQUEST.get('name'))
        # menu.set_attr('name', request.REQUEST.get('name'),null=False)
        menu.parent_id = int(request.REQUEST.get('parent_id', '0'))
        menu.order = int(request.REQUEST.get('order', '0'))
        # menu.is_show = int(request.REQUEST.get('is_show', '0'))
        # menu.is_log = int(request.REQUEST.get('is_log', '0'))
        menu.set_attr('url', request.REQUEST.get('path'),null=True)
        menu.icon = request.REQUEST.get('icon', '')
        menu.css = request.REQUEST.get('css', '')
        menu.save(using='write')
    except Exception,e:
        err_msg = trace_msg()
    return render_to_response('404.html',locals())