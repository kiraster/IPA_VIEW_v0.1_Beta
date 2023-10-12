'''
可复用功能函数
'''
import ipaddress


# 判断是否为正确IPv4地址格式
def verify_ipaddress(ip):
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ValueError:
        return False


# 判断是否为正确掩码格式
def is_valid_subnet_mask(subnet_mask):
    if subnet_mask.isdigit() and 0 <= int(subnet_mask) <= 32:
        # 处理 "0-32" 格式的字符串
        binary_subnet_mask = '1' * int(subnet_mask) + '0' * (32 - int(subnet_mask))
    else:
        # 处理 "255.255.255.0" 格式的字符串
        try:
            subnet = ipaddress.IPv4Network("0.0.0.0/"+subnet_mask, strict=False)
            binary_subnet_mask = "".join(bin(int(x)).replace("0b", "").zfill(8) for x in subnet.netmask.packed)
        except ValueError:
            return False

    # 将二进制的子网掩码转换为十进制点分十进制格式
    decimal_subnet_mask = '.'.join([str(int(binary_subnet_mask[i:i+8], 2)) for i in range(0, 32, 8)])

    # 使用ipaddress模块进行校验
    try:
        subnet = ipaddress.IPv4Network("0.0.0.0/" + decimal_subnet_mask, strict=False)
        if str(subnet.netmask) == decimal_subnet_mask:
            return decimal_subnet_mask
        else:
            # 如果不相等，说明转换失败
            return False
    except ValueError:
        return False


# 根据IP地址和子网掩码计算返回网段信息
def get_network_info(ip_address, subnet_mask):
    try:
        network = ipaddress.IPv4Network(ip_address + '/' + subnet_mask, strict=False)
        network_cidr = str(network)

        return network_cidr
    except ValueError:
        return None

# mac地址判断及统一格式


# 计算IP地址数量

def calc_div_count(network):
    cidr_index = network.find('/')  # 查找IP地址网段中的CIDR前缀
    if cidr_index == -1:  # 如果没有CIDR前缀，则默认为32（IPv4）或128（IPv6）
        return pow(2, 32) if ':' not in network else pow(2, 128)

    cidr = int(network[cidr_index+1:])
    prefix = network[:cidr_index]
    binary_prefix = ipaddress.IPv4Address(prefix).packed if ':' not in network else ipaddress.IPv6Address(prefix).packed
    div_count = pow(2, len(binary_prefix) * 8 - cidr)  # 计算网段内的IP地址数量

    return div_count
