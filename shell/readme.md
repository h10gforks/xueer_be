# Shell
xueer shell脚本

+ data.sh: 初始化数据库
+ start.sh: 启动学而和Nginx服务
+ stop.sh: 关闭学而和Nginx服务
+ pgdump.sh: 结合crontab定时(每晚23:30)备份
+ post-receive: 学而自动部署脚本

note:

+ 学而现在使用supervisor和redispapa进行管理, start.sh/stop.sh已经不再使用
+ 学而使用github webhook自动部署
+ github webhook用的是Python Flask编写的脚本
+ 通过设置github webhook, github会自动提交POST请求, webhook接受请求执行脚本
