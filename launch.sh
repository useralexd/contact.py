#!/bin/bash
LOG=bot.log

touch $LOG
echo '------------------' >> $LOG
date >> $LOG
while true
do
        python3 proxy_bot.py >> $LOG;
        sleep 5;
done
