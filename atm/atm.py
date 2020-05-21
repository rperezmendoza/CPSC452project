#atm class
import sys
import os
import re
import datetime

from getpass import getpass
from Crypto.PublicKey import RSA
from socket import *

#This is a function to display the menu
def displayMenu(id):
	print("\n=========================================")
	print("==========WELCOME TO PYTHONBANK==========")
	print("=========================================")
	print("Account #: " + format(id) + " is currently login")
	print("Please make a selection from 1-5:")
	print(" 1) View Balance \t\t 2) Withdraw")
	print(" 3) Deposit \t\t\t 4) View Account History")
	print("\t\t 5) Log Off")
	print("=========================================\n")

#functions to send/receive messages through a socket
def receive_msgdec(s, size, decKey):
	result = ""
	tempBuff = ""
	while len(result) != size:
		tempBuff = s.recv(size)
		if not tempBuff:
			return -1
		result += tempBuff
	#uses the key to start the decryption
	result_dec = decKey.decrypt(result)
	return result_dec

def send_msgenc(s, msg, size, encKey):
	#encrypt the message before it is sent out
	enc_msg = encKey.encrypt(msg, 0L)[0]
	bytes_sent = 0
	while bytes_sent < size:
		bytes_sent += s.send(enc_msg[bytes_sent:])

MSG_SIZE = 256 #Setting the message size to 256
AUTHENTICATION_SUCCESS = '1'


atm_num = sys.argv[1]			#We will either atm1 or atm 2 (1/2)
serverPort = int(sys.argv[2])	#Can use any port. In the demo I'll be using 8080
serverName = sys.argv[3]		#local host

# load the atm 1 and 2 private key and bank server public key
if atm_num == '1' or atm_num == '2':
	f_handler = (open('atm_keys/atm{}_privkey.pem'.format(atm_num), 'r'),
					 open('atm_keys/server_pubkey.pem'.format(atm_num), 'r'))
	pubKey = RSA.importKey(f_handler[1].read())
	privKey = RSA.importKey(f_handler[0].read())
else:
	print("Error!!! the ATM # (" + format(atm_num) + ") is invalid")
	exit(-1)


#Connectos to the ATM server
cSocket = socket(AF_INET, SOCK_STREAM)
cSocket.connect((serverName, serverPort))

while 1:
	#User account information
	while 1:
		print("**************PYTHONBANK CORP***************")
		username = raw_input("Please enter your account number: ")
		result = re.match(r'^[0-9]{6}$', username)
		if result:
			break
		else:
			print("Please enter your account number: ")
			continue
		
	psswrd = getpass()
	credentials = (username, psswrd)
	c = ' '.join(credentials)
	print("Connecting...")

	#dtime needed for the login request as well as records
	dtime = datetime.datetime.now().strftime('%Y-%m-%d%H:%M:%S')
	#using public key to send encrypted credentials. 
	send_msgenc(cSocket, c + ' ' + dtime, MSG_SIZE, pubKey)

	psswrd = None		#setting password to no values
	credentials = None	#setting credentials to no values

	#get the server's response
	response = receive_msgdec(cSocket, MSG_SIZE, privKey)

	if response == AUTHENTICATION_SUCCESS:
		print "Connection Successful!"
		break
	else:
		print("Connection failed due to the following errors:")
		print(" *Account DNE\n *Wrong password\n *request timed out\n") #Note: DNE stands for Does Not Exist, meaning that the account is not in the records
		continue 

#Make selections from 1-5
while 1:
	displayMenu(username)
	choice = raw_input("Make a Selection from 1-5: ")
	amount = ''

#For choice 2 and 3, I tried making if statement to compare value greater than one
#but wasn't able to display the updated balance only using try/except exceptions
#===========================CHOICE 2 WITHDRAW===================================
	if choice == '2':
		while 1:
			amount = ' ' + raw_input("Please enter an amount to withdraw: $")
			try:
				float(amount)
			except:
				print ("Error amount entered!!!\n Must be $1 or more")
				continue
			break

#============================CHOICE 3 DEPOSIT===================================
	if choice == '3':
		while 1:
			amount = ' ' + raw_input("Please enter an amount to deposit: $")
			try:
				float(amount)
			except:
				print("Error amount entered!!!\n Must be $1 or more")
				continue
			break
		#encrypts user's choice before it gets sent to the server
	send_msgenc(cSocket, choice + amount, MSG_SIZE, pubKey)
	response = receive_msgdec(cSocket, MSG_SIZE, privKey)
	print("\n"+ response)

#=========================CHOICE 4==============================================
	if choice == '4':
		#Will get responses 
		while response != ' ':
			response = receive_msgdec(cSocket, MSG_SIZE, privKey)
			print response

#============================CHOICE 5===========================================
	if choice == '5':
		#Will log off user from the bank account
		cSocket.close()
		print("Logging off")
		exit(0)
