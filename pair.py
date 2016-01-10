#!/usr/bin/env python3.4

import socket,sys,platform,os

import db
import aes

TEST_PHRASE = {1 : "lir is the best"}

def _decrypt(data,iv):
    f = aes.Factory(key)
    return f.decrypt(data,iv)

def pair(conn):
    ddb = db.DeviceDB("devices.db")
    #Receive pairing process version number
    version = int(readPlain(conn,1))
    print("Version:",version)
    if version == 1:
        #Will pair will be encrypted
        #1 - yes
        #0 - no
        enc = readPlain(conn,1)
        print("Encrypted:",enc == "1")
        if enc == "1":
            read = readEnc
            send = sendEnc
        elif enc == "0":
            read = readPlain
            send = sendPlain
        else:
            print("1: Unexpected Value:",enc)
        if read(conn) == TEST_PHRASE[1]:
            print("Receive Good")
        send(conn,TEST_PHRASE[1])
        #send hostname
        send(conn,socket.gethostname())
        #send os
        send(conn,' '.join(platform.linux_distribution()[0:2]))
        #receive hostname
        host = read(conn)
        print("HOST:",host)
        #receive os
        _os = read(conn)
        print("OS:",_os)
        #receive uid
        _uid = read(conn)
        _id = ddb.addDevice({"name" : host, "key" : key, "os" : _os, "uid" : _uid})
        print("Row ID",_id)
        ddb.close()
    
def sendEnc(conn,text):
    f = aes.Factory(key)
    enc,iv = f.encrypt(text)
    conn.sendall(iv + b'\n')
    conn.sendall(enc + b'\n')
    
def sendPlain(conn,text):
    conn.sendall(text.encode("UTF-8") + b'\n')
    
def readEnc(conn):
    iv = readLine(conn)
    print("IV:",iv)
    enc = readLine(conn)
    print("ENC:",enc)
    return _decrypt(enc,iv)

def readPlain(conn,n = None):
    data = ""
    if n != None:
        while len(data) < n:
            c = conn.recv(1)
            if c != b'\r' and c != b'\n' and c != b'' and c != None:
                data += c.decode("UTF-8")
    else:
        data = readLine(conn)
    return data

def readLine(conn):
    data = ""
    while True:
        c = conn.recv(1)
        if c != b'\r' and c != b'\n' and c != b'' and c != None:
            data += c.decode("UTF-8")
        else:
            break
    return data

key = None

def main():
    PORT = 9040

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("Created Socket")
    
    try:
        s.bind(('',PORT))
    except socket.error as e:
        print ("Bind Failed.",e)
        return False
        
    print ("Bind Complete.")
    
    s.listen(10)
    print ("Socket Listening on port " + str(PORT))
    
    global key
    key = aes.generateRandom(16)
    #key = "aaaaaaaaaaaaaaaa"
    os.system("qrencode -s 15 -o pair.png \""+key+"\"")
    os.system("xdg-open pair.png")
    print ("Key: ",key)
    
    con,addr = s.accept()
    print('Connected with ' + addr[0] + ':' + str(addr[1]))
    pair(con)
    sys.exit(0)
    
if __name__ == "__main__":
    main()
