import socket
import os
import subprocess
import select
import sys

TIMEOUT = 20


s = socket.socket()
host = "127.0.0.1"
port = 12345

s = socket.socket()
s.connect((host,port))
conn_id = s.recv(1024)
conn_id = conn_id.decode("utf-8")
instructions = s.recv(1024)
print(instructions.decode("utf-8"))
message = "NA"


def GameOver():
    msg = s.recv(1024)
    print(msg.decode("utf-8"))
    s1 = s.recv(1024)
    print(s1.decode("utf-8"))
    s2 = s.recv(1024)
    print(s2.decode("utf-8"))
    s3 = s.recv(1024)
    print(s3.decode("utf-8"))
    t = s.recv(1024)
    print(t.decode("utf-8"))
    sys.exit()
    
def Main():
    while True:
        data = s.recv(1024)
        response = data.decode("utf-8")
        if(response == 'quit'):
            GameOver()
        if(len(data)>0):
            print("question number " ,response)

        lst = select.select([sys.stdin,s],[],[],10)
        if(len(lst[0])>0) and (lst[0][0]==sys.stdin):
            bv = input()
            bv = conn_id + " " + bv 
            s.sendall(bv.encode("utf-8"))
        elif (len(lst[0])>0) and (lst[0][0]==s):
            bi = s.recv(1024)
            bi = bi.decode("utf-8")
            print(bi)
            ansinfo = s.recv(1024)
            ansinfo = ansinfo.decode("utf-8")
            print(ansinfo)
            continue
        else:
            print("TIME's UP.")
        bi = s.recv(1024)
        bi = bi.decode("utf-8")
        if(bi == 'Your Answer:'):
            print("You have 30s to answer the question.\n"+bi)
            ansinfo = select.select([sys.stdin],[],[],30)
            if(len(ansinfo[0])>0):
                answer = input()
                s.sendall(answer.encode("utf-8"))
                ansinfo = s.recv(1024)
                print(ansinfo.decode("utf-8"))
            else:
                print("Time is finished")
                s.sendall(message.encode("utf-8"))
    s.close()
Main()
