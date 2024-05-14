# 一、项目简介

一个使用 Flask 框架组装的IP地址管理平台，很简陋

在配置文件`/app/config.py` 配置好指定交换机的snmp v2c 只读团体名称后，可以定时轮询指定交换机的arp数据，将获得的ip、mac地址及轮询时间写进数据库；下一次没有轮询到的已知ip会被设置为离线状态

这样就可以拿到一份准确的局域网设备数据（包括曾短暂上线后被轮询到但之后离线的）

前端：Bootstrap、Datatable、sweetalert……

后端：Flask、APScheduler……

数据库：SQLite

# 二、内置功能	
- 首页：*没有首页的首页* 
- IP地址表：显示IP地址使用情况，可在页面进行增、删、改、导出到Excel表格
-  分组：按分组 + 网段显示目录树，右侧显示所选择查看网段的饼图，方块表和网段IP地址表
-  设置：查看定时任务执行情况和轮询参数；将ip子网添加到指定分组
-  数据库：无功能，被定向到404
-  关于：一段话


# 三、项目结构

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

# 四、安装使用

## 4.1 下载源码备用

```
# git
git clone https://github.com/kiraster/IPA_VIEW_v0.1_Beta.git

# ZIP
https://github.com/kiraster/IPA_VIEW_v0.1_Beta  ->>  Code  –>> Download ZIP
```

## 4.2 安装python并配置虚拟环境
经过热心群众测试python3.12运行本代码有错误，使用python3.10可以完美规避安装环境报错问题
```
# 使用venv
# 创建虚拟环境
python -m venv venv
#  进入虚拟环境
.\venv\Scripts\activate

# 使用miniconda3
# 可以miniconda安装python，使用介绍见作者博客https://kiraster.github.io/posts/f2cfb11.html
# 创建一个虚拟环境（指定Python版本3.10）
conda create -n ipa_base python=3.10
# 激活虚拟环境
conda activate ipa_base
```

## 4.3 修改配置

```
# 定义flask代码中的配置项
class FlaskConfig:
    HOST = '127.0.0.1'  # 设置主机地址，'0.0.0.0' 表示监听所有可用的网络接口
    PORT = 80  # 设置端口号，一般情况下使用默认的 5000 端口
    # 开启调试模式
    DEBUG = True
    # 数据库连接URI
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'

    # 添加MySQL数据库连接
    # MySQL所在主机名
    HOSTNAME = "127.0.0.1"
    # MySQL监听的端口号，默认3306
    MYSQL_PORT = "3306"
    # 连接MySQL的用户名
    USERNAME = "root"
    # 连接MySQL的密码
    PASSWORD = "12345678"
    # PASSWORD = quote(PASSWORD, safe='')
    # MySQL上创建的数据库名称
    DATABASE = "ipa"
    # 修改以下URL，对应你的MySQL数据库路径
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{MYSQL_PORT}/{DATABASE}"
    # SQLALCHEMY_DATABASE_URI = 'mysql://root:12345678@#@127.0.0.1:3306/ipa'
    # url = 'mysql+pymysql://root:12345678@127.0.0.1:3306/ipa'

    # SQLALCHEMY_TRACK_MODIFICATIONS当设置为True时，SQLAlchemy会在对数据库进行修改操作（如添加、更新、删除记录）后发出信号，
    # 以便其他组件（如Flask-Migrate）能够捕获这些变化并生成相应的数据库迁移脚本。
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 定义SECRET_KEY，CSRF保护需要一个密钥来安全地对令牌进行签名。
    # 默认情况下，这将使用Flask应用程序的SECRET_KEY。如果想使用单独的令牌，可以设置WTF_CSRF_SECRET_KEY
    SECRET_KEY = '21caf73529034bf8ad2d04e820dc2f1d'


# APScheduler配置参数
# job1 和 job2 时间建议从30改为300
class APSchedulerConfig:
    # 开启API查询接口
    SCHEDULER_API_ENABLED = True
    job1_name = '定时轮询ARP表'
    job2_name = '定时更新没有轮询到ARP表项的IP地址状态'
    job1_seconds = 300
    job2_seconds = 300
    # 最大定时任务实例数
    # 此数值是指“比如说你网络卡了30分钟以上，而前一次轮询没有完成，就会堆积到2次轮询任务，大概就是这么个意思”
    SCHEDULER_MAX_INSTANCES = 66


class SNMPConfig:
    # 当超过30分钟没有updated_at值更新，则available值置为False；单位：分钟
    REFRESH_TIME = 30
    SNMP_DATA = [
        {'snmp_host': '192.168.56.10', 'snmp_community': 'public'},
        {'snmp_host': '192.168.56.20', 'snmp_community': 'xswl_public'},
    ]
```

## 4.4 安装库

