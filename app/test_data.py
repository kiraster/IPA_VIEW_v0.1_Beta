from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from config import FlaskConfig


app = Flask(__name__)  # 创建app对象
# 使用配置文件中的配置项
app.config.from_object(FlaskConfig)
# 定义db对象，实例化SQLAlchemy，传入app对象
db = SQLAlchemy(app)


# 定义数据模型类，创建 IP_GROUP 表
class IPGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group = db.Column(db.String(256), unique=True)
    group_item = db.relationship('IPTable', backref='group', lazy=True)  # 建立外键关联

    def __repr__(self):
        return "<IPGroup %r>" % self.group


# 定义数据模型类，创建 IP_TABLE 表
class IPTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(15), unique=True, nullable=False)
    mask = db.Column(db.String(15), nullable=False)
    mac_add = db.Column(db.String(17))
    network = db.Column(db.String(18))
    desc = db.Column(db.String(256))
    user = db.Column(db.String(256))
    available = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ip_group_id = db.Column(db.Integer, db.ForeignKey('ip_group.id'))  # 添加外键关联

    def __repr__(self):
        return "<IPTable %r>" % self.ip


if __name__ == '__main__':

    # 创建数据表
    with app.app_context():

        # 创建数据表，添加测试数据
        db.create_all()

        network0 = IPGroup(group='Default')
        network1 = IPGroup(group='新办公楼1区网段')
        network2 = IPGroup(group='新办公楼2区网段')
        network3 = IPGroup(group='服务器网段')
        network4 = IPGroup(group='监控网段')
        network5 = IPGroup(group='旧办公楼网段')

        host1 = IPTable(ip='10.1.1.1', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='10.1.1.0/24', user='user1', available=True, ip_group_id=1)
        host2 = IPTable(ip='10.1.2.2', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='10.1.2.0/24', user='user2', available=True, ip_group_id=1)
        host3 = IPTable(ip='10.1.3.3', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='10.1.3.0/24', user='user3', available=False, ip_group_id=1)
        host4 = IPTable(ip='10.1.4.4', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='10.1.4.0/24', user='user4', available=False, ip_group_id=1)
        host5 = IPTable(ip='10.1.5.5', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='10.1.5.0/24', user='user5', available=False, ip_group_id=1)

        host6 = IPTable(ip='10.1.10.6', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='10.1.1.0/24', user='user12', available=True, ip_group_id=2)
        host7 = IPTable(ip='10.1.10.7', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='10.1.10.0/24', user='user22', available=True, ip_group_id=2)
        host8 = IPTable(ip='10.1.11.8', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='10.1.11.0/24', user='user32', available=False, ip_group_id=2)
        host9 = IPTable(ip='10.1.11.9', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='10.1.11.0/24', user='user42', available=False, ip_group_id=2)
        host10 = IPTable(ip='10.1.12.10', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='10.1.12.0/24', user='user52', available=False, ip_group_id=2)

        host11 = IPTable(ip='172.16.100.1', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='172.16.100.0/24', user='user13', available=True, ip_group_id=3)
        host12 = IPTable(ip='172.16.100.2', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='172.16.100.0/24', user='user23', available=True, ip_group_id=3)
        host13 = IPTable(ip='172.16.100.3', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='172.16.100.0/24', user='user33', available=False, ip_group_id=3)
        host14 = IPTable(ip='172.16.101.4', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='172.16.101.0/24', user='user43', available=False, ip_group_id=3)
        host15 = IPTable(ip='172.16.101.5', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='172.16.101.0/24', user='user53', available=False, ip_group_id=3)

        host16 = IPTable(ip='192.168.10.6', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='192.168.10.0/24', user='user14', available=True, ip_group_id=4)
        host17 = IPTable(ip='192.168.10.7', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='192.168.10.0/24', user='user24', available=True, ip_group_id=4)
        host18 = IPTable(ip='192.168.10.8', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='192.168.10.0/24', user='user34', available=False, ip_group_id=4)
        host19 = IPTable(ip='192.168.10.9', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='192.168.10.0/24', user='user44', available=False, ip_group_id=4)
        host20 = IPTable(ip='192.168.11.10', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='192.168.11.0/24', user='user54', available=False, ip_group_id=4)

        host21 = IPTable(ip='192.168.88.21', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='192.168.88.0/24', user='user15', available=True, ip_group_id=5)
        host22 = IPTable(ip='192.168.88.22', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='192.168.88.0/24', user='user25', available=True, ip_group_id=5)
        host23 = IPTable(ip='192.168.88.23', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='192.168.88.0/24', user='user35', available=False, ip_group_id=5)
        host24 = IPTable(ip='192.168.99.24', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='192.168.99.0/24', user='user45', available=False, ip_group_id=5)
        host25 = IPTable(ip='192.168.99.25', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='192.168.99.0/24', user='user55', available=False, ip_group_id=5)
        host26 = IPTable(ip='192.168.99.26', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='192.168.99.0/24', user='user56', available=False, ip_group_id=5)
        host27 = IPTable(ip='192.168.99.27', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='192.168.99.0/24', user='user57', available=False, ip_group_id=5)
        host28 = IPTable(ip='192.168.99.28', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='192.168.99.0/24', user='user58', available=False, ip_group_id=5)
        host29 = IPTable(ip='192.168.99.29', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='192.168.99.0/24', user='user59', available=False, ip_group_id=5)
        host30 = IPTable(ip='192.168.99.30', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='192.168.99.0/24', user='user60', available=False, ip_group_id=5)
        host31 = IPTable(ip='192.168.99.31', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='192.168.99.0/24', user='user61', available=False, ip_group_id=5)
        host32 = IPTable(ip='192.168.99.32', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='192.168.99.0/24', user='user62', available=False, ip_group_id=5)
        host33 = IPTable(ip='192.168.99.33', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='192.168.99.0/24', user='user63', available=False, ip_group_id=5)
        host34 = IPTable(ip='192.168.99.34', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='192.168.99.0/24', user='user64', available=False, ip_group_id=5)
        host35 = IPTable(ip='192.168.99.35', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='192.168.99.0/24', user='user65', available=False, ip_group_id=5)
        host36 = IPTable(ip='192.168.99.36', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='192.168.99.0/24', user='user66', available=False, ip_group_id=5)
        host37 = IPTable(ip='192.168.99.37', mask='255.255.255.0', mac_add='aaaa-bbbb-cccc', network='192.168.99.0/24', user='user67', available=False, ip_group_id=5)

        db.session.add_all([network0, network1, network2, network3, network4, network5])
        db.session.add_all([host1, host2, host3, host4, host5, host6, host7, host8, host9, host10, host11, host12, host13, host14, host15, host16, host17, host18, host19, host20, host21, host22, host23, host24, host25,host26, host27, host28, host29, host30, host31, host32, host33, host34, host35, host36, host37])
        db.session.commit()
