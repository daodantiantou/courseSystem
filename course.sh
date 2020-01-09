#!/bin/bash
nohup python3 /opt/app/project/course/manage.py runserver 0.0.0.0:8000 1>/opt/app/project/course/course.txt 2>&1 &
