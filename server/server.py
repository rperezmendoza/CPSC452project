#Bank server class
import sys
import os
import threading
import datetime

from Crypto.PublicKey import RSA
from passlib.hash import argon2
from socket import *
from Crypto.Cipher import AES
from subprocess import call

#record customer transaction
def transHist(id, request, val=None):
    h = open('bank_statement/{}.txt'.format(id), 'a')
    dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if request == 'login':
        if val == 1:
			h.write("{}: Successful access!!! {}\n".format(dtime, id))
        else:
			h.write("{}: xxxFAILED accessxxx {}\n".format(dtime, id))
            
	#Will get the customer's balance from option 1
    elif request == 'view_balance':
        h.write ("{}: Balance accessed for account {}\n".format(dtime, id))
    elif request == 'logoff':
        h.write("{}: User {} logged off.\n".format(dtime, id))
		#Amount of money withdrawn 
    elif request == 'withdraw':
        if val[0] == True:
            h.write("{}: User {} withdrew ${:.2f}.\n".format(dtime, id, val[1]))
        else:
            h.write("{}: User {} failed to withdraw ${:.2f}\n".format(dtime, id, val[1]))
    elif request == 'deposit':
        #Amount of money deposited 
        h.write("{}: User {} deposited ${:.2f}.\n".format(dtime, id, val))
    elif request == 'shutdown':
        h.write("{}: User {} logged off from ATM.\n".format(dtime, id))
    h.close()

#loadAccount function
#Note: This will be used to load both ATMs and provide the same connection at the same
#Time. Also this connection might not be secured in real world, but it works for 
#This project. 
def loadAccounts():
	print("\n\n**********DECRYPTION PROCESS**********")
	print("\nPlease enter the password created from ATM1")
	ssl1 = 'openssl aes-256-cbc -d -in afilesdec.txt.enc -out afilesdec.txt'.split()
	call(ssl1)
	print("\nPlease enter the password created from ATM2")
	ssl2 = 'openssl aes-256-cbc -d -in a_bal.txt.enc -out a_bal.txt'.split()
	call(ssl2)
	print("\n**************************************")

	accounts = []
	with open('afilesdec.txt', 'r') as h:
		for i in h:
			i_t = i.rstrip()
			i_t_s = i_t.split()
			account = (i_t_s[0], i_t_s[1])
			accounts.append(account)

	a_balance = []
	with open('a_bal.txt', 'r') as h:
		for i in h:
			i_t = i.rstrip()
			i_t_s = i_t.split()
			balance = (i_t_s[0], float(i_t_s[1]))
			a_balance.append(balance)

	return accounts, a_balance


#Function to update the user's account and writes it into the a_bal.txt file
def updateAccount(balances):
	with open('a_bal.txt', 'w') as h:
		for balance in balances:
			h.write(balance[0] + ' {:.2f}\n'.format(balance[1]))
	ssl1 = 'openssl aes-128-cbc -e -in a_bal.txt -out a_bal.txt.enc'.split()
	call(ssl1)

MSG_SIZE = 256
AUTHENTICATION_SUCCESS = '1'

#functions to send/receive messages through a socket
def receive_msgdec(s, size, decKey):
	result = ""
	tempBuff = ""
	while len(result) != size:
		tempBuff = s.recv(size)
		if not tempBuff:
			return -1
		result += tempBuff
	result_dec = decKey.decrypt(result)
	return result_dec

def send_msgenc(s, msg, size, encKey):
	#encrypt the message before it is sent out
	enc_msg = encKey.encrypt(msg, 0L)[0]
	bytes_sent = 0
	while bytes_sent < size:
		bytes_sent += s.send(enc_msg[bytes_sent:])

def serv_connect(s, atm_num):
	connectionSocket, addr = s.accept()
	print("Connection " + format(atm_num) + " recognized.\n")

	#update the keys generated into files atm1_pubkey, atm2_pubkey, and server_privkey files
	f_handler = (open('server_keys/atm{}_pubkey.pem'.format(atm_num), 'r'),
					 open('server_keys/server_privkey.pem'.format(atm_num), 'r'))
	pubKey = RSA.importKey(f_handler[0].read())
	privKey = RSA.importKey(f_handler[1].read())
	for h in f_handler:
		h.close()

	while 1:
		while 1:
			# receive credentials from the atm
			dec_c = receive_msgdec(connectionSocket, MSG_SIZE, privKey)
			dec_c = dec_c.split()
			c = (dec_c[0], dec_c[1])
			dtime = datetime.datetime.strptime(dec_c[2], '%Y-%m-%d%H:%M:%S')
			now = datetime.datetime.now().strftime('%Y-%m-%d%H:%M:%S')
			now2 = datetime.datetime.strptime(now, '%Y-%m-%d%H:%M:%S')

			#Time request comparison, note that this must not exceed in order to accept credentials. 
			latency = now2 - dtime
			latency_s = latency.total_seconds()
			print("Latency:" + str(latency_s))

			#The max logon request is set to 15 seconds max
			if latency_s > 15:
				#the request timed out
				print 'Request timed out.'
				send_msgenc(connectionSocket, AUTH_FAILURE, MSG_SIZE, pubKey)
				transHist(c[0], 'login', True)
				continue
		
			#erase the decrypted credentials
			dec_c = None

			#credential verification.
			found = False
			for i in accounts:
				if c[0] == i[0]:
					#password verification
					if argon2.verify(c[1], i[1]):
						found = True
					else:
						break
			if found:
				print ("The credentials entered mactch")
				send_msgenc(connectionSocket, AUTHENTICATION_SUCCESS, MSG_SIZE, pubKey)
				transHist(c[0], 'login', False)
			else:
				print "The credentails entered do not match"
				#The atm will refuse the invalid credentials entered
				send_msgenc(connectionSocket, AUTH_FAILURE, MSG_SIZE, pubKey)
				transHist(c[0], 'login', True)
				continue
			break

