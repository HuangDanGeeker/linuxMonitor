import socket
import simplejson
import os
import pyServer.MessagePackage as MessagePackage
import time
import requests
import threading


clients = {}


def deal_accpet():
    while True:
        client, addr = s.accept()
        print('连接地址：', addr)
        buff = client.recv(1024)
        print("接收到" + str(buff))
        # 接收到的消息为linux主机首次连接消息
        buff = buff.decode().replace("\n", "")
        data = simplejson.loads(str(buff))
        print("json化" + str(data))
        mp = MessagePackage.MessagePackage('create', data['host_name'])
        global clients
        clients[mp.get_uuid()] = client
        response = requests.post('http://127.0.0.1:8000/post', data=mp.to_json())
        # print("响应200 = " + str(response))
        threading.Thread(target=deal_receive, args=[client]).start()


def deal_receive(client):
    print("deal_receive(client)")
    while True:
        buff = client.recv(2048)
        print("接收到" + str(buff))
        if 'a' == buff[0]:      # 接收到的消息为连接活确认
            mp = MessagePackage.MessagePackage('warn', buff.decode().s[1:])
        else:                   # 接收到的消息为linux主机状态信息
            buff = buff.decode().replace("\n", "").replace(",]", "]")
            data = simplejson.loads(buff)
            print("json化" + str(data))
            mp = MessagePackage.MessagePackage('update', data['host_name'],
                                               data['memInfo'], data['cpuUser'],
                                               eval(str(data['processInfo']))
                                               )
        response = requests.post(url='http://127.0.0.1:8000/post',
                                 headers={'Content-Type': 'application/json'},
                                 data=mp.to_json())
        # print("响应200 = " + str(response))


def deal_order():
    while True:
        try:
            with open("order.txt", 'r+') as file_handler:
                with open("./temp_order.txt", "a+") as tempfile_handler:
                    lines = file_handler.readlines()
                    if 0 == len(lines):
                        time.sleep(2000)
                        continue
                    uuid = file_handler.readline()
                    pid = file_handler.readline()
                    del lines[0:2]
                    for line in lines:
                        tempfile_handler.writelines(line)
            os.remove('order.txt')
            os.rename("temp_order.txt", 'order.txt')
            clients[uuid].send(pid)
        except Exception as e:
            time.sleep(2000)


def check_alive():
    global clients
    while True:
        if 0 == len(clients):
            time.sleep(2000)
        else:
            for client in clients:
                client.sendall("")  # 客户端'活'检查


if __name__ == '__main__':
    s = socket.socket()
    host = socket.gethostname()
    port = 8124
    s.bind(("192.168.43.30", port))
    s.listen(5)
    print("start TCP server")
    threading.Thread(target=deal_accpet).start()
    threading.Thread(target=deal_order).start()
    threading.Thread(target=check_alive).start()


