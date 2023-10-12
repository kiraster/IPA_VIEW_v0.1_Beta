from flask import Flask
from flask.cli import AppGroup
import click

app = Flask(__name__)
insert_cli = AppGroup('insert')


@insert_cli.command('group')
@click.option('-n', '--name', prompt=True, default='Default', help='The name of the Default group.')
def insert_group(name):
    from app import db
    from app.models import IPGroup
    default_group = IPGroup(group=name)  # 创建一个新的group对象
    db.session.add(default_group)  # 将用户对象添加到会话中
    db.session.commit()  # 提交会话，将数据插入到数据库
    print(f"The DefaultGroup '{name}' has been added to the database!")  # 输出插入成功信息


# 注册自定义命令
app.cli.add_command(insert_cli)
