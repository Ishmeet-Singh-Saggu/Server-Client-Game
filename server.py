import socket
import sys
import threading
import time
from queue import Queue
import select
import operator
import subprocess

conn_id = 0
NUMBER_OF_THREADS = 3

all_connection_list = []
JOB_NUMBER = [1,2]
queue = Queue()
allcon = {}
scores = {}
all_address = []

instructions = "Welcome to the Quiz.\nI am your host.\nYou can press any button as buzzer.\n"
q = list(range(0,20))
a = list(range(0,20))

def create_socket():
    try:
        global host
        global port
        global s
        host = ""
        port = 12345
        s = socket.socket()
    except socket.error as err:
        print("Socket cannot be created :",err)

def bind_socket():
    try:
        global host
        global port
        global s
        s.bind((host,port))
        print("Binding Port ...")
        s.listen(5)
    except socket.error as err:
        print("Socket cannot be binded :",err)
        print("Retrying again ....")
        bind_socket()


def accepting_connections():
    for conn in allcon:
        allcon[conn].close()
    count = 1
    global conn_id
    while(len(allcon)<3):
            conn,address = s.accept()
            s.setblocking(1)
            scores[conn_id] = 0
            allcon[conn_id] = conn
            all_address.append(address)
            conn.send(str.encode(str(conn_id)))
            conn_id += 1
            print("Player",count,"joined")
            count += 1
    for conn in allcon:
        print(conn,allcon[conn])
        all_connection_list.append(allcon[conn])
        allcon[conn].send(str.encode(instructions))
    StartLoop()

def StartLoop():
    global quesno 
    quesno = 0
    while True:
        try:
            print("Inside Loop")
            running = True
            while running:
                sendques(quesno)
                buzzer_recv = select.select(all_connection_list,[],[],15)
                print(buzzer_recv)
                if(len(buzzer_recv[0])>0):
                    bd = buzzer_recv[0][0].recv(1024)
                    bd = bd.decode("utf-8")
                    connection_id,bd = bd.split()
                    print(connection_id, bd)
                    sendbuzzerback(connection_id)
                    get_answer(connection_id)
                else:
                    sendbuzzerback(-1)
                quesno += 1
                if(quesno == len(q)):
                    FinishLoop()
                    sys.exit()
                check_max_score()

        except Exception as e:
            print("Error occurred in handling connection :",e)
            accepting_connections()

def sendques(quesno):
    time.sleep(1)
    for conn in allcon:
        allcon[conn].send(str.encode(str(q[quesno])))

def sendbuzzerback(id):
    msg = "Player "+str(id)+" has pressed the buzzer"
    if id ==-1:
        msg = "No One has Pressed the buzzer. Next Question will be prompted now"
    print(msg)
    for conn in allcon:
        if str(conn) != str(id):
            allcon[conn].send(str.encode(msg))

def get_answer(id):
    allcon[(int)(id)].send("Your Answer:".encode("utf-8"))
    answer = allcon[(int)(id)].recv(1024)
    answer = answer.decode("utf-8")
    result = verify(answer)
    if result:
        sendanswerresult(id,True)
        scores[(int)(id)] = scores[(int)(id)] + 1
        print(scores)
    else:
        sendanswerresult(id,False)

def verify(answer):
    if str(answer) == str(a[quesno]):
        return True
    else:
        return False

def sendanswerresult(id,correct):
    msg = ''
    if correct:
        msg = "Player "+str(id)+"has given the right answer"
    else:
        msg = "Player "+str(id)+"has given the wrong answer" 
    for conn in allcon:
        if str(conn) != str(id):
            allcon[conn].send(msg.encode("utf-8"))
        elif correct:
            allcon[conn].send("Right Answer".encode("utf-8"))
        else:
            allcon[conn].send("Wrong Answer".encode("utf-8"))

def check_max_score():
    wd = max(scores,key = scores.get)
    if scores[wd] == 5:
        FinishLoop()
        sys.exit()
def FinishLoop():
    global scores
    wd = max(scores,key = scores.get)
    quit = "quit"
    for conn in allcon:
        allcon[conn].send(quit.encode("utf-8"))
    m = "Player "+str(wd)+" has won the game\n"+"Final Scores are:"
    for conn in allcon:
        if str(conn)  == str(wd):
            st = "Congratulations!!! You won! "
            allcon[conn].send(st.encode("utf-8"))
        else:
            allcon[conn].send(m.encode("utf-8"))
    for conn in allcon:
        print("sending to ",conn)
        for s in sorted(scores):
            time.sleep(1)
            st = "Player "+str(s)+":"+str(scores[s])
            allcon[conn].send(st.encode("utf-8"))
    for conn in allcon:
        allcon[conn].send("Quiz has ended".encode("utf-8"))
    time.sleep(5)

def create_workers():
    for i in range(NUMBER_OF_THREADS):
        t = threading.Thread(target = work)
        t.daemon = True
        t.start()

def work():
    while True:
        x = queue.get()
        if x == 1:
            create_socket()
            bind_socket()
            accepting_connections()
        queue.task_done()

def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)
    queue.join()
create_workers()
create_jobs()
