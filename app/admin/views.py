from functools import wraps
from flask import render_template, redirect, url_for, session, request, flash, abort, jsonify, current_app
# import uuid  # 生成唯一字符串

from . import admin
from app import db, app
from app.models import IPGroup, IPTable
from app import config
from app.config import APSchedulerConfig, SNMPConfig
# 导入可复用功能函数
from app.admin.lib import verify_ipaddress, is_valid_subnet_mask, get_network_info


# 首页渲染
@admin.route("/")
def index():
    return render_template('admin/index.html')


# 设置页渲染
@admin.route("/settings", methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # 获取表单输入的值
        # job_seconds = int(request.form.get('job_seconds'))
        # snmp_community = request.form.get('snmp_community')
        # snmp_host = request.form.get('snmp_host')

        # 更新配置文件中的参数

        # 重新加载配置文件
        app.config.from_object(config)

    # 获取当前配置参数
    scheduler_config = {
        'seconds': APSchedulerConfig.job1_seconds,
        'snmp_data': SNMPConfig.SNMP_DATA,
    }
    # print(scheduler_config)

    return render_template('admin/settings.html', scheduler_config=scheduler_config)


# 处理批量修改网段加入分组
@admin.route("/join_group", methods=['GET', 'POST'])
def join_group():
    if request.method == 'POST':
        # 获取表单输入的值
        # job_seconds = int(request.form.get('job_seconds'))
        network = request.form.get('network')
        group = request.form.get('group')
        print(network, group)

        # 检查是否有数据行填写此网段，若无则返回错误提示，有则下一步
        existing_network = IPTable.query.filter_by(network=network).first()
        if not existing_network:
            # print('网段不存在于任一数据行中')
            response = {
                'status_code': 6001,
                'message': 'Invalid network format!'
            }
            return jsonify(response)

        if not group or str(group).isspace():
            response = {
                'status_code': 6002,
                'message': 'Invalid group_name format!'
            }
            return jsonify(response)
        else:
            # 检查要更新的分组名称是否与其他已存在的分组名称重复
            existing_group = IPGroup.query.filter_by(group=group).first()
            if existing_group:
                # 如果分组名称已存在，则更新 IPTable 表中对应记录的 ip_group_id 字段
                ip_group_id = existing_group.id
            else:
                # 判断分组数据不为空的其他值
                # 创建新分组并保存到 IPTable 表中对应记录的 ip_group_id 字段
                new_group = IPGroup(group=group)
                db.session.add(new_group)
                db.session.flush()
                ip_group_id = new_group.id

    # 查询network=network的数据行
    ip_table = IPTable.query.filter_by(network=network).all()

    # 修改ip_group_id
    # 修改每一行的ip_group_id为1
    for ip_table in ip_table:
        ip_table.ip_group_id = ip_group_id

    try:
        db.session.commit()
        # 添加成功返回 JSON 数据
        response = {
            'status_code': 2001,
            'message': 'Successfully.'
        }

        return jsonify(response)

    except Exception as e:
        db.session.rollback()
        response = {
                'status_code': 6003,
                'message': str(e)
            }
        return jsonify(response)


# 处理配置参数修改
@admin.route("/edit_para", methods=['GET', 'POST'])
def edit_para():
    if request.method == 'POST':
        pass

    response = {
            'status_code': 2001,
            'message': 'Successfully.'
        }

    return jsonify(response)


# 启动定时任务
@admin.route('/start_scheduler', methods=['POST'])
def start_scheduler():
    from app import scheduler

    try:
        if not scheduler.running:
            scheduler.start()  # 如果调度器未在运行，则启动
        else:
            scheduler.shutdown()  # 停止调度器
            scheduler.start()  # 启动调度器
        status = 'success'  # 成功启动，返回状态为 success

    except Exception as e:
        # status = 'failed'  # 停止失败，返回状态为 failed
        status = str(e)  # 停止失败，返回状态为 failed

    return status  # 将状态返回给前端


# 停止定时任务
@admin.route('/stop_scheduler', methods=['POST'])
def stop_scheduler():
    from app import scheduler

    try:
        scheduler.shutdown()  # 停止调度器
        status = 'success'  # 正常停止，返回状态为 success

    except Exception as e:
        # status = 'failed'  # 停止失败，返回状态为 failed
        status = str(e)  # 停止失败，返回状态为 failed

    return status  # 将状态返回给前端


# about页渲染
@admin.route("/about")
def about():

    return render_template('admin/about.html')


# 渲染基本IP地址表框架
@admin.route("/ipshow")
def ipshow():
    return render_template('admin/ipshow.html')


# IP表数据行查询接口
@admin.route("/ipshow_data")
def ipshow_data():
    data = IPTable.query.all()

    ip_list = []
    for ip in data:
        ip_group = IPGroup.query.get(ip.ip_group_id)
        ip_dict = {
            'id': ip.id,
            'ip': ip.ip,
            'mask': ip.mask,
            'mac_add': ip.mac_add,
            'network': ip.network,
            'group_name': ip_group.group,
            'desc': ip.desc,
            'user': ip.user,
            'available': ip.available,
            'created_at': ip.created_at,
            'updated_at': ip.updated_at
        }

        ip_list.append(ip_dict)

    respon_data = {'data': ip_list}

    # 返回带有正确状态码的JSON数据
    return jsonify(respon_data)


# 改
@admin.route('/edit', methods=['POST'])
def edit_row():
    try:
        data = request.get_json()

        # 获取请求中的数据
        row_id = data.get('id')
        ip = data.get('ip')
        mask = data.get('mask')
        mac_add = data.get('mac_add')
        desc = data.get('desc')
        user = data.get('user')
        group_name = data.get('group_name')

        # 根据row_id进行更新操作
        ip_table = IPTable.query.filter_by(id=row_id).first()

        if not ip_table:
            return jsonify(status='error', message='找不到对应的数据行'), 404

        # 判断IP地址的格式是否正确
        if not verify_ipaddress(ip):
            response = {
                'status_code': 4001,
                'message': 'Invalid IP address format!'
            }
            return jsonify(response)

        # 检查数据库中是否存在相同的 IP 记录
        # existing_ip = IPTable.query.filter_by(ip=ip).first()
        # if existing_ip:
        #     response = {
        #         'status_code': 4002,
        #         'message': 'Duplicate IP record.'
        #     }
        #     return jsonify(response)
        ip_table.ip = ip

        # 判断子网掩码的格式是否正确
        if not is_valid_subnet_mask(mask):
            response = {
                'status_code': 4003,
                'message': 'Invalid subnet mask!'
            }
            return jsonify(response)
        ip_table.mask = mask

        # 计算网络号并返回"x.x.x.x/x"格式的信息
        # 此处是画蛇添足，因为python执行到这一步，已经确保IP地址和子网掩码是正确格式
        if not get_network_info(ip, mask):
            response = {
                'status_code': 4004,
                'message': 'Unable to calculate network segment information!'
            }
            return jsonify(response)

        # 计算网段信息的值
        ip_table.network = get_network_info(data.get('ip'), data.get('mask'))

        if group_name and not str(group_name).isspace():
            # 检查要更新的分组名称是否与其他已存在的分组名称重复
            existing_group = IPGroup.query.filter_by(group=group_name).first()
            if existing_group:
                # 如果分组名称已存在，则更新 IPTable 表中对应记录的 ip_group_id 字段
                ip_table.ip_group_id = existing_group.id
            else:
                # 否则创建新分组并保存到 IPTable 表中对应记录的 ip_group_id 字段
                new_group = IPGroup(group=group_name)
                db.session.add(new_group)
                db.session.flush()
                ip_table.ip_group_id = new_group.id

        if mac_add and not str(mac_add).isspace():
            ip_table.mac_add = mac_add
        if desc and not str(desc).isspace():
            ip_table.desc = desc
        if user and not str(user).isspace():
            ip_table.user = user

        # 提交更新操作
        db.session.commit()

        # 返回成功响应
        return jsonify(status_code=2001, message='数据行更新成功')
    except Exception:
        # 返回错误响应
        return jsonify(status='error', message='数据行更新失败'), 500


# 删
@admin.route('/delete', methods=['POST'])
def delete_rows():
    ids = request.get_json().get('ids')  # 获取前端发送的 JSON 数据中的 ids 属性值
    if not ids:
        return {'status_code': 400, 'message': 'No IDs provided'}  # 没有提供有效的 IDs

    result = delete_row(ids)

    if result == -1:
        return {'status_code': 404, 'message': 'Row not found in the database'}  # 数据行不存在
    elif result == 0:
        return {'status_code': 500, 'message': 'Database operation failed'}  # 数据库操作失败
    else:
        return {'status_code': 2001}  # 返回删除成功的状态码


# 删除数据行单行具体操作
def delete_row(ids):
    for id in ids:
        # 根据id查找对应的数据行
        row = IPTable.query.filter_by(id=id).first()
        if row:
            # 如果找到了对应的数据行，则执行删除操作
            try:
                db.session.delete(row)
                db.session.commit()  # 提交数据库修改
            except Exception:
                return 0
        else:
            return -1


# 增
@admin.route('/add', methods=['POST'])
def add_data():
    try:
        data = request.json  # 获取前端提交的数据

        # 判断IP地址的格式是否正确
        if not verify_ipaddress(data['ip']):
            response = {
                'status_code': 4001,
                'message': 'Invalid IP address format!'
            }
            return jsonify(response)

        # 检查数据库中是否存在相同的 IP 记录
        existing_ip = IPTable.query.filter_by(ip=data['ip']).first()
        if existing_ip:
            response = {
                'status_code': 4002,
                'message': 'Duplicate IP record.'
            }
            return jsonify(response)

        # 判断子网掩码的格式是否正确，如正确返回decimal_subnet_mask
        mask = is_valid_subnet_mask(data['mask'])
        if not mask:
            response = {
                'status_code': 4003,
                'message': 'Invalid subnet mask!'
            }
            return jsonify(response)

        # 计算网络号并返回"x.x.x.x/x"格式的信息
        # 此处是画蛇添足，因为python执行到这一步，已经确保IP地址和子网掩码是正确格式
        if not get_network_info(data['ip'], data['mask']):
            response = {
                'status_code': 4004,
                'message': 'Unable to calculate network segment information!'
            }
            return jsonify(response)

        # 计算网段信息的值
        network = get_network_info(data['ip'], data['mask'])

        # 检查要更新的分组名称是否与其他已存在的分组名称重复
        group_name = data['group_name']
        existing_group = IPGroup.query.filter_by(group=group_name).first()
        if existing_group:
            # 如果分组名称已存在，则更新 IPTable 表中对应记录的 ip_group_id 字段
            ip_group = existing_group
        else:
            # 判断分组数据为空的情况
            if not group_name:
                default_group = IPGroup.query.filter_by(group='Default').first()
                ip_group = default_group
            else:
                # 否则创建新分组并保存到 IPTable 表中对应记录的 ip_group_id 字段
                new_group = IPGroup(group=group_name)
                db.session.add(new_group)
                db.session.flush()
                ip_group = new_group

        # 创建新记录并插入到IPTable表中
        ip_table = IPTable(ip=data['ip'], mask=mask, mac_add=data['mac_add'], network=network, desc=data['desc'], user=data['user'], available=bool(data['available']), group=ip_group)
        db.session.add(ip_table)
        db.session.commit()

        # 添加成功返回 JSON 数据
        response = {
            'status_code': 2001,
            'message': 'Data added successfully.'
        }
        return jsonify(response)
    except Exception as e:
        # 发生异常时返回错误信息
        response = {
            'status_code': 5001,
            'message': str(e)
        }
        return jsonify(response), 500


# 分组页面
@admin.route("/ipgroup")
def ipgroup():
    # ip_groups = IPGroup.query.all()
    ip_groups = IPGroup.query.options(db.joinedload(IPGroup.group_item)).all()

    data = []
    for ip_group in ip_groups:
        if not ip_group.group_item:  # 如果ip_group没有对应的IPTable，跳过当前循环
            continue

        networks_set = set()
        for ip_table in ip_group.group_item:
            networks_set.add(ip_table.network)

        networks = [{'name': network, 'id': ip_table.id} for network in networks_set]

        group_data = {'name': ip_group.group, 'id': ip_group.id, 'networks': networks}
        data.append(group_data)

    # print(data)
    return render_template('admin/ipgroup.html', data=data)


@admin.route("/ipgroupdetail", methods=['GET', 'POST'])
def ipgroupdetail():

    if request.method == 'POST':
        data = request.get_json()
        network = data.get('network')
    else:
        network = request.args.get('network')

    ip_tables = IPTable.query.filter_by(network=network).all()

    # 统计available字段
    len_count = len(ip_tables)
    true_count = len([ip_table for ip_table in ip_tables if ip_table.available])
    false_count = len(ip_tables) - true_count

    if ip_tables:
        group_items = []
        # ip_group_id = ip_tables[0].ip_group_id
        for data_row in ip_tables:
            ip_group = IPGroup.query.get(data_row.ip_group_id)
            if ip_group:
                table_data = {
                    'id': data_row.id,
                    'ip': data_row.ip,
                    'mask': data_row.mask,
                    'mac_add': data_row.mac_add,
                    'network': data_row.network,
                    'desc': data_row.desc,
                    'user': data_row.user,
                    'available': data_row.available,
                    'created_at': data_row.created_at,
                    'updated_at': data_row.updated_at,
                    'group_name': ip_group.group
                }
                group_items.append(table_data)

        if request.method == 'POST':
            response = {'data': group_items}

        else:
            response = {
                'status': 'success',
                'network': network,
                'count': {'len_count': len_count, 'true_count': true_count, 'false_count': false_count},
                'group_items': {'data': group_items}
            }
    else:
        response = {
            'status': 'error',
            'message': 'No IPTable data found for the given network'
        }
    # print(response)

    return jsonify(response)
