# supervisor-ini
supervisor 进程管理配置文件

+ **xueer**: xueer 主进程
+ **celery**: celery 主进程
+ **celerybeat**: celery beat 定时任务进程
+ **redispapa**: redis和服务器监控
    + redis: 6380~0: 热搜词存储
    + redis: 6385~1: 搜索缓存memcached
    + redis: 6382~2: celery broker和backend
