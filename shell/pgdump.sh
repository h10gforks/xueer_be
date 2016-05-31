#########################################################################
#                            shell variables                            #
#########################################################################
date_now=`date +%Y-%m-%d`
back_dir=/var/lib/pgsql/backups
back_log_dir="$back_dir/backup.log"
rmback_log_dir="$back_dir/rmback.log"


#########################################################################
#                           postgresql backup                           #
#########################################################################
/usr/bin/pg_dump -U postgres xueerdb > $back_dir/$date_now.out
if [ $? = 0 ]; then
    echo "$date_now xueer database backup success✅  " >> $back_log_dir
    echo "" >> $back_log_dir
else
    echo "$data_now xueer database backup failed❌  " >> $back_log_dir
    echo "" >> $back_log_dir
fi

#########################################################################
#                           remove backup files                         #
#########################################################################
find $back_dir -mtime +8 -exec rm -rf {} \;
if [ $? = 0 ]; then
    echo "$date_now rm backup files successful✅  " >> $rmback_log_dir
    echo "" >> $rmback_log_dir
else
    echo "$date_now rm backup files failed❌  " >> $rmback_log_dir
    echo "" >> $rmback_log_dir
fi
