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
#TODO create a connection class instead of import the pair script
import pair

#listeners are clients waiting to receive updates from the server
#{signal id,[clients ...]}
listeners = {}

def add_listener(sig,conn):
	if sig in listeners:
		listeners[sig].append(conn)
	else:
		listeners[sig] = [conn]
	
def action(mode,data,conn):
	reply = b''
	command = None
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
		add_listener(data,conn)
		command = None
	#the message is encrypted
	elif mode == "enc":
		iv = pair.readLine(conn)
		did = pair.readLine(conn)
		ddb = db.DeviceDB("devices.db")
		device = ddb.getDeviceByID(did)
		pair.key = device['key']
		msg = pair._decrypt(data,iv)
		try:
			mode,msg = msg.split(":",1)
		except:
			mode = "speech"
		action(mode,msg,conn)
	else:
		reply += b"UnknownMode;"
	
	if command != None:
		d = os.getcwd()
		os.chdir(fs.home()+"/.lir/bin")
		print("EXECUTING:",command)
		out = subprocess.getoutput("./"+command)+";"
		reply += out.encode('utf-8')
		os.chdir(d)
		
	return reply
	
def resp(conn):
	#infinite loop so that function do not terminate and thread do not end.
	onerun = False
	while onerun == False:
		#Receiving from client
		#TODO replace with buffer to receive large commands
		data = pair.readLine(conn)
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
		reply = b'OK;'
		try:
			mode,data = data.split(":",1)
		except:
			mode = "speech"
			
		reply += action(mode,data,conn)
			
		if not data: 
			break
	 
		try:
			conn.sendall(reply + b"\n")
		except:
			#client disconnected immediatly after submitting command
			pass

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
