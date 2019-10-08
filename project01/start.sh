#! /bin/sh

    view_pid=`ps -ef|grep view_extraction|grep -v grep|awk '{print $2}'`

    if [ -n "$view_pid" ]; then
        kill $view_pid
        echo "stop servcie"
    fi
    nohup python -u view_extraction.py params1 > nohup.out 2>&1 &
    echo "start service"
