from socket import *
import json
import threading
import GPSmod
import time

SERVER_HOST = '127.0.0.1'    # 服务器IP地址
SERVER_PORT = 8777           # 服务器的端口
BUFFERSIZE = 65536           # 单次接收的bytes的最大大小
REQUEST_TYPES = ['request_serv', 'data_on_request', 'confirm_recv']  # 请求的三种类型
TIMEOUT = 5                  # 默认超时等待时间5秒

class RequestSender(threading.Thread):
    '''
    作为基类，用于发送请求/数据到服务器
    '''
    def __init__(self):
        # 创建curClient作为当前通信使用的socket
        super().__init__()
        self.curClient = socket(AF_INET, SOCK_STREAM)

    
    def run(self):
        self.sendRequest()
        self.handleData(TIMEOUT)
    
    def sendRequest(self):
        pass

    def handleData(self, timeout):
        '''
        :param timeout: unit: s
        '''
        pass


class PositionSender(RequestSender):
    '''
    上传位置信息
    '''
    def __init__(self):
        super().__init__()
        self.com_port = 'com3'  #当前GPS定位设备所在串口
        self.serviceName = 'PositionUpload'

    def sendRequest(self):
        try:
            self.curClient.connect((SERVER_HOST, SERVER_PORT))  # 尝试连接服务器
        except Exception as error:
            print("Error raised when connecting to server.")    # 若失败，打印错误信息
        else: # 若成功连接，立刻发送位置数据
            lPosition = GPSmod.gps_demo.gps_read(self.com_port)
            response = dict()
            response['UTCTime'] = lPosition[0]
            response['latitude'] = lPosition[1]
            response['latitudeHalf'] = lPosition[2]
            response['longitude'] = lPosition[3]
            response['longitudeHalf'] = lPosition[4]
            response['requestType'] = REQUEST_TYPES[0]
            response['serviceName'] = self.serviceName
            jsonStr = json.dumps(response) # 将字典转换为json形式字符串
            self.curClient.send(jsonStr.encode()) # 发送至服务器

    def handleData(self, timeout):
        startTime = time.clock()
        # 等待时长为timeout
        while time.clock() - startTime < timeout:
            pass
        # 等待完毕，尝试接收数据
        try:
            bMessage = self.curClient.recv(BUFFERSIZE)
        except Exception as error:
            print("Error raised when receiving message form server.")
        else:
            message = bMessage.decode()
            jMessage = json.loads(message)
            if jMessage['requestType'] != REQUEST_TYPES[1]:  # 若请求类型不符，打印错误
                print("Error: requestType not matched\nReceived:"+jMessage['requestType']+
                '\nExpected:'+REQUEST_TYPES[1])
            elif jMessage['serviceName'] != self.serviceName:   # 若请求的服务名称不符，打印错误
                print("Error: serviceName not matched\nReceived:"+jMessage['serviceName']+
                '\nExpected:'+self.serviceName)
            else:
                # 传出confirm_recv
                response = dict()
                response['requestType'] = REQUEST_TYPES[2]
                response['serviceName'] = self.serviceName
                jsonStr = json.dumps(response) # 将字典转换为json形式字符串
                self.curClient.send(jsonStr.encode())
        
        self.curClient.close()  # 会话结束，关闭socket


class CallInfoSender(RequestSender):
    '''
    与上面的类几乎一样，上传通话记录信息
    '''
    def __init__(self):
        super().__init__()
        self.com_port = 'com3'
        self.serviceName = 'CallInfoUpload'

    def sendRequest(self):
        try:
            self.curClient.connect((SERVER_HOST, SERVER_PORT))
        except Exception as error:
            print("Error raised when connecting to server.")
        else:
            response = dict()
            # 在这里编辑需要上传的打电话信息
            response['callTime'] = "..."
            jsonStr = json.dumps(response) # 将字典转换为json形式字符串
            self.curClient.send(jsonStr.encode()) # 发送至服务器

    def handleData(self, timeout):
        startTime = time.clock()
        # 等待timeout
        while time.clock() - startTime < timeout:
            pass

        try:
            bMessage = self.curClient.recv(BUFFERSIZE)
        except Exception as error:
            print("Error raised when receiving message from server.")
        else:
            message = bMessage.decode()
            jMessage = json.loads(message) # 将json字符串转换为dict
            if jMessage['requestType'] != REQUEST_TYPES[1]:
                print("Error: requestType not matched\nReceived:"+jMessage['requestType']+
                '\nExpected:'+REQUEST_TYPES[1])
            elif jMessage['serviceName'] != self.serviceName:
                print("Error: serviceName not matched\nReceived:"+jMessage['serviceName']+
                '\nExpected:'+self.serviceName)
            else:
                # 传出confirm_recv
                response = dict()
                response['requestType'] = REQUEST_TYPES[2]
                response['serviceName'] = self.serviceName
                jsonStr = json.dumps(response)
                self.curClient.send(jsonStr.encode())
        
        self.curClient.close()  # 会话结束，关闭socket


def main():
    pass

if __name__ == '__main__':
    main()
