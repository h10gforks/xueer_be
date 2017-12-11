# 🏫 [学而](https://xueer.muxixyz.com) ![](http://www.animatedimages.org/data/media/271/animated-ship-image-0059.gif)<br/>

![travis](https://api.travis-ci.org/Muxi-Studio/xueer_be.svg)

华师评课平台, 华师***课程经验收割机***<br/>

## Sails Xueer

### 0. xueer.env配置

* MySQL数据库配置

  * XUEER\_ORM\_URI: mysql://\<username\>:\<passwd\>@\<host\>:\<port\>/\<db_name\>

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
1. 数据库: MySQL, redis
2. 服务器: gunicorn, nginx
3. 任务队列: celery(celery beat)
4. redis监控工具: [redispapa](https://github.com/no13bus/redispapa)
5. 学而主仓库: [xueer_be](https://github.com/Muxi-Studio/xueer_be)
6. 学而静态文件仓库: [xueer_static](https://github.com/Muxi-Studio/xueer_static)

### 2. 搭建
1. 登录服务器
2. 切换到root用户的 `~` 目录
3. 进入`xueer`目录（没有的话自己建一个）
4. 创建`kubenetes`中的 `namespace`: xueer
5. 写用作celery消息队列的 redis 的 redis1-deploy.yaml 和 redis1-svc.yaml
6. 写xueer的 deployment 和 service 文件
7. 创建响应的deployment和service
8. 修改`~/nginxconf/sitesconf/xueer.conf`
9. 重启`nginx`的pods
10. 检查应用是否正常运行
11. 登出服务器

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
