#bank class
import os
from Crypto.PublicKey import RSA
from passlib.hash import argon2
from subprocess import call

################################################################################
######################AT LEAST 4 ACCOUNTS PROVIDED##############################
################################################################################
#list of account numbers
accounts = [('123456', 'welcome'), ('789101', 'W3lc0m3'), ('121314', '!W3lc0m3!'), ('151617', '43v3rpssw')]

a_balance = [('123456', 695.36), ('789101', 781.57), ('121314', 542.25), ('151617', 62.47)]

#Opens the file "afilesdec.txt" located in the server directory in order to 
#hash the password
with open('server/afilesdec.txt', 'w') as h:
	for account in accounts:
		h.write(account[0] + ' ')
		#hashing the password
		hashpssw = argon2.hash(account[1])
		h.write(hashpssw + '\n')

#write accounts balance to the a_bal.txt file 
with open('server/a_bal.txt', 'w') as h:
	for account in a_balance:
		h.write(account[0] + ' ' + '{:.2f}'.format(account[1]) + '\n')

#encrypt created files using AES
#Note OpenSSL provides a popular, but insecure command line interface for AES encryption
#which has been used in this project. 
print("\n\n*****CREATE A PASSWORD FOR THE FOLLOWING*****\n\n")
print("Encryption password creation for ATM1")
ssl1 = 'openssl aes-256-cbc -salt -in server/afilesdec.txt -out server/afilesdec.txt.enc'.split()
call(ssl1)
print("\nEncryption password creation for ATM2")
ssl2 = 'openssl aes-256-cbc -salt -in server/a_bal.txt -out server/a_bal.txt.enc'.split()
call(ssl2)
print("\n*****PASSWORDS CREATED*****\n\n")

#Creating 3 different directories. One for atm key, server key, and customer records.
#This is to look for the keys easily.
#This files will be created under their belonging directory
os.mkdir('atm/atm_keys')
os.mkdir('server/server_keys')
os.mkdir('server/bank_statement')

#This loop will create keys for both atms.
for i in range(1,3):
    key = RSA.generate(2048)
    f = open('atm/atm_keys/atm{}_privkey.pem'.format(i), 'w')
    f.write(key.exportKey('PEM'))
    f.close()

    pub_key = key.publickey()
    f_handler = (open('atm/atm_keys/atm{}_pubkey.pem'.format(i), 'w'), open('server/server_keys/atm{}_pubkey.pem'.format(i), 'w'))
    for h in f_handler:
        h.write(pub_key.exportKey('PEM'))
        h.close()

key = RSA.generate(2048)
f = open('server/server_keys/server_privkey.pem', 'w')
f.write(key.exportKey('PEM'))
f.close()

pub_key = key.publickey()

f_handler = (open('atm/atm_keys/server_pubkey.pem', 'w'), open('server/server_keys/server_pubkey.pem', 'w'))
for h in f_handler:
    h.write(pub_key.exportKey('PEM'))
    h.close()
