import time, re
from pysnmp.hlapi import *
from pysnmp.entity.rfc3413.oneliner import cmdgen

from .config import SNMPConfig


# oid值
oid_dict = {
    "arpIpMac": (1, 3, 6, 1, 2, 1, 4, 22, 1, 2)
}


class Snmp:

    def __init__(self, ip, community, mpModel=1, port=161, timeout=1000):
        self.ip = ip
        self.community = community
        self.mpModel = mpModel
        self.port = port
        self.timeout = timeout
        self.result = {}

    def snmpWalk(self, oid, n=0):
        iterator = bulkCmd(SnmpEngine(),
                           CommunityData(self.community),
                           UdpTransportTarget((self.ip, self.port)),
                           ContextData(),
                           0, 50,
                           ObjectType(ObjectIdentity(oid)),
                           lexicographicMode=False)
        result = []
        for (errorIndication, errorStatus, errorIndex, varBinds) in iterator:
            if not errorIndication and not errorStatus:
                for varBind in varBinds:
                    oid_value = [x.prettyPrint() for x in varBind]
                    if oid_value and len(oid_value) >= 2 and str(oid_value[1]).strip() != '':
                        result.append(oid_value)
            else:
                if n < 3:
                    n += 1
                    time.sleep(1)
                    # print(self.ip, oid, '重试snmp_bulkget')
                    return self.snmpWalk(oid, n)
        return result

    def setResult(self, name, oid_result):
        if oid_result and len(oid_result) >= 1 and len(oid_result[0]):
            self.result.update({name: str(oid_result[0][1]).upper()})

    def getArpIpMacTable(self, oid, reg):
        ArpIpMacTableResult = self.snmpWalk(oid)
        # print("ArpIpMacTableResult=", ArpIpMacTableResult)
        # ArpIpMacTableInfoResult = []
        # for item in ArpIpMacTableResult:
        #     portInfo = item[0]
        #     match = re.search(reg, portInfo)
        #     portIndex = match.group(1) if match and len(match.groups()) else ""
        #     ArpIpMacTableInfoResult.append({'ip': portIndex, 'mac': str(item[1][2:]).upper()})
        # self.result.update({'ArpIpMac': ArpIpMacTableInfoResult})
        return ArpIpMacTableResult


# 处理snmp结果
def res_process(data):

    try:

        response_data = []

        for item in data:
            # 使用正则表达式匹配IP地址的部分
            ip = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$', item[0])

            if ip:
                ip_address = ip.group(1)

            # 去掉0x前缀并转换为大写字母
            hex_mac = item[1][2:]

            if hex_mac:
                # 使用字符串操作添加分隔符-
                mac_address = '-'.join([hex_mac[i:i+4] for i in range(0, len(hex_mac), 4)])

            item_data = {'ip': ip_address, 'mac_add': mac_address}
            response_data.append(item_data)

        return response_data
    except Exception:
        return False


# 结果写入数据库，不能搞太频繁，机子受不了，或者定时的时定长点
def add_data(data):
    from . import db, app
    from app.models import IPTable
    from app.admin.lib import get_network_info
    from datetime import datetime

    with app.app_context():
        try:
            for item_data in data:
                # 提取需要插入或更新的字段值
                ip = item_data.get('ip')
                mac_add = item_data.get('mac_add')

                # 查询数据库中是否已存在相同的记录
                existing_record = IPTable.query.filter_by(ip=ip).first()

                if existing_record:
                    # 更新记录
                    existing_record.mac_add = mac_add
                    existing_record.available = True
                    existing_record.updated_at = datetime.utcnow()
                else:
                    # 计算网段信息的值，不能获取IP地址的掩码默认24位
                    network = get_network_info(ip, '255.255.255.0')
                    # 查询network网段是否已存在于数据库中
                    existing_network_record = IPTable.query.filter_by(network=network).first()
                    # 根据查询结果决定逻辑分支
                    if existing_network_record:
                        # 如果网络已存在，则获取其所属的分组ID
                        ip_group_id = existing_network_record.ip_group_id
                    else:
                        # 如果网络不存在，则准备创建新的网络记录，默认ip_group_id为1
                        ip_group_id = 1
                    # 创建新的IPTable记录
                    new_data = IPTable(ip=ip, mask='255.255.255.0', mac_add=mac_add, network=network, available=True,
                                       ip_group_id=ip_group_id)
                    db.session.add(new_data)

            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print('写入或更新数据出错了' + str(e))
            return False


# 被定时任务调用的函数
def get_arp_table():

    # from config import SNMPConfig

    snmp_data = SNMPConfig().SNMP_DATA

    for item in snmp_data:

        snmp = Snmp(item['snmp_host'], item['snmp_community'])

        res = snmp.getArpIpMacTable(oid_dict.get('arpIpMac'), r'SNMPv2-SMI::mib-2.4.22.1.2.5.(\S+)')

        # print(res)

        res_processed = res_process(res)
        # print(res_processed)
        if not res_processed:
            print('轮询任务出错了')
            return

        add_res = add_data(res_processed)
        if not add_res:
            print('写入或更新数据出错了')
            return


# 当超过30分钟没有updated_at值更新，则available值置为False
def update_available():

    from datetime import datetime, timedelta
    from app.models import IPTable
    from app import db, app
    from app.config import SNMPConfig

    with app.app_context():
        # 获取当前时间
        current_time = datetime.utcnow()

        # 计算时间阈值（30分钟之前的时间）
        threshold_time = current_time - timedelta(minutes=SNMPConfig.REFRESH_TIME)

        # 查询updated_at时间与当前时间相差30分钟以上的数据行
        ip_table_list = IPTable.query.filter(IPTable.updated_at < threshold_time).all()

        # 修改每一行的available值为False
        for ip_table in ip_table_list:
            ip_table.available = False

        # print('DONE>>>>>')

        # 提交修改到数据库中
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False


# if __name__ == '__main__':

#     from config import SNMPConfig

#     snmp_data = SNMPConfig().SNMP_DATA

#     for item in snmp_data:

#         snmp = Snmp(item['snmp_host'], item['snmp_community'])

#         res = snmp.getArpIpMacTable(oid_dict.get('arpIpMac'), r'SNMPv2-SMI::mib-2.4.22.1.2.5.(\S+)')

#         # print(res)

#         res_processed = res_process(res)
#         # print(res_processed)

#         add_res = add_data(res_processed)
#         if not add_res:
#             print('写入或更新数据出错了')