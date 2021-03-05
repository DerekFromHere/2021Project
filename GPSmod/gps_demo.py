import serial
import time
import re
import math
# 定义常量
x_PI = 3.14159265358979324 * 3000.0 / 180.0
PI = 3.1415926535897932384626  # π
A = 6378245.0  # 长半轴
EE = 0.00669342162296594323  # 扁率
COM_PORT = "com4"  # 定义端口


def transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
        0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 *
            math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * PI) + 40.0 *
            math.sin(lat / 3.0 * PI)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * PI) + 320 *
            math.sin(lat * PI / 30.0)) * 2.0 / 3.0
    return ret


def transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
        0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 *
            math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * PI) + 40.0 *
            math.sin(lng / 3.0 * PI)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * PI) + 300.0 *
            math.sin(lng / 30.0 * PI)) * 2.0 / 3.0
    return ret


def gps_parse(ad):
    r = []
    lines = []
    load = []
    t = float(ad[1])
    ad = ad[2:6]
    for ad_one in ad:
        ad_one = ad_one.split('.')
        if len(ad_one) > 1:
            d = int(ad_one[0][:-2])
            m = float(ad_one[0][-2:] + '.' + ad_one[1])
            p = d + m / 60
            load.append(p)

        else:
            lines.append(ad_one[0])
    load = load[::-1]
    load = wgs84togcj02(*load)
    load = gcj02tobd09(*load)
    load = load[::-1]
    r.append(t)
    for ipp, fx in enumerate(lines):
        r.append(load[ipp])
        r.append(fx)

    return r


def out_of_china(lng, lat):
    """
    判断是否在国内，不在国内不做偏移
    :param lng:
    :param lat:
    :return:
    """
    if lng < 72.004 or lng > 137.8347:
        return True
    if lat < 0.8293 or lat > 55.8271:
        return True
    return False


def gcj02tobd09(lng, lat):
    """
    火星坐标系(GCJ-02)转百度坐标系(BD-09)
    谷歌、高德——>百度
    :param lng:火星坐标经度
    :param lat:火星坐标纬度
    :return:
    """
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_PI)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_PI)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return [bd_lng, bd_lat]


def wgs84togcj02(lng, lat):
    """
    WGS84转GCJ02(火星坐标系)
    :param lng:WGS84坐标系的经度
    :param lat:WGS84坐标系的纬度
    :return:
    """
    if out_of_china(lng, lat):  # 判断是否在国内
        return lng, lat
    dlat = transformlat(lng - 105.0, lat - 35.0)
    dlng = transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * PI
    magic = math.sin(radlat)
    magic = 1 - EE * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((A * (1 - EE)) / (magic * sqrtmagic) * PI)
    dlng = (dlng * 180.0) / (A / sqrtmagic * math.cos(radlat) * PI)
    mglat = lat + dlat
    mglng = lng + dlng
    return [mglng, mglat]


def monitor(port):
    """
    一个被阻塞的进程，可以一直读取gps模块返回的信息，并保存在result中。
    2021/2/15: 现在已经不是阻塞的了，读到信息便会返回
    :param port: 端口的句柄
    result：list [UTC时间，纬度，纬度半球，经度，经度半球]
    UTC时间：float 格式 hhmmss.000
    纬度：float 单位：度
    纬度半球： str
    经度：float 单位：度
    经度半球：str

    """
    time.sleep(1)
    while 1:
        result = port.readline()
        # print(type(result))
        result = result.decode(encoding='ascii')
        # print(result)
        if result != b'':
            pattern = r"\$GNGGA,.*"
            result = re.findall(pattern, result)
            if len(result) != 0:
                result = result[0]
                result = result.split(",")
                # print(result)
                result = gps_parse(result)
                # print(result)
                return result


def gps_read(com_port):
    """
    主函数，负责打开串口
    """
    try:
        with serial.Serial(com_port, baudrate=9600, timeout=5) as port:
            if port.isOpen():  # 判断串口连接情况
                print(port.name + ' is open...!!!')
                # print(at(port))
                return monitor(port)
    except serial.serialutil.SerialException:
        print(f"Error: Serial {com_port} access denied")


gps_read(COM_PORT)
