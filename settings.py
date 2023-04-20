# -*- coding: utf-8 -*-
# @FileName  : settings.py
# @Author： 公众号：阿三先生
# @Date 11/9/22 2:11 PM
# @Version 1.0
# 项目主目录
import os

def project_dir(project_name):
    cwd = os.getcwd()
    pro_list = cwd.split("/")[::-1]

    pro_index = 0
    for index in range(len(pro_list)):
        if project_name in pro_list[index]:
            pro_index = index
            break

    project_path_list = pro_list[pro_index:]
    return "/".join(project_path_list[::-1])


project_path = project_dir("chatgpt-service")
# 日志目录
log_path = f'{project_path}/logs'

SERVICE_NAME = "chatgpt-service"
SERVICE_PORT = 8012

API_KEY = "**********************"
