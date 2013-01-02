#!/usr/bin/env python
import smtplib
import argparse
import string
import md5
import re
import random
import auth

def auth(username, password):
  parse = re.search("([\w\.]*[\w])[@]([\w.]*[\w])", username)
  uname = parse.group(1)
  domain_name = parse.group(2)
  if domain_name == "gmail.com":
    mailserver = smtplib.SMTP("smtp.gmail.com", 587)
    mailserver.ehlo()
    mailserver.starttls()
    mailserver.ehlo()
    log = mailserver.login(username,password)
    result = "true"
    mailserver.close()
  else:
    print("Sorry, " + domain_name + " is not supported. Currently only Gmail authentication is available\n")
    return "false", ""
  return result, uname, log
  
def dkg():
  share = random.random()
  return share
  
def ibc(uname, share, master_share):
  public_key = uname
  private_key = random.random()
  return public_key

def main():
  print "**************WELCOME****************\n"
  print "This is the interface for the program\n"
  print "Please enter the email address and the password that you want to use as your identity : "
  iden = raw_input("Email address : ")
  passw = raw_input("Password : ")
  hashp = md5.new(passw).digest()
  auth_result, uname, log = auth(iden, passw)
  print passw
  if  auth_result is "true":
    print("Hello, " + uname + ". Authentication has been successful\n. Auth result is : ")
    print(log)
  else:
    print("Authentication failed. Either username or you password has been entered incorrectly. Try again")
    return
  
  print("Your public key is now" + ibc(uname, dkg(), dkg()))
  
if __name__ == "__main__":
  main()
