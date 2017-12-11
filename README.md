# 🏫 [学而](https://xueer.muxixyz.com) ![](http://www.animatedimages.org/data/media/271/animated-ship-image-0059.gif)<br/>

![travis](https://api.travis-ci.org/Muxi-Studio/xueer_be.svg)

华师评课平台, 华师***课程经验收割机***<br/>

## Sails Xueer

### 0. xueer.env配置

* postgresql数据库配置

  * XUEER\_ORM\_URI: postgresql://\<username\>:\<passwd\>@\<host\>:\<port\>/\<db_name\>

* Celery配置

  * C\_FORCE\_ROOT: 是否root运行celery
  * CELERY\_ACCEPT\_CONTENT: pickle root运行celery有漏洞

* Redis配置

  * REDIS1_HOST: 热搜词存储host
  * REDIS2_HOST: LRU/memory cache host
  * REDIS6380PASS: REDIS1的密码
  * REDIS6385PASS: REDIS2的密码
  * REDIS3_HOST: 运行redis3的主机


### 1. 准备

0. 基础环境: {*nix系统(推荐ubuntu)} + {python2.7环境} + {virtualenv, Flask} + {git}
1. 数据库: postgresql, redis
2. 服务器: gunicorn, nginx
3. 任务队列: celery(celery beat)
4. 进程管理工具: supervisor
5. redis监控工具: [redispapa](https://github.com/no13bus/redispapa)
6. github webhook监听工具: [github-webhook-handler](https://github.com/razius/github-webhook-handler)
7. 学而主仓库: [xueer_be](https://github.com/Muxi-Studio/xueer_be)
8. 学而静态文件仓库: [xueer_static](https://github.com/Muxi-Studio/xueer_static)

### 2. 搭建
1. 登录服务器
2. 创建目录: ```~/www/xueer/```
3. git clone:
    + <code>git clone xueer_be ~/www/xueer/</code>
    + <code>git clone xueer_static ~/www/xueer/</code>
    + <code>git clone github-webhook-handler ~/www/</code>
    + <code>git clone redispapa ~/www/</code>
4. 配置学而主仓库(xueer_be)运行环境
    + <code>export XUEER_CONFIG="product"</code> # 写入~/.bashrc
    + <code>export XUEER_ORM_URI=sqlalchemy_database_uri</code>  # 写入~/.bashrc
    + 安装python开发包
        - <code>virtualenv venv && source venv/bin/activate</code>
        - <code>./venv/bin/pip install -r requirements.txt</code>
            + 由于恶心的GFW存在, 推荐使用[中科大pip源](http://topmanopensource.iteye.com/blog/2004853)
    + 运行<code>python manage.py db upgrade</code>没有报错则环境配置成功.
5. 配置xueer_be和xueer_static的github webhooks
    + 参照readme和github官方API
6. 配置redis
    + 配置LRU缓存(redis)
        - <code>redis-server --port 6385</code>
    + 配置学而全站热搜词存储(redis)
        - <code>redis-server --port 6380</code>
    + 配置celery broker 和 backend
        - <code>redis-server --port 6382</code>
    + 配置redispapa监控
        - 参照redispapa readme文件
7. 配置进程管理
    + 创建supervisor配置文件和目录
        - <code>echo_supervisord_conf > /etc/supervisord.conf</code>
        - 注释掉/etc/supervisord.conf里的[include]
        - <code>mkdir /etc/supervisord.d</code>
    + 将supervisor-ini中的ini配置文件放到/etc/supervisord.d/中
    + <code>supervisord && supervisorctl reload</code>
    + <code>supervisord status</code> 查看个进程运行状态
8. 配置nginx
    + 学而nginx配置文件见<code>nginx-conf/xueer.conf</code>
9. 登出服务器

这样就搭建起了一个全自动+自带监控的学而。

## 源码🐎

### 学而桌面版❤️ 源码
+ 前端源码: https://github.com/Muxi-Studio/xueer_be/tree/master/xueer/src
+ 后端源码: https://github.com/Muxi-Studio/xueer_be
    + [后端代码介绍](https://github.com/Muxi-Studio/xueer_be/blob/master/be-readme.md)

### 学而移动版😄 源码
+ 移动端源码: https://github.com/Muxi-Studio/Xueer_Moblie
+ API接口源码: https://github.com/Muxi-Studio/xueer_be/tree/master/xueer/api_1_0

### 学而管理后台📝 源码
+ 管理后台源码: https://github.com/Muxi-Studio/xueer_management

### 华中师范大学```(ง •_•)ง``[木犀团队](http://muxistudio.com)
![muxi](https://avatars2.githubusercontent.com/u/10476331?v=3&s=200) <br/>
<hr/>

## 。。。

> 但是对于黑客, "计算机科学"这个标签是一个麻烦。如果黑客的工作被称为科学, 这会让他们感到自己应该做得像搞科学一样。所以, 大学和实验室
> 里的黑客, 就不去做那些真正想做得事情(设计优美的软件), 而是觉得自己应该写一些研究性的论文。

    --> 《黑客与画家》
<hr/>
