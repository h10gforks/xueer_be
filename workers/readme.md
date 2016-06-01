# Workers
后台任务队列celery task

## @celery.task
### 定时清空hot keywords数据库
hot keywords(热搜词)统计策略, 每三天清空一次.

### 定时备份postgresql数据库
每晚23:30定时备份: 现在是在postgres用户下实现crontab定时
