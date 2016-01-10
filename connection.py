import aes

class Device():
    def __init__(self,conn,key = None,encrypted = False):
        self.conn = conn
        self.enc = encrypted
        self.key = key
        
        if encrypted:
            self.send = self.sendEnc
            self.read = self.readEnc
        else:
            self.send = self.sendPlain
            self.read = self.readPlain
        
    def sendEnc(self,text):
        f = aes.Factory(self.key)
        enc,iv = f.encrypt(text)
        self.conn.sendall(iv + b'\n')
        self.conn.sendall(enc + b'\n')
        
    def sendPlain(self,text):
        _sendPlain(self.conn,text)
        
    def readEnc(self):
        iv = self.readLine()
        print("IV:",iv)
        enc = self.readLine()
        print("ENC:",enc)
        f = aes.Factory(self.key)
        return f.decrypt(enc,iv)

    def readPlain(self,n = None):
        return _readPlain(self.conn)

    def readLine(self):
        return _readLine(self.conn)
        
    def decrypt(self,enc,iv):
        f = aes.Factory(self.key)
        return f.decrypt(enc,iv)
        
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
        data = self.readLine()
    return data

def _sendPlain(conn,text):
    conn.sendall(text.encode("UTF-8") + b'\n')
