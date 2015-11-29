#coding=utf-8
import sys
import socket
import getopt
import threading
import subprocess

#定义一些全局变量
listen                = False
command               = False
upload                = False
execute               = ""
target                = ""
upload_distination    = ""
port                  = 0

#主函数处理命令行参数
def usage():
    print "Cheng Net Tool"
    print
    print "Usage: chengnet.py -t target_host -p port"
    print "-l --listen                 -listen on [host]:[port] for incoming connection"
    print "-e --execute=file_to_run    -execute the given file upon receiving a connection"
    print "-c --command                -initialize a command shell"
    print "-u --upload=destination     -upon receiving connection upload a file and write to [destination]"
    print
    print
    print "Examples:"
    print "chengNet.py -t 192.168.0.1 -p 55555 -l -c"
    print "chengNet.py -t 192.168.0.1 -p 55555 -l -u=c:\\target.exe"
    print "chengNet.py -t 192.168.0.1 -p 55555 -l -e=\"cat /etc/passed\""
    print "echo 'ANCDEFGHI' | ./chengNet.py -t 192.168.11.12 -p 135"
    sys.exit(0)

def main():
    global listen
    global port
    global execute
    global command
    global upload_distination
    global target

    if not len(sys.argv[1:]):
        usage()

    #读取命令行
    try:
        opts,args = getopt.getopt(sys.argv[1:],"hle:t:p:cu",["help","listen","execute","target","port","command","upload"])
    except getopt.GetoptError as err:
        print str(err)
        usage()

    for o,a in opts:
        if o in ("-h","--help"):
            usage()
        elif o in ("-l","--listen"):
            listen = True
        elif o in ("-e","--execute"):
            execute =a
        elif o in ("-c","--commandshell"):
            command =True
        elif o in ("-u","--upload"):
            upload_distination = a
        elif o in ("-t","--target"):
            target = a
        elif o in ("-p","--port"):
            port = int(a)
        else:
            assert False,"Unhandled Option"


    #我们是进行监听还是仅从标准输入发送数据？
    if not listen and len(target) and port >0:
        #从命令行读取内存数据
        #这里将阻塞，所以不再向标准输入发送数据时发送CTRL-D
        buffer = sys.stdin.read()

        #发送数据
        client_sender(buffer)

    #监听并准备上传文件，执行命令
    #放置一个反弹shell
    #取决于上面的命令行选项
    if listen:
        server_loop()


main()

def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        #连接到目标主机
        client.connect((target,port))

        if len(buffer):
            client.send(buffer)



        while True:
            #现在等待回传数据
            recv_len = 1
            response = ""

            while recv_len:

                data     = client.recv(4096)
                recv_len = len(data)
                response+= data

                if recv_len < 4096:
                    break

            print response,

            #等待更多输入
            buffer = raw_input("")
            buffer += "\n"

            #发送出去
            client.send(buffer)

    except:
        print "[*] Exception ! Exitting"
        client.close()