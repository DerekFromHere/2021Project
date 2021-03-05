from socket import *
import json
import threading
import GPSmod
import time

SERVER_HOST = '127.0.0.1'    #本机IP地址
SERVER_PORT = 8777             #监听的端口
BUFFERSIZE = 65536
REQUEST_TYPES = ['request_serv', 'data_on_request', 'confirm_recv']
TIMEOUT = 5

class RequestSender(threading.Thread):

    def __init__(self):
        # connect，然后作为curClient
        super().__init__()
        self.curClient = socket(AF_INET, SOCK_STREAM)
        # self.curClient.connect((SERVER_HOST, SERVER_PORT))
        # self.message = message
    
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

    def __init__(self):
        super().__init__()
        self.com_port = 'com3'
        self.serviceName = 'PositionUpload'

    def sendRequest(self):
        try:
            self.curClient.connect((SERVER_HOST, SERVER_PORT))
        except Exception as error:
            print("Error raised when connecting to server.")
        else:
            lPosition = GPSmod.gps_demo.gps_read(self.com_port)
            response = dict()
            response['UTCTime'] = lPosition[0]
            response['latitude'] = lPosition[1]
            response['latitudeHalf'] = lPosition[2]
            response['longitude'] = lPosition[3]
            response['longitudeHalf'] = lPosition[4]
            response['requestType'] = REQUEST_TYPES[0]
            response['serviceName'] = self.serviceName
            jsonStr = json.dumps(response)
            self.curClient.send(jsonStr.encode())

    def handleData(self, timeout):
        startTime = time.clock()
        while(time.clock() - startTime < timeout):
            try:
                bMessage = self.curClient.recv(BUFFERSIZE)
            except Exception as error:
                print("Error raised when connecting to server.")
            else:
                message = bMessage.decode()
                jMessage = json.loads(message)
                if jMessage['requestType'] != REQUEST_TYPES[1]:
                    print("Error: requestType not matched\nReceived:"+jMessage['requestType']+
                    '\nExpected:'+REQUEST_TYPES[1])
                elif jMessage['serviceName'] != self.serviceName:
                    print("Error: serviceName not matched\nReceived:"+jMessage['serviceName']+
                    '\nExpected:'+self.serviceName)
                else:
                    # 传出confirm_recv，关闭curClient
                    response = dict()
                    response['requestType'] = REQUEST_TYPES[2]
                    response['serviceName'] = self.serviceName
                    jsonStr = json.dumps(response)
                    self.curClient.send(jsonStr.encode())
                    self.curClient.close()


class CallInfoSender(RequestSender):
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
            lPosition = GPSmod.gps_demo.gps_read(self.com_port)
            response = dict()
            # 在这里编辑需要上传的打电话信息
            response['callTime'] = "..."
            jsonStr = json.dumps(response)
            self.curClient.send(jsonStr.encode())

    def handleData(self, timeout):
        startTime = time.clock()
        while(time.clock() - startTime < timeout):
            try:
                bMessage = self.curClient.recv(BUFFERSIZE)
            except Exception as error:
                print("Error raised when connecting to server.")
            else:
                message = bMessage.decode()
                jMessage = json.loads(message)
                if jMessage['requestType'] != REQUEST_TYPES[1]:
                    print("Error: requestType not matched\nReceived:"+jMessage['requestType']+
                    '\nExpected:'+REQUEST_TYPES[1])
                elif jMessage['serviceName'] != self.serviceName:
                    print("Error: serviceName not matched\nReceived:"+jMessage['serviceName']+
                    '\nExpected:'+self.serviceName)
                else:
                    # 传出confirm_recv，关闭curClient
                    response = dict()
                    response['requestType'] = REQUEST_TYPES[2]
                    response['serviceName'] = self.serviceName
                    jsonStr = json.dumps(response)
                    self.curClient.send(jsonStr.encode())
                    self.curClient.close()


def main():

