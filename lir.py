#!/usr/bin/env python3.4

import argparse
import socket
import settings
import fs

parser = argparse.ArgumentParser(description='Send commands to the Lir backend')
parser.add_argument('--host', type=str, help='Address of host computer (default to main.ini value)')
parser.add_argument('--port', type=str, help='Port of host computer (default to main.ini value)')
parser.add_argument('--speak', dest="text", type=str, help='Title of notification')
parser.add_argument('--notify-title', dest="title", type=str, help='Title of notification', required=False)
parser.add_argument('--notify-body', dest="body", type=str, help='Body of notification', required=False)
parser.add_argument('--notify-icon', dest="icon", type=str, help='Path to icon for noticiation',required=False)
args = parser.parse_args()

info = settings.ini("~/.lir/main.ini")

if args.host != None:
    HOST = args.host
else:
    HOST = info.get("server","host")
if args.port != None:
    PORT = int(args.port)
else:
    PORT = int(info.get("server","port"))

def display_notification(title,body=None,icon=None,speech=None):
    cmd = "notify \""+title+"\""
    if body != None:
        cmd += " -b \""+body+"\""
    if icon != None:
        cmd += " -i \""+icon+"\""
    resp = send_command(cmd)
    if info.get("tts","read-responses") == "True":
        if type(speech) == str:
            speak(speech)
        else:
            speak(title)
        return resp
    
def speak(text,engine=None):
    cmd = "say \""+text+"\""
    if engine:
        cmd += " --tts \""+engine+"\""
    resp = send_command(cmd)
    return resp
    
def send_speech(cmd):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.send(b"speech:"+cmd.encode('utf-8')+b"\r\n")
    resp = s.recv(1024)
    s.close()
    
def send_command(cmd):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.send(b"direct:"+cmd.encode('utf-8')+b"\r\n")
    resp = s.recv(1024)
    s.close()
    
def main():

    print(args)

    if args.text != None:
        print(speak(args.text))
    if args.title != None:
        #cmd = b"direct:notify \""+args.title.encode('utf-8')+b"\""
        #if args.body:
        #    cmd += b" -b \""+args.body.encode('utf-8')+b"\""
        #if args.icon:
        #    cmd += b" -i \""+args.icon.encode('utf-8')+b"\""
        #s.send(cmd+b"\r\n")
        #print(s.recv(1024))
        print(display_notification(args.title,args.body,args.icon))

if __name__ == "__main__":
    main()
