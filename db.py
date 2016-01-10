#!/usr/bin/env python3.4

import sqlite3

class DeviceDB():
    def __init__(self,path):
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
        self.cur.execute("SELECT * FROM devices WHERE id = ?",_id)
        return self.cur.fetchone()
        
    def getDeviceByAddress(self,_ip):
        self.cur.execute("SELECT * FROM devices WHERE ip = ?",_ip)
        return self.cur.fetchone()
        
    def close(self):
        if self.con:
            self.con.close()

def main():
    return 0
    
if __name__ == "__main__":
    main()
