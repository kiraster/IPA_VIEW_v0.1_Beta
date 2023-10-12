# import os
from flask import Flask, render_template
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from . import task
from .config import FlaskConfig, APSchedulerConfig
from .commands import insert_cli


# 创建app对象
app = Flask(__name__) 

# 注册自定义命令
app.cli.add_command(insert_cli)

# 使用配置文件中的配置项
app.config.from_object(FlaskConfig)

scheduler = APScheduler()

# 定义db对象，实例化SQLAlchemy，传入app对象
db = SQLAlchemy(app)

# 数据迁移引擎实例化
migrate = Migrate(app, db)

from app import models

# 蓝图注册
from app.admin import admin as admin_blueprint
app.register_blueprint(admin_blueprint, url_prefix="/admin")


# 调用task.py文件里的任务函数
@scheduler.task('interval', id='interval_job_01', name=APSchedulerConfig.job1_name, seconds=APSchedulerConfig.job1_seconds, max_instances=APSchedulerConfig.SCHEDULER_MAX_INSTANCES)
def job1():
    task.get_arp_table()
    print('已完成轮询任务>>>')


# 调用task.py文件里的任务函数
@scheduler.task('interval', id='interval_job_02', name=APSchedulerConfig.job2_name, seconds=APSchedulerConfig.job2_seconds)
def job2():
    task.update_available()
    print('已完成检测在线主机状态任务>>>')


# 添加全局404页面
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


# scheduler和app结合
app.config.from_object(APSchedulerConfig)
scheduler.init_app(app)
scheduler.start()


# 定义查询任务API接口url
from flask_restful import Api, Resource

api = Api(app)


class TaskListResource(Resource):
    def get(self):
        jobs = scheduler.get_jobs()
        task_list = []
        for job in jobs:
            task_list.append({
                "id": job.id,
                "name": job.name,
                "trigger": str(job.trigger),
                "next_run_time": str(job.next_run_time)
            })
        return task_list, 200


api.add_resource(TaskListResource, "/admin/tasks")