#! /bin/bash

cd /bunbunmaru
python3 run_collector.py &
uwsgi --socket 0.0.0.0:80 --protocol=http -w run_server
