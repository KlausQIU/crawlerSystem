#coding:utf-8
# 自动更新公告进程

from django.core.management.base import AppCommand
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option,OptionParser

from models.server import Server
from views.game.base import GMProtocolBase
from django.db.models.base import ModelBase
import sys,os,datetime,time,json
import threading,traceback


import settings
settings.DEBUG = False

from views.server.notice import create_server_notice
from django.db import connections

class Command(BaseCommand):
    '''公告自动生成进程
    '''
    help = '公告自动生成进程'
    option_list = BaseCommand.option_list + (
                   make_option('-c','--cron',action='store_true',
                                dest='cron', default=False,
                                help='定时任务'
                                ),

                                )
    def handle(self, *args, **options):
        print '公告自动生成进程 开启:%s ' % datetime.datetime.now()
        if options.get('cron'):
            while 1:
                try:
                    try:connections['default'].connection.ping()
                    except:connections['default'].close()
                    create_server_notice()
                except:
                    traceback.print_exc()
                time.sleep(60)
            
        else:
            create_server_notice()
        