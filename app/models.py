from datetime import datetime

from app import db


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
