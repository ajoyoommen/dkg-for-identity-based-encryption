#!/usr/bin/env python
import auth
import dkg
import ibc
import sys
import getpass
import sys

nodeid = 0


def readlist():
    global nodeid
    fp = open("files/identity", "r")
    i = fp.readline()
    nodeid = i.rstrip('\r\n')
    dkg.nodeid = int(nodeid)
    print("Read 'identity' and now node id is ", nodeid, dkg.nodeid)
    fp.close()


def main():
    print("**************WELCOME****************\n")
    print("This is the interface for the program\n")

    # Phase 1 - Authenticating the identity. The following code will retreive the username and password and send it to
    # the module auth.py

    auth_type = input(
        "Please select the type of authentication(Enter the number and press enter) \n\t1. Email\n\t2. LDAP\n\t\t:")
    if auth_type == '1':
        auth_str = "Email address"
    elif auth_type == '2':
        auth_str = "LDAP username"
    else:
        print("Invalid input")
        sys.exit()
    print("Please enter the " + auth_str + " that you want to use as your identity : ")
    username = input(auth_str + " : ")
    password = getpass.getpass("Please enter the password for your " + auth_str + " '" + username + "' : ")
    auth_result = auth.auth(username, password, auth_type)
    auth_result = "S"
    if auth_result is "S":
        print(
            "Hello, " + username + ". Authentication has been successful. You can now use your username as your "
                                   "Identity\n")
    else:
        print("Authentication failed")
        print(auth_result)
        return

        # Phase 2 - The DKG protocol can now start. It will run in a different thread. As soon as DKG completes,
        # the share is written to a file
    print("Please wait while the system initializes")
    readlist()
    global nodeid
    dkg.dkg(nodeid)


    print("Waiting for DKG to generate key .....   ", end=' ')
    while 1:
        if dkg.status == "sharegen":
            break
        else:
            pass

    print("Share Generated")

    # Phase 3 - Generate the keys using username and the share, the keys are stored in the loaded ibc library
    ibc.start(username, nodeid)

    # Phase 4 - Applications. the generated keys can be used to encrypt as well as decrypt messages
    option = input("Select what you would like to do : \n1. Send a Message\t2. View Inbox\n\t: ")
    if option == '1':
        msg = input("Enter the message to encrypt : ")
        print
        "Enter the name of the user you want to send to from this list :"
        ibc.printallcontacts()
        rnode = input("Enter the name :")
        ibc.sendencrmsg(msg, rnode, nodeid)
    elif option == '2':
        ibc.inbox()
    else:
        print("Incorrect option")
        return
    print("Exiting................")
    return


class NullWriter:
    def write(self, s):
        pass


# sys.stderr = NullWriter()

if __name__ == "__main__":
    main()
