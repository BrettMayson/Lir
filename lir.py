#!/usr/bin/env python3.4

class Language():
    def __init__(self,lang = 'en'):
        self.data = Settings.ini("langs/"+lang)
        
    def get(section,key):
        return self.data.get(secion,key)

class OutputWriter:
    DEFAULT = '\033[0m'     #END COLOR
    HEADER = '\033[95m'     #Purple
    DEBUG = '\033[94m'      #Blue
    OK = '\033[92m'         #Green
    WARNING = '\033[93m'    #Orange
    FAIL = '\033[91m'       #Red
    ENDC = '\033[0m'        #END COLOR
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    def __init__(self,name,enc = False,standard = DEFAULT):
        self.name = name
        self.enc = enc
        self.standard = standard
        
    def info(self,*text):
        self.write(OutputWriter.ENDC + self._name()+" " + ' '.join(map(str,text)))
        
    def debug(self,*text):
        self.write(self._name()+" "+OutputWriter.DEBUG + ' '.join(map(str,text)) + OutputWriter.ENDC)
        
    def header(self,*text):
        self.write(self._name()+" "+OutputWriter.HEADER + ' '.join(map(str,text)) + OutputWriter.ENDC)
        
    def warning(self, *text):
        self.write(self._name()+" "+OutputWriter.WARNING + ' '.join(map(str,text)) + OutputWriter.ENDC)
        
    def fail(self, *text):
        self.write(self._name()+" "+OutputWriter.FAIL + ' '.join(map(str,text)) + OutputWriter.ENDC)
        
    def success(self, *text):
        self.write(self._name()+" "+OutputWriter.OK + ' '.join(map(str,text)) + OutputWriter.ENDC)
        
    def write(self,text):
        #with open("/tmp/lir-"+self.name+".log",'a') as f:
        #    f.write(text+"\n")
        print(text)
    
    def _name(self):
        text = ""
        text += self.standard
        text += "["+self.name+"]"
        text += OutputWriter.ENDC
        return text
        
    def helper(self):
        self.info("[Standard Connection]")
        self.header("[Encrypted Connection]")
        self.info("Info")
        self.debug("Debug")
        self.warning("Warning")
        self.fail("Fail")
        self.success("Success")

class DataStorage():
    class Devices():
        def __init__(self,path):
            import sqlite3
            self.con = sqlite3.connect(path)
            self.con.row_factory = sqlite3.Row
            self.cur = self.con.cursor()
            self._createDB()
            
        def _reset(self):
            self.cur.execute("DROP TABLE IF EXISTS devices")
            self._createDB()
            
        def _createDB(self):
            #Create table if one doesn't exist
            self.cur.execute("CREATE TABLE IF NOT EXISTS devices (_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, key TEXT, os TEXT, uid TEXT)")
            
        def addDevice(self,data):
            self.cur.execute("INSERT INTO devices(name, key, os, uid) VALUES (?, ?, ?, ?)",(data['name'],data['key'],data['os'], data['uid']))
            self.con.commit()
            return self.cur.lastrowid
            
        def getDeviceByID(self,_id):
            self.cur.execute("SELECT * FROM devices WHERE uid = ?",(_id,))
            return self.cur.fetchone()
            
        def close(self):
            if self.con:
                self.con.close()