#########################################################################################################
#########################################################################################################
#######################Password will be removed from memory and user must enter #########################
#######################his/her bank account##############################################################
		username = c[0]
		c = None
###########################STARTS USER REQUEST===========================================================
		#While loop is being used so that the user can make a selection from 1-5
		while 1:
			#get request from the server
			print "Ready to receive requests from user {} from atm {}".format(username, atm_num)
			dec_request = receive_msgdec(connectionSocket, MSG_SIZE, privKey)
			print "request received: {} from user {} from atm {}".format(dec_request, username, atm_num)

			args = dec_request.split()
			
			#Option 1, which will check account's balance
			if dec_request[0] == '1':
				balance = 0
				for i in a_balance:
					if username == i[0]:
						balance = i[1]
				response_str = "Your current balance is: ${:.2f}".format(balance)
				send_msgenc(connectionSocket, response_str, MSG_SIZE, pubKey)
				transHist(username, 'view_balance')

			#Option 2, which will allow the user to withdrawl money from his/her account
			elif dec_request[0] == '2':
				amount = round(float(args[1]),2)
				count = 0
				for account in a_balance:
					if username == account[0]:
						break
					count += 1
				#if statement to check if the withdrawl can be completed successfully
				if (round(a_balance[count][1] - amount, 2) >= 0):
					a_balance[count] = (a_balance[count][0], a_balance[count][1] - amount)
					response_str = 'Your new balance is: ${:.2f}'.format(round(a_balance[count][1],2))
					print 'Money withrawn from this account'
					transHist(username, 'withdraw', (True, amount))
				else:
					response_str = 'Transaction failed. Current balance is ${:.2f}'.format(a_balance[count][1])
					print 'WITHDRAW: FAILURE'
					transHist(username, 'withdraw', (False, amount))
				send_msgenc(connectionSocket, response_str, MSG_SIZE, pubKey)

			#Option 3, which will allow the usser to deposit to current account
			elif dec_request[0] == '3':
				amount = round(float(args[1]),2)
				count = 0
				for account in a_balance:
					if username == account[0]:
						break
					count += 1
				a_balance[count] = (a_balance[count][0], a_balance[count][1] + amount)
				response_str = 'Your new balance is: ${:.2f}'.format(round(a_balance[count][1],2))
				print("Money deposited to the account.")
				transHist(username, 'deposit', amount)
				send_msgenc(connectionSocket, response_str, MSG_SIZE, pubKey)

			#Option4, which privides the current account's history
			elif dec_request[0] == '4':
				count = 0
				h = open('bank_statement/{}.txt'.format(username))
				for i in h:
					send_msgenc(connectionSocket, i, MSG_SIZE, pubKey)
				end_msg = ' '
				send_msgenc(connectionSocket, end_msg, MSG_SIZE, pubKey)

			#This option will log out the user from his/her account. 
			elif dec_request[0] == '5':
				response_str = "See you soon!"
				send_msgenc(connectionSocket, response_str, MSG_SIZE, pubKey)
				print 'Account logged off'
				transHist(username, 'logoff')
				break
				return
###########################END OF USER REQUEST============================================================


#Account information loaded from the files created/updated 
accounts, a_balance = loadAccounts()

serverPort = int(sys.argv[1])

#Socket1 to handle first ATM
serverSocket1 = socket(AF_INET, SOCK_STREAM)
serverSocket1.bind(('', serverPort))
serverSocket1.listen(0)
#Socket2 to handle second ATM
serverSocket2 = socket(AF_INET, SOCK_STREAM)
serverSocket2.bind(('', serverPort + 1))
serverSocket2.listen(0)
#Provides connection 
thread1 = threading.Thread(target=serv_connect, args=(serverSocket1, 1,))
thread2 = threading.Thread(target=serv_connect, args=(serverSocket2, 2,))
thread1.start()
thread2.start()

print "Accessing ATMs."

thread1.join()
thread2.join()
#Closes the sockets
serverSocket1.close()
serverSocket2.close()
#Calls the function to update the account
updateAccount(a_balance)

