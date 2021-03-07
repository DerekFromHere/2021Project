from socket import *
import json
import threading
import GPSmod
import time

HOST = gethostname()    #本机IP地址
PORT = 8777             #监听的端口
BUFFERSIZE = 65536
REQUEST_TYPES = ['request_serv', 'data_on_request', 'confirm_recv']
TIMEOUT = 5


class RequestHandler(threading.Thread):
    def __init__(self, curClient, message):
        super().__init__()
        self.curClient = curClient
        self.message = message
        self.serviceName = ''
        self.jMessage = dict()

    def run(self):
        try:
            self.jMessage = json.loads(self.message)    # 尝试将接收到的消息转换为dict
        except Exception as e:
            print("Cannot convert message to a json dict.")
            return
        if self.jMessage['requestType'] != REQUEST_TYPES[0]:    # 检查请求类型
            print("Error: requestType not matched\nReceived:"+jMessage['requestType']+
            '\nExpected:'+REQUEST_TYPES[0])
        elif self.jMessage['serviceName'] != self.serviceName:  # 检查服务名称
            print("Error: serviceName not matched\nReceived:"+jMessage['serviceName']+
            '\nExpected:'+self.serviceName)
        else:   # 若请求类型与请求名称都正确，进入处理请求环节
            self.handleRequest()
            self.getConfirm(TIMEOUT)
    
    def handleRequest(self):
        pass

    def getConfirm(self, timeout):
        pass


class PositionReceiver(RequestHandler):
    def __init__(self, curClient, message):
        super().__init__(curClient, message)
        self.serviceName = 'PositionUpload'

    def handleRequest(self):
        # 传出data_on_request，关闭curClient
        response = dict()
        response['requestType'] = REQUEST_TYPES[1]
        response['serviceName'] = self.serviceName
        jsonStr = json.dumps(response)
        self.curClient.send(jsonStr.encode())
        # self.jMessage就是存储位置信息的dict，可以在这里进行操作

    def getConfirm(self, timeout):
        '''
        :param timeout: unit: s
        '''
        startTime = time.clock()
        while time.clock() - startTime < timeout:
            try:
                bMessage = self.curClient.recv(BUFFERSIZE)
            except Exception as error:
                pass
            finally:
                jMessage = bMessage.decode()
                dMessage = json.loads(jMessage)
                if dMessage['requestType'] == REQUEST_TYPES[2] and \
                    dMessage['serviceName'] == self.serviceName:
                    return
                elif dMessage['requestType'] != REQUEST_TYPES[2]:
                    raise Exception("Error: requestType not matched\nReceived:"+jMessage['requestType']+
                    '\nExpected:'+REQUEST_TYPES[2])
                elif dMessage['serviceName'] != self.serviceName:
                    raise Exception("Error: serviceName not matched\nReceived:"+jMessage['serviceName']+
                    '\nExpected:'+self.serviceName)


class CallInfoReceiver(RequestHandler):
    def __init__(self, curClient, message):
        super().__init__(curClient, message)
        self.serviceName = 'CallInfoUpload'

    def handleRequest(self):
        # 传出data_on_request，关闭curClient
        response = dict()
        response['requestType'] = REQUEST_TYPES[1]
        response['serviceName'] = self.serviceName
        jsonStr = json.dumps(response)
        self.curClient.send(jsonStr.encode())
        # self.jMessage就是存储通话记录信息的dict，可以在这里进行操作

    def getConfirm(self, timeout):
        '''
        :param timeout: unit: s
        '''
        startTime = time.clock()
        while time.clock() - startTime < timeout:
            try:
                bMessage = self.curClient.recv(BUFFERSIZE)
            except Exception as error:
                pass
            finally:
                jMessage = bMessage.decode()
                dMessage = json.loads(jMessage)
                if dMessage['requestType'] == REQUEST_TYPES[2] and \
                    dMessage['serviceName'] == self.serviceName:
                    return
                elif dMessage['requestType'] != REQUEST_TYPES[2]:
                    raise Exception("Error: requestType not matched\nReceived:"+jMessage['requestType']+
                    '\nExpected:'+REQUEST_TYPES[2])
                elif dMessage['serviceName'] != self.serviceName:
                    raise Exception("Error: serviceName not matched\nReceived:"+jMessage['serviceName']+
                    '\nExpected:'+self.serviceName)


def main():
    sockfd = socket(AF_INET, SOCK_STREAM)
    sockfd.bind((HOST, PORT))
    sockfd.listen(512)
    while True:
        connfd, addr = sockfd.accept()
        message = ''
        while not message:
            message = connfd.recv(BUFFERSIZE).decode()
        connfd.setblocking(False)
        # 任务分发给线程
        jMessage = json.loads(message)
        if jMessage['serviceName'] == 'PositionUpload':
            PositionReceiver(connfd, message).start()
        elif jMessage['serviceName'] == 'CallInfoUpload':
            CallInfoReceiver(connfd, message).start()
        else:
            print("Received an unknown request with the serviceName:" + \
jMessage['serviceName'])