class Communication():
    class Device():
        def __init__(self,out,conn,key = None,encrypted = False):
            self.conn = conn
            self.enc = encrypted
            self.key = key
            
            self.peername = conn.getpeername()
            self.out = out
            
            self.factory = Communication.AES.Factory(self.key)
            
            if encrypted:
                self.send = self.sendEnc
                self.read = self.readEnc
            else:
                self.send = self.sendPlain
                self.read = self.readPlain
            
        def sendEnc(self,text):
            #print("LEN",len(text))
            #if len(text) < 1024 * 4:
            enc,iv = self.factory.encrypt(text)
            self.conn.sendall(iv + b'\n')
            self.conn.sendall(enc + b'\n')
            #else:
            #    enc,iv = self.factory.encrypt(text)
            #    enc2,iv2 = self.factory.encrypt("|long|"+str(len(enc))+"|/long|")
            #    self.conn.sendall(iv2 + b'\n')
            #    self.conn.sendall(enc2 + b'\n')
            
        def sendPlain(self,text):
            Communication._sendPlain(self.conn,text)
            
        def readEnc(self):
            iv = self.readLine()
            enc = self.readLine()
            return self.factory.decrypt(enc,iv)

        def readPlain(self,n = None):
            return Communication._readPlain(self.conn,n)

        def readLine(self):
            return Communication._readLine(self.conn)
            
        def decrypt(self,enc,iv):
            return self.factory.decrypt(enc,iv)
            
        def close(self):
            self.conn.close()
        
    def _readLine(conn):
        data = ""
        while True:
            c = conn.recv(1)
            if c != b'\r' and c != b'\n' and c != b'' and c != None:
                data += c.decode("UTF-8")
            else:
                break
        return data

    def _readPlain(conn,n=None):
        data = ""
        if n != None:
            while len(data) < n:
                c = conn.recv(1)
                if c != b'\r' and c != b'\n' and c != b'' and c != None:
                    data += c.decode("UTF-8")
        else:
            data = Communication._readLine(conn)
        return data

    def _sendPlain(conn,text):
        conn.sendall(text.encode("UTF-8") + b'\n')


    class AES():
        class Factory():
            
            BS = 16
            
            def __init__( self, key ):
                self.key = key
            
            def pad(self,s):
                return s + (self.BS - len(s) % self.BS) * chr(self.BS - len(s) % self.BS)     

            def unpad(self,s):
                return s[:-ord(s[len(s)-1:])]

            def encrypt( self, raw ):
                import base64
                from Crypto.Cipher import AES
                from Crypto import Random
                raw = self.pad(raw)
                iv = Random.new().read( AES.block_size )
                cipher = AES.new( self.key, AES.MODE_CBC, iv )
                return [base64.b64encode(cipher.encrypt( raw )) , base64.b64encode(iv)]

            def decrypt( self, enc, iv ):
                import base64
                from Crypto.Cipher import AES
                enc = base64.b64decode(enc)
                iv = base64.b64decode(iv)
                cipher = AES.new(self.key, AES.MODE_CBC, iv )
                return self.unpad(cipher.decrypt( enc )).decode("UTF-8")
                
        def generateRandom(n):
            import random
            import string
            return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(n))


class Settings():
    class ini():
        def __init__(self,name):
            try:
                from configparser import ConfigParser
            except ImportError:
                from ConfigParser import ConfigParser  # ver. < 3.0
            import os
            
            # instantiate config
            self.config = ConfigParser()
            #file name
            self.name = name if name.endswith(".ini") else name+".ini"
            self.name = FileSystem.expand_path(self.name)

            # parse existing file
            if os.path.exists(self.name):
                self.config.read(self.name)

        def get(self,section,key):
            #get a value from the config
            return self.config.get(section,key)
            
        def set(self,section,key,value):
            #set a value in the config
            return self.config.set(section, key, value)

        def create_section(self,name):
            #create a new section in the config
            if not self.has_section(name):
                self.config.add_section(name)

        def has_section(self,name):
            #check for a section in the config
            return self.config.has_section(name)

        def save(self):
            #try:
                BACKUP = "/tmp/new_settings.ini"
                #save to an alternate file to assure no data loss
                with open(BACKUP, "w") as configfile:
                    self.config.write(configfile)
                FileSystem.delete(self.name)
                FileSystem.move(BACKUP,self.name)
                return True
            #except:
            #    FileSystem.delete(BACKUP)
            #    return False

