'''
编写设置参数
'''


# 定义flask代码中的配置项
class FlaskConfig:
    HOST = '127.0.0.1'  # 设置主机地址，'0.0.0.0' 表示监听所有可用的网络接口
    PORT = 80  # 设置端口号，一般情况下使用默认的 5000 端口
    # 开启调试模式
    DEBUG = True
    # 数据库连接URI
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'
    # SQLALCHEMY_TRACK_MODIFICATIONS当设置为True时，SQLAlchemy会在对数据库进行修改操作（如添加、更新、删除记录）后发出信号，
    # 以便其他组件（如Flask-Migrate）能够捕获这些变化并生成相应的数据库迁移脚本。
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 定义SECRET_KEY，CSRF保护需要一个密钥来安全地对令牌进行签名。
    # 默认情况下，这将使用Flask应用程序的SECRET_KEY。如果想使用单独的令牌，可以设置WTF_CSRF_SECRET_KEY
    SECRET_KEY = '21caf73529034bf8ad2d04e820dc2f1d'


# APScheduler配置参数
class APSchedulerConfig:
    # 开启API查询接口
    SCHEDULER_API_ENABLED = True
    job1_name = '定时轮询ARP表'
    job2_name = '定时更新没有轮询到ARP表项的IP地址状态'
    job1_seconds = 30
    job2_seconds = 30
    # 最大定时任务实例数
    SCHEDULER_MAX_INSTANCES = 66


class SNMPConfig:
    # 当超过30分钟没有updated_at值更新，则available值置为False
    REFRESH_TIME = 1
    SNMP_DATA = [
        {'snmp_host': '192.168.56.10', 'snmp_community': 'public'},
        {'snmp_host': '192.168.56.20', 'snmp_community': 'xswl_public'},
    ]
