## 项目简介

一个使用 Flask 框架组装的IP地址管理平台，很简陋

前端：Bootstrap、Datatable、sweetalert……

后端：Flask、APScheduler……

数据库：SQLite

预览截图：https://kiraster.github.io/gallery/IPA_VIEW_v0.1_Beta/

### 内置功能

- 首页：*没有首页的首页* 
- IP地址表：显示IP地址使用情况，可在页面进行增、删、改、导出到Excel表格
-  分组：按分组 + 网段显示目录树，右侧显示所选择查看网段的饼图，方块表和网段IP地址表
-  设置：查看定时任务执行情况和轮询参数
-  数据库：404
-  关于：一段话

### 项目结构

```
|   app.py  # 没什么用装个样子
|   manage.py  #　应用入口文件
|   README.md
|   requirements.txt　　＃　安装库
|   
+---app
|   |   commands.py  # 自定义插入组命令
|   |   config.py　　＃　配置文件
|   |   models.py　　＃　数据模型类代码
|   |   task.py　　＃　定时任务代码
|   |   test_data.py　　＃　导入测试数据
|   |   __init__.py
|   |   
|   +---admin
|   |   |   lib.py　　＃ 可复用功能函数代码
|   |   |   views.py　　＃ 视图函数代码
|   |   |   __init__.py
|   |           
|   +---static　　＃　CSS JS 插件
|   |           
|   +---templates  # 被渲染的html模板
|   |   |   404.html  # 404 页面
|   |   |   
|   |   \---admin
|   |           about.html
|   |           base.html
|   |           index.html
|   |           ipgroup.html
|   |           ipshow.html
|   |           settings.html
|              
|           
+---instance  # flask db 命令自动生成的文件夹
|       db.sqlite3  # sqlite3数据库文件
|       
+---migrations  # flask db 命令自动生成的文件夹

```

## 安装使用

### 下载

```
# git
git clone https://github.com/kiraster/IPA_VIEW_v0.1_Beta.git

# ZIP
https://github.com/kiraster/IPA_VIEW_v0.1_Beta  ->>  Code  –>> Download ZIP
```

### 虚拟环境

```
# 创建虚拟环境
python -m venv venv
# 进入虚拟环境
.\venv\Scripts\activate
```

### 修改配置

```
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
```

### 安装库

```
pip install -r requirements.txt
# 网络不行用下面这个
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/  -r requirements.txt
```

### 运行项目

```
# 创建当前版本的数据迁移脚本
flask db init
# 数据迁移脚本
flask db migrate
# 创建数据库
flask db upgrade

# 在IPGroup表创建一个默认组
# 输入以下命令，填写默认组组，回车使用默认值“Default”，默认组名称随意起都可
flask insert group
Name [default]: 

# 可选，导入测试数据
 python .\app\test_data.py

# 启动应用
python manage.py
或
flask run
```

### 预览

![ScreenCaputure231012233137](https://s2.loli.net/2023/10/12/D4mpPBsOhouYZL2.jpg)

![ScreenCaputure231012233149](https://s2.loli.net/2023/10/12/LYQkNxOPDVXjHBR.jpg)

![ScreenCaputure231012233228](https://s2.loli.net/2023/10/13/IvNVqYmJnDoEU5c.jpg)

![ScreenCaputure231012233235](https://s2.loli.net/2023/10/13/wMDQG8XOuEf4tip.jpg)

![ScreenCaputure231012233255](https://s2.loli.net/2023/10/13/cCFhGL4rsMyWmEO.jpg)

![ScreenCaputure231012233324](https://s2.loli.net/2023/10/13/JuLl3vF6TOmCVzh.jpg)

![ScreenCaputure231012233502](https://s2.loli.net/2023/10/13/DBWQbeIamuhAxoC.jpg)

![ScreenCaputure231012233510](https://s2.loli.net/2023/10/13/hIDWOnZBg8fa4Em.jpg)

![ScreenCaputure231012233530](https://s2.loli.net/2023/10/13/x8yEvQ1nMkahf5V.jpg)

![ScreenCaputure231012233542](https://s2.loli.net/2023/10/13/ZbGsINpLFdKvo8V.jpg)

![ScreenCaputure231012233627](https://s2.loli.net/2023/10/13/X5BZhbJgnWLCQ4O.jpg)

![ScreenCaputure231012233635](https://s2.loli.net/2023/10/13/bC4mnLF6BJi5j9p.jpg)

![ScreenCaputure231012233734](https://s2.loli.net/2023/10/13/tMZQqxJToXSAldh.jpg)

![ScreenCaputure231012233740](https://s2.loli.net/2023/10/13/WzAx4NVm3UMeYGv.jpg)

![ScreenCaputure231012233800](https://s2.loli.net/2023/10/13/dYiTrvEaoOIDtcC.jpg)

![ScreenCaputure231012233912](https://s2.loli.net/2023/10/13/aV3eyd1iTzODQJ8.jpg)

![ScreenCaputure231012233923](https://s2.loli.net/2023/10/13/6T8n3uaABLqIZNE.jpg)

![ScreenCaputure231012233929](https://s2.loli.net/2023/10/13/f2qhtZa7uv4nr91.jpg)

![ScreenCaputure231012234122](https://s2.loli.net/2023/10/13/lAZ6hC2DcRerMEm.jpg)

## 感谢

就像开头说的，我只是组装了一个东西，代码中用到了很多开源的代码，感谢以下

- https://github.com/shuzheng/zhengAdmin
- https://github.com/istarmeow/FlaskMovie
- https://github.com/idindrakusuma/simple-404-template
- https://github.com/twbs/bootstrap
- https://gitee.com/cloudResource/error-page
- https://code.juejin.cn/pen/7085639478659776542
- https://gitee.com/pear-admin/pear-admin-flask
- https://datatables.net/
- https://github.com/t4t5/sweetalert
- ……
