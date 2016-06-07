###############  学而自动部署脚本 #################
supervisorctl stop xueer
python manage.py db upgrade
supervisorctl start xueer
supervisorctl status
echo "xueer deployment done!"
###############  学而自动部署脚本 #################
