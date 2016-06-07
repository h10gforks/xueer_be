## 更新
###############  学而自动部署脚本 #################
supervisorctl stop xueer
python manage.py db migrate
python manage.py db upgrade
supervisorctl start xueer
supervisorctl status
###############  学而自动部署脚本 #################
