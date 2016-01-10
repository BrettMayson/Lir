#!/usr/bin/env python3.4

import socket,sys,platform,os

import db
import aes
import connection

TEST_PHRASE = {1 : "lir is the best"}

def pair(conn):
    ddb = db.DeviceDB("devices.db")
    #Receive pairing process version number
    version = int(device.readPlain(conn,1))
    print("Version:",version)
    if version == 1:
        #Will pair will be encrypted
        #1 - yes
        #0 - no
        enc = readPlain(conn,1)
        print("Encrypted:",enc == "1")
        device = connection.Device(conn,key,enc == "1")
        if device.read() == TEST_PHRASE[1]:
            print("Receive Good")
        device.send(TEST_PHRASE[1])
        #send hostname
        device.send(socket.gethostname())
        #send os
        device.send(' '.join(platform.linux_distribution()[0:2]))
        #receive hostname
        host = device.read()
        print("HOST:",host)
        #receive os
        _os = device.read()
        print("OS:",_os)
        #receive uid
        _uid = device.read()
        _id = ddb.addDevice({"name" : host, "key" : key, "os" : _os, "uid" : _uid})
        print("Row ID",_id)
        ddb.close()
    
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
