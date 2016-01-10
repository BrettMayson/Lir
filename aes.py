#!/usr/bin/env python3.4

import base64
from Crypto.Cipher import AES
from Crypto import Random

import random
import string

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) 
unpad = lambda s : s[:-ord(s[len(s)-1:])]

class Factory:
	def __init__( self, key ):
		self.key = key

	def encrypt( self, raw ):
		raw = pad(raw)
		iv = Random.new().read( AES.block_size )
		cipher = AES.new( self.key, AES.MODE_CBC, iv )
		return [base64.b64encode(cipher.encrypt( raw )) , base64.b64encode(iv)]

	def decrypt( self, enc, iv ):
		enc = base64.b64decode(enc)
		iv = base64.b64decode(iv)
		cipher = AES.new(self.key, AES.MODE_CBC, iv )
		return unpad(cipher.decrypt( enc )).decode("UTF-8")
		
def generateRandom(n):
	return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(n))
