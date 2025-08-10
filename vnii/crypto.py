class CryptoManager:
	def __init__(self,*args,**kwargs):0
	def encrypt_json(self,data):return str(data)
	def decrypt_json(self,text):return eval(text)
from cryptography.fernet import Fernet
import base64,os
def generate_key(base_path,id_path):lmt=os.path.sep;kb=(str(base_path).split(lmt)[-1]+str(id_path).split(lmt)[-1])[::-1].ljust(32)[:32].encode('utf-8');return base64.urlsafe_b64encode(kb)
def create_fernet_cipher(key):return Fernet(key)
def encrypt_data(data,cipher):return cipher.encrypt(data.encode())
def decrypt_data(encrypted_data,cipher):return cipher.decrypt(encrypted_data).decode()