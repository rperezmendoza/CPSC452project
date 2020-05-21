Name: Roberto Perez Mendoza
Assignment: Final Project
CPSC 452

Email: perezmendoza_roberto@csu.fullerton.edu
Programming language used: Python 2.7

How to execute: This project contains two directories and a bank.py file under the
"finalProject_rperezmendoza1" directory. In addition, one should be using two 
terminals for the bank server and atm to work properly. To do that do the following:
*Terminal1-.
     -Look for the directory where the project is located 
     -Enter this on the terminal: python ./bank.py
     -You shuld be able to create a password for both ATM1 and ATM2
		*Note: A verification will be required to verify that you entered the correct password
	 -Once successfully created the password, you must change to the server directory and run
	  the server class and include the port e.g. python ./server.py 8080
	 -You will then have to entered the password you created previously for both ATM1 and 2
     -A successfull connection should be prompted and you can go ahead and use the 2nd terminal
      in order to connect to the ATMs and do the transactions.

*Terminal2-.
    -For the second terminal, One must have to access to the atm directory and type the following
		* python ./atm.py 1 8080 localhost
     Note: 1 stands for ATM1, you can use 1 or 2. 8080 stands for the port connection, which was used
	in the bank's server previously. And we are using a localhost connection
    -A successful message will be displayed in the bank's server and the user should be able to see
	the menu prompted. In this case the user should be able to make selections such as view balances,
    make deposit, withdraw money, review history, and logoff from the atm machine.

Throughout these process, one should be able so see new files created, which provide a .txt with the 
records of the transactions as well as private/public keys for both ATM1,2, and server.



Anything special: Before running this program, one should be able to install the following libraries, otherwise the program won't work.
     *python-passlib
          -sudo apt-get update
          -sudo apt-get install python-passlib
     *aragon2_cffi
          -sudo pip install argon2_cffi

I also use the following OpenSSL to encrypt/decrypt files. Which I found helpful
online at https://stackoverflow.com/questions/16056135/how-to-use-openssl-to-encrypt-decrypt-files?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa

* openssl aes-256-cbc -salt -in server/afilesdec.txt -out server/afilesdec.txt.enc
* openssl aes-256-cbc -d -in a_bal.txt.enc -out a_bal.txt




//======================BANK ACCOUNTS & PASSWORDS THAT CAN BE USED===================================
The following accounts # and passwords can be used to test the ATM machine
*123456 => password -. welcome 
*789101 => password -. W3lc0m3 
*121314 => password -. !W3lc0m3! 
*151617 => password -. 43v3rpssw


//===============================NOTE VIDEO RECORDING================================================
As requested by you, below is the link to my video recordings. My video recordings demonstrate my 
a demo to my project. The video contains 2 parts. Below is the link to it:

https://drive.google.com/file/u/2/d/1OFq0CiSvhd6f0HYpk9R-wPF7BVcRKfxO/view?usp=drive_web


Please contact me if you have any issues.





























