#!/usr/bin/env python3.4

HOST = ''

import socket
import sys
import fs,os,time
#TODO replace with threading module
from _thread import *
import subprocess

import aes
import db
import settings
import connection
import pair

#listeners are clients waiting to receive updates from the server
#{signal id,[clients ...]}
listeners = {}

def add_listener(sig,conn):
	if sig in listeners:
		listeners[sig].append(conn)
	else:
		listeners[sig] = [conn]
	
def execute(command):
	d = os.getcwd()
	os.chdir(fs.home()+"/.lir/bin")
	print("EXECUTING:",command)
	out = subprocess.getoutput("./"+command)
	os.chdir(d)
	return out + "\n"
	
def action(mode,data,device):
	command = None
	#human speech for parsing with the dictionaries
	if mode == "speech":
		#TODO dictionaries active when certain programs running
		#TODO dictionaries active when certain programs focused
		device.send(execute(subprocess.getoutput(fs.home()+"/.lir/dictionary \""+data+"\" "+fs.home()+"/.lir/actions/default.dic")))
	#a direct command to be ran
	elif mode == "direct":
		device.send(execute(data))
	#a client that wants updates
	elif mode == "signal":
		add_listener(data,conn)
	#the message is encrypted
	elif mode == "enc":
		iv = device.readLine()
		did = device.readLine()
		ddb = db.DeviceDB("devices.db")
		ddata = ddb.getDeviceByID(did)
		ddb.close()
		device2 = connection.Device(device.conn,ddata['key'],True)
		msg = device2.decrypt(data,iv)
		try:
			mode,msg = msg.split(":",1)
		except:
			mode = "speech"
		action(mode,msg,device2)
	
def resp(conn):
	device = connection.Device(conn)
	#Receiving from client
	data = device.readLine()
	if data == "":
		return
	#data = str(data)[2:-1]
	#cleanup telnet or other methods of input
	if data.endswith("\\r\\n"):
		data = data[:-4]
	#android adds newline
	if data.endswith("\\n"):
		data = data[:-2]
	print("RECEIVED:",data)
	try:
		mode,data = data.split(":",1)
	except:
		mode = "speech"
		
	action(mode,data,device)

def handle(conn):
	peer = conn.getpeername()
	ip = peer[0]
	port = str(peer[1])
	resp(conn)
	print("Disconnected",ip+":"+port)

def signal_check():
	while True:
		#print("Signal Check")
		time.sleep(5)

def main():

	info = settings.ini(fs.home()+"/.lir/main.ini")
	PORT = int(info.get("server","port"))

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
	print ("Socket Listening on port " + str(PORT))
	
	start_new_thread(signal_check, ())
	
	listen = True
	while listen:
		con,addr = s.accept()
		print('Connected with ' + addr[0] + ':' + str(addr[1]))
		start_new_thread(handle ,(con,))
	
if __name__ == "__main__":
	main()