class FileSystem():
    DEBUG = False

    def debug(*text):
        if FileSystem.DEBUG:
            print("[DEBUG]",text)
            
    def system(cmd):
        import os
        import subprocess
        with open(os.devnull, 'wb') as devnull:
            subprocess.check_call(cmd, stdout=devnull, stderr=subprocess.STDOUT)

    def expand_path(path):
        import os
        #expand home directory
        path = os.path.expanduser(path)
        if not path.startswith("/"):
            path = os.getcwd() + "/" + path
        #resolve relative paths
        path = os.path.realpath(path)
        return path

    def move(src,dst):
        import shutil
        src = FileSystem.expand_path(src)
        dst = FileSystem.expand_path(dst)
        shutil.move(src,dst)
        return True

    def copy(src,dst):
        import os
        import shutil
        src = FileSystem.expand_path(src)
        dst = FileSystem.expand_path(dst)
        try:
            os.makedirs(dst)
        except:
            pass
        if os.path.isdir(src):
            files = [f for f in os.listdir(src) if os.path.isfile(os.path.join(src, f))]
            dirs =  [f for f in os.listdir(src) if os.path.isdir(os.path.join(src, f))]
            
            for f in files:
                if not f.endswith("~"):
                    shutil.copy(os.path.join(src,f),os.path.join(dst,f))
                
            for d in dirs:
                if copy(os.path.join(src,f),os.path.join(dst,f)) == False:
                    return False
            return True
        elif os.path.isfile(src):
            shutil.copy(src,dst)
            return True
        else:
            return False

    def delete(path):
        import os
        import shutil
        path = FileSystem.expand_path(path)
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
                return True
            elif os.path.isfile(path):
                os.remove(path)
                return True
            else:
                return False
        else:
            return False
            
    def create(path):
        import os
        path = FileSystem.expand_path(path)
        if not os.path.exists(path):
            open(path, 'a').close()
            
    def create_directory(directory):
        import os
        directory = FileSystem.expand_path(directory)
        if not os.path.exists(directory):
            os.makedirs(directory)

    def home():
        return FileSystem.expand_path("~")
        
    LIR_SETTINGS = expand_path("~/.lir/main.ini")

class PluginManager():
    def inject_dictionary(path,name):
        info = Settings.ini(FileSystem.expand_path("~/.lir/main.ini"))
        path = FileSystem.expand_path(path)
        mode = path.split("/")[-1]
        FileSystem.create("~/.lir/actions/"+mode+".dic")
        with open(FileSystem.expand_path("~/.lir/actions/"+mode+".dic"),'a') as f:
            f.write("\n####\n#  "+name+"\n####\n")
            with open(path+"/"+info.get("general","language")+".dic") as src:
                f.write(src.read())

    def installCompressed(path):
        import os
        import tarfile
        #resolve path and open tar
        path = FileSystem.expand_path(path)
        name = path.split("/")[-1]
        tar = tarfile.open(path,'r:gz')
        FileSystem.create_directory("/tmp/lir")
        #extract into /tmp
        tar.extractall("/tmp/lir/")
        #load info
        info = Settings.ini("/tmp/lir/info.ini")
        #move files to "install" plugin
        FileSystem.copy("/tmp/lir/info.ini","~/.lir/plugins/"+info.get("info","name").replace(" ","_").lower()+".ini")
        for s in ["tts","sst","services","bin","signals"]:
            if info.has_section(s):
                if not FileSystem.copy("/tmp/lir/"+s,"~/.lir/"+s+"/"+name):
                    return False
        for dic in os.listdir("/tmp/lir/actions"):
            if os.path.isdir("/tmp/lir/actions/"+dic):
                PluginManager.inject_dictionary("/tmp/lir/actions/"+dic,info.get("info","name"))
        FileSystem.delete("/tmp/lir")
        return True
        
    def installFolder(path):
        import os
        import tarfile
        path = FileSystem.expand_path(path)
        name = path.split("/")[-1]
        info = Settings.ini(path+"/info.ini")
        #move files to "install" plugin
        FileSystem.copy(path+"/info.ini","~/.lir/plugins/"+info.get("info","name").replace(" ","_").lower()+".ini")
        for s in ["tts","sst","services","bin","signals"]:
            #if info.has_section(s):
            if os.path.exists(path+"/"+s):
                if not FileSystem.copy(path+"/"+s,"~/.lir/"+s+"/"+name):
                    return False
        if os.path.isdir(path+"/actions"):
            for dic in os.listdir(path+"/actions"):
                if os.path.isdir(path+"/actions/"+dic):
                    PluginManager.inject_dictionary(path+"/actions/"+dic,info.get("info","name"))
        return True
