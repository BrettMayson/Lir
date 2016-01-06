#!/usr/bin/env python3.4

HOST = ''

import socket
import sys
import fs,os,time
#TODO replace with threading module
from _thread import *
import subprocess

import rsa
import settings

#listeners are clients waiting to receive updates from the server
#{signal id,[clients ...]}
listeners = {}
key = None

def add_listener(sig,conn):
    if sig in listeners:
        listeners[sig].append(conn)
    else:
        listeners[sig] = [conn]


#Pair Codes
#2 - send public
#3 - receive public
#4 - receive name
#5 - receive os
#6 - repeat encrypted (palin text will be sent to the device and needs to send back encrypted text)
#7 - repeat plain (encrypted text will be sent to the device and needs to send back plain text)
#100 - Pair Complete
#900 - Receive Public Failed
#901 - Stage 1 Failed
#902 - Stage 2 Failed
def pair(data,conn):
    try:
        device,version = data.split("-",1)
    except:
        conn.sendall("Invalid Start Request;")
    if version.split('.')[0] == 1:
        #ask for public key
        conn.sendall("2\n")
        public = conn.recv(1024)
        print(public)
        pair_send_stage(conn,3,key.getPublic())
        pair_send_stage(conn,4,socket.gethostname())
        import platform
        pair_send_stage(conn,5,' '.join(platform.linux_distribution[0:1]))
        conn.sendall("6\n")
        wait = True
        while wait:
            r = conn.recv(128)
            print("PAIR CODE",stage,"RESP:",r)
            if r == "OK":
                wait = False
            time.sleep(0.05)
        conn.sendall("ABCabc123\n")
        data = rconn.recv(1024)
        print(data)
        if key.decrypt(data) == "ABCabc123":
            print("stage 1 good")
        else:
            conn.sendall("901\n")
            return 901
        conn.sendall("7\n")
        wait = True
        while wait:
            r = conn.recv(128)
            print("PAIR CODE",stage,"RESP:",r)
            if r == "OK":
                wait = False
            time.sleep(0.05)
        conn.sendall(key.encrypt("123abcABC",public)+"\n")
        data = rconn.recv(1024)
        if data == "123abcABC":
            print("stage 2 good")
        else:
            conn.sendall("902\n")
            return 902
        conn.sendall("100\n")
        return 100
    else:
        print("Invalid Version:",version)
    
def pair_send_stage(conn,stage,data):
    conn.sendall(str(stage)+"\n")
    #wait for ready from client
    wait = True
    while wait:
        r = conn.recv(128)
        print("PAIR CODE",stage,"RESP:",r)
        if r == "OK":
            wait = False
        time.sleep(0.05)
    conn.sendall(data+"\n")
    wait = True
    while wait:
        r = conn.recv(128)
        print("PAIR CODE",stage,"RESP:",r)
        if r == "OK":
            wait = False
        time.sleep(0.05)
    
def resp(conn):
    conn.send(b'Lir Server Connection\nSend a command!\n')
     
    #infinite loop so that function do not terminate and thread do not end.
    while True:
        #Receiving from client
        #TODO replace with buffer to receive large commands
        data = conn.recv(1024)
        data = str(data)[2:-1]
        #cleanup telnet or other methods of input
        if data.endswith("\\r\\n"):
            data = data[:-4]
        #android adds newline
        if data.endswith("\\n"):
            data = data[:-2]
        print("RECEIVED:",data)
        reply = b'OK;'
        try:
            mode,data = data.split(":",1)
        except:
            mode = "speech"
            
            
        close_conn = True
            
        #human speech for parsing with the dictionaries
        if mode == "speech":
            #TODO dictionaries active when certain programs running
            #TODO dictionaries active when certain programs focused
            command = subprocess.getoutput(fs.home()+"/.lir/dictionary \""+data+"\" "+fs.home()+"/.lir/actions/default.dic")
        #a direct command to be ran
        elif mode == "direct":
            command = data
        #a client that wants updates
        elif mode == "signal":
            close_conn = False
            add_listener(data,conn)
        elif mode == "pair_start":
            pair(data,conn)
        else:
            reply += b"UnknownMode;"
        
        d = os.getcwd()
        os.chdir(fs.home()+"/.lir/bin")
        print("EXECUTING:",command)
        #TODO add some checks and support for multiple dictionaries
        out = subprocess.getoutput("./"+command)+";"
        reply += out.encode('utf-8')
        os.chdir(d)
        
        if not data: 
            break
     
        try:
            conn.sendall(reply + b"\n")
        except:
            #client disconnected immediatly after submitting command
            pass
     
    #came out of loop
    if close_conn:
        conn.close()

def signal_check():
    while True:
        #print("Signal Check")
        time.sleep(5)

def main():

    info = settings.ini(fs.home()+"/.lir/main.ini")
    PORT = int(info.get("server","port"))
    
    key = rsa.Key()
    if os.path.exists(fs.home()+"/.lir/keys.pem"):
        key.load(fs.home()+"/.lir/keys.pem")
    else:
        key.generate(1024)
        key.save(fs.home()+"/.lir/keys.pem")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("Created Socket")
    
    try:
        s.bind((HOST,PORT))
    except socket.error as e:
        print ("Bind Failed.",e)
        return False
        
    print ("Bind Complete.")
    
    print ("Starting Signal Check")
    
    s.listen(10)
    print ("Socket Listening")
    
    start_new_thread(signal_check, ())
    
    listen = True
    while listen:
        con,addr = s.accept()
        print('Connected with ' + addr[0] + ':' + str(addr[1]))
        start_new_thread(resp ,(con,))
    
if __name__ == "__main__":
    main()
