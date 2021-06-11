import hashlib
from Crypto.Random import get_random_bytes
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django import urls
import pymongo
import random
import string
from Crypto.Cipher import AES
import datetime
from base64 import b64encode,b64decode

# Create your views here.
db_client = pymongo.MongoClient(
    'mongodb+srv://markis:cmritproject123@cluster0.313vp.mongodb.net/priv?authSource=admin&replicaSet=atlas-fkelf3-shard-0&readPreference=primary&appname=MongoDB%20Compass%20Community&ssl=true')
# Selecting database
db = db_client['privmsg']
col = db["msg"]

# Function to encrypt plaintext
def encrypt(plain_text, password):
    # generate a random salt
    salt = get_random_bytes(AES.block_size)

    # use the Scrypt KDF to get a private key from the password
    private_key = hashlib.scrypt(
        password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)

    # create cipher config
    cipher_config = AES.new(private_key, AES.MODE_GCM)

    # return a dictionary with the encrypted text
    cipher_text, tag = cipher_config.encrypt_and_digest(bytes(plain_text, 'utf-8'))
    return {
        'cipher_text': b64encode(cipher_text).decode('utf-8'),
        'salt': b64encode(salt).decode('utf-8'),
        'nonce': b64encode(cipher_config.nonce).decode('utf-8'),
        'tag': b64encode(tag).decode('utf-8')
    }

# Function to decrypt from dictionary
def decrypt(enc_dict, password):
	# decode the dictionary entries from base64
	salt = b64decode(enc_dict['salt'])
	cipher_text = b64decode(enc_dict['cipher_text'])
	nonce = b64decode(enc_dict['nonce'])
	tag = b64decode(enc_dict['tag'])
	

	# generate the private key from the password and salt
	private_key = hashlib.scrypt(
		password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)

	# create the cipher config
	cipher = AES.new(private_key, AES.MODE_GCM, nonce=nonce)

	# decrypt the cipher text
	decrypted = cipher.decrypt_and_verify(cipher_text, tag)

	return decrypted


# Function to generate a random link string
def gen_link(length=random.randint(7, 10)):
    # List of strings that can be used for a password
    text = f"{string.ascii_letters}{string.digits}"
    text = list(text)
    # Shuffling the text
    random.shuffle(text)
    # Returning a randomly chosen password
    link =  ''.join(random.choices(text, k=length))
    # Checking if room name exists
    db_unique = db['data'].find_one({'link':link}, {'_id':0, 'created_at':0})
    # Exists, so making a recursive call
    if db_unique:
        gen_link()
    else:
        return link

# Function to create burn messages
def create_msg(request, msg):
	# Generate link for message
	link = gen_link()
	# Generate password for message
	msg_pass = gen_link()
	enc_msg = encrypt(msg, msg_pass)
	data = {}
	for key in enc_msg:
		data[key] = enc_msg[key]
	data['link'] = link 
	data['created_time'] = datetime.datetime.utcnow()
	# Insert data to mongo
	col.insert(data)
	# Append password to link string
	link +=';'+msg_pass
	return redirect(reverse('msg:read', kwargs={"link": link}))


# Function to read a given message
def read(request, link):
	if len(link.split(';')) <= 1:
		link = link.split(';')[0]
		passwd = link.split(';')[1]
	else:
		return HttpResponse('error')
	# Query to check if link exists
	link = col.find_one({'link': link}, {'_id':0, 'created_at':0})
	# If link does not exist
	if link is None:
		return HttpResponse('Msg does not exist!')
	# If link exists
	else:
		# Try to decrypt file with the given password in URL
		try:
			msg = decrypt(link, passwd)
			return render(request, 'msg/index.html', {'msg': msg})
		except:
			return HttpResponse('error')
			