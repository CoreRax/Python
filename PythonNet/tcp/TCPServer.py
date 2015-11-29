#coding=utf-8
#创建一个标准多线程TCP服务端
import socket
import threading

bind_ip = "127.0.0.1"
bind_port =9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((bind_ip,bind_port))

server.listen(5)

print ("[*] Listening on %s:%d" %(bind_ip,bind_port))

def handel_client(client_socket):
    #打印客户端发送的内容
    request = client_socket.recv(1024)

    print ("[*] Received: %s" %request)

    #返还一个数据包
    client_socket.send("ACK!")
    client_socket.close()


while True:
    client,addr = server.accept()

    print ("[*] Accept connection from: %s:%d" %(addr[0],addr[1]))

    #挂起客户端线程，处理传入数据
    client_handler = threading.Thread(target=handel_client,args=(client,))
    client_handler.start()