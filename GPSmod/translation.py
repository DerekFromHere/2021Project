# -*- coding: utf-8 -*-

import json
#import requests
import math
import sys


#key = 'your key here'  # 这里填写你的百度开放平台的key
x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 扁率


def gcj02tobd09(lng, lat):
    """
    火星坐标系(GCJ-02)转百度坐标系(BD-09)
    谷歌、高德——>百度
    :param lng:火星坐标经度
    :param lat:火星坐标纬度
    :return:
    """
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return [bd_lng, bd_lat]


def bd09togcj02(bd_lon, bd_lat):
    """
    百度坐标系(BD-09)转火星坐标系(GCJ-02)
    百度——>谷歌、高德
    :param bd_lat:百度坐标纬度
    :param bd_lon:百度坐标经度
    :return:转换后的坐标列表形式
    """
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return [gg_lng, gg_lat]


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
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [mglng, mglat]


def gcj02towgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    if out_of_china(lng, lat):
        return lng, lat
    dlat = transformlat(lng - 105.0, lat - 35.0)
    dlng = transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]


def transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
        0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret


def transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
        0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret


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


def process_json(input_json_file, output_json_file):
    file_grid = output_json_file + "_grid.json"
    file_heat = output_json_file + "_heat.json"
    fin = open(input_json_file, 'r')
    fout = open(file_heat, 'w')
    fout_ = open(file_grid,'w')

    out = []
    out_ = []
    for eachLine in fin:
        fileName,leftLon,rightLon,topLat,bottomLat,cnt,color = eachLine.split(",")
        data = {}
        data_ = {}
        result1 = wgs84togcj02(float(leftLon),float(topLat))
        result2 = gcj02tobd09(result1[0],result1[1])
        result3 = wgs84togcj02(float(rightLon),float(bottomLat))
        result4 = gcj02tobd09(result3[0],result3[1])
        data[ "lat" ] = result2[1]
        data[ "lng" ] = result2[0]
        data[ "count" ] = cnt
        out += [ data ]
        data_[ "topLat" ] = result2[1]
        data_[ "leftLon" ] = result2[0]
        data_[ "bottomLat" ] = result4[1]
        data_[ "rightLon" ] = result4[0]
        data_[ "cnt" ] = cnt
        data_[ "color" ] = color
        out_ += [ data_ ]
    fout.write(str(out))
    fout_.write(str(out_))
    fin.close()
    fout.close()
    fout_.close()


def processCSV(inputJsonFile, outputJsonFile):
    file_csv = outputJsonFile + ".csv"
    fin = open(inputJsonFile, 'r')
    fout = open(file_csv, 'w')
    for eachLine in fin:
        fileName,addr,topLat,leftLon = eachLine.split(",")
        result1 = bd09togcj02(float(leftLon),float(topLat))
        result2 = gcj02towgs84(result1[0],result1[1])
        out=str(fileName) + "," + str(addr) + "," + str(result2[0]) + "," + str(result2[1]) + "\n"
        fout.write(str(out))
    fin.close()
    fout.close()




if __name__ == '__main__':
    if sys.argv[3] == "json":
        process_json(sys.argv[1], sys.argv[2])
    else:
        processCSV(sys.argv[1],sys.argv[2])