```
pip install -r requirements.txt
# 网络不行用下面这个
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/  -r requirements.txt
```

## 4.5 运行

```
# 创建当前版本的数据迁移脚本

flask db init

#  运行以上命令会提示如下，如果使用sqlite，直接快进到数据迁移脚本 flask db migrate

“Please edit configuration/connection/logging settings in 'F:\\xxx\\IPA_VIEW_v0.1_Beta\\migrations\\alembic.ini' before proceeding.”

# 根据提示修改alembic.ini文件，在文件末尾添加如下

[sqlalchemy]
url = mysql+pymysql://root:12345678@127.0.0.1:3306/ipa

---------------------------------------------------------------------------------

# 数据迁移脚本
flask db migrate
# 创建数据库
flask db upgrade

# 在IPGroup表创建一个默认组
# 输入以下命令，填写默认组组，回车使用默认值“Default”，默认组名称随意起都可
flask insert group
Name [default]: 

# [可选]，导入测试数据，如果可以抓到snmp数据不要导入，不然还要逐行删除
 python .\app\test_data.py

# 启动应用
# 注意2种方式访问端口不一样
python manage.py
# 相关配置在class FlaskConfig中
# 或第二种办法
flask run（建议用此方式）
# 此模式启动仅支持在本机使用固定地址http://127.0.0.1:5000/admin访问，即使修改config.py中相应参数也无效。
# 若想修改默认5000端口并运行通过ip:端口方式访问，请以下面命令运行，并注意放行相关防火墙端口。
flask run -h 0.0.0.0 -p 8080
# -h 后为要监听的网络接口地址，'0.0.0.0' 表示监听所有可用的网络接口
# -p 后数字为要修改的服务端口

```
![e2d52aace85db2aedcfd7d6557be964](https://github.com/bg4vrg/IPA_VIEW_v0.1_Beta/assets/19301725/c3056066-d551-4917-b2aa-e8c5eb4cc019)

# 五、设置
## 5.1 ip子网手动分组
网页前端设置选项那里可以手动将ip子网（类似192.168.1.0/24）创建到新的分组里，支持中文，同时该子网在默认分组里会自动去掉，只显示你创建的分组里。
## 5.2 关于删除不生效
需要手动刷新网页

## 5.3 预览

浏览器地址栏输入：127.0.0.1/admin/ ，或者  127.0.0.1[:port]/admin/

## 5.4 批处理文件自启动
为了最大限度解放打工人，需要做到一键运行乃至开机即启动。
### 5.4.1 准备批处理运行环境
找到AnacondaPrompt(miniconda3)图标，查看图标属性并复制目标栏内内容备用

![015c9efcd2ec7badcb037c62ba3d9ad](https://github.com/bg4vrg/IPA_VIEW_v0.1_Beta/assets/19301725/eb3ff29d-01b4-47fb-8a0b-79bea2b4dd5e)


`
%windir%\System32\cmd.exe "/K" C:\miniconda3\Scripts\activate.bat C:\miniconda3
`

复制"/K"后面的内容,不要照抄，安装路径都不一定相同

`
C:\miniconda3\Scripts\activate.bat C:\miniconda3
`

### 5.4.2 批处理内容
为了调用miniconda3，需要在命令前加call，完整批处理内容如下，保存为bat文件即可。

```
@echo off
call C:\miniconda3\Scripts\activate.bat C:\miniconda3
call activate ipa_base
cd /d C:\ipa_VIEW
call python manage.py
cmd /k
```
<b>仅供参考</b>

注意：
C:\ipa_VIEW是我程序解压的位置

cmd /k是为了不关闭cmd窗口



运行效果如下图

![37780c3218ee534681142bb8e0c8035](https://github.com/bg4vrg/IPA_VIEW_v0.1_Beta/assets/19301725/317b67c8-dadd-42f0-94c2-522b8a4c574c)

## 5.5 对网页进行简单加密

比较简陋，明文密码，实测F12看不到，凑合用下。
将以下代码插入到IPA_VIEW\app\templates\admin下的index.html里面，然后修改下你要设置的密码。

```
<SCRIPT language=JavaScript> 
function password() { 
var testV = 1; 
var pass1 = prompt('请输入密码:',''); 
while (testV < 3) { 
if (!pass1) 
history.go(-1); 
if (pass1 == "这里输入你想设置的密码") { 
alert('密码正确!'); 
break; 
} 
testV+=-1; 
var pass1 = prompt('密码错误!请重新输入:'); 
} 
if (pass1!="password" & testV ==3) 
history.go(-1); 
return " "; 
} 
document.write(password()); 
</SCRIPT>
```

# 六、预览截图

https://kiraster.github.io/gallery/IPA_VIEW_v0.1_Beta/

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

---

# 感谢

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

感谢热心群众 @[**bg4vrg**](https://github.com/bg4vrg)
