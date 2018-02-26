#coding:utf-8
# 自动开启活动的守护进程

from django.core.management.base import AppCommand
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option,OptionParser

from models.server import Server
from models.game import Activity
from views.game.base import GMProtocolBase
from django.db.models.base import ModelBase
import sys,os,datetime,time,json
import threading,traceback

from util import convert_to_datetime
from util.threadpoll import ThreadPool
from django.db import transaction
from django.db.models import Q
from Queue import Queue

import settings
settings.DEBUG = False
from views.game.activity import activity_action

from django.db import connections




def keep_connections():
    connection_list = [connections['default'],connections['read'],connections['write']]
    for c in connection_list:
        try:c.connection.connection.ping()
        except:c.close()
        
class ActivityExcute(threading.Thread):
    def __init__(self):
        self.work_queue = Queue()
        super(ActivityExcute,self).__init__()
        self.setDaemon(True)
        
    def run(self):
        while 1:
            activity_action_tup = self.work_queue.get()
            now = datetime.datetime.now()
            try:connections['default'].connection.ping()
            except:connections['default'].close()
            keep_connections()
            if len(activity_action_tup) == 2:
                activity_model,action = activity_action_tup
                for s in activity_model.server.all():
                    result = activity_action(activity_model,action,s.id,activity_model.msg,-999,force_log=True)
                    print '[%s] - %s %s(%s) - %s' % (now,activity_model.name,s.name,s.id,result['msg'])

class Command(BaseCommand):
    '''游戏活动自动开启
    '''
    help = '游戏活动开启守护进程'
        
    def handle(self, *args, **options):
        activity_excute = ActivityExcute()
        activity_excute.start()

        activity_auto_on_list = Activity.AUTO_ON_LIST
        activity_auto_off_list =  Activity.AUTO_OFF_LIST
        print '自动开启的活动列表:'
        for activity_name in activity_auto_on_list:
            print activity_name
        print '自动关闭的活动列表:'    
        for activity_name in activity_auto_off_list:
            print activity_name
        while True:
            now = datetime.datetime.now()
            sdate = datetime.datetime(now.year,now.month,now.day,now.hour,now.minute,0)
            edate = datetime.datetime(now.year,now.month,now.day,now.hour,now.minute,59)
            base_query = Q(is_auto=1)
            qeury_on = base_query & Q(sdate__range=[sdate,edate]) & Q(type__in=activity_auto_on_list) 

            query_off = Q(is_auto_off=1) & Q(edate__range=[sdate,edate]) & Q(type__in=activity_auto_off_list) 
            keep_connections()
            try:
                activity_on_list = Activity.objects.prefetch_related('server').filter(qeury_on)

                activity_off_list = Activity.objects.prefetch_related('server').filter(query_off)
                for a in activity_on_list:
                    activity_excute.work_queue.put((a,'on'))
                for a in activity_off_list:
                    activity_excute.work_queue.put((a,'off'))
                
            except:
                traceback.print_exc()
            if now.hour % 12 == 0 and now.minute==1:
                print '[%s] 工作中 sleep 60' % now ,'-' * 40
            
            time.sleep(60)
            
        
        
