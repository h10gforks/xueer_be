###############  学而自动部署脚本 #################
redis-server /etc/redis/redis6380.conf&
redis-server /etc/redis/redis6385.conf&
echo "xueer redis restarted!"
supervisorctl stop xueer
python manage.py db upgrade
supervisorctl start xueer
supervisorctl status
echo "xueer deployment done!"
###############  学而自动部署脚本 #################
