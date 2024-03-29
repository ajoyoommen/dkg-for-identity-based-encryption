import threading
import socket
import re
import sys
from ctypes import *
from datetime import datetime

nodeID = 0
identity = ""
tempcontlist = []
port = 1000
numNodes = 0
ip = '127.0.0.1'
sys_n = 1
sys_t = 1
sys_f = 1
sys_u = 0
ibc = cdll.LoadLibrary('files/libibc.so.1.0.1')


def read_contlist():
    """contlist contains the node contact addresses, load it into a list"""
    fp = open("files/contlist", "r")
    global tempcontlist, numNodes
    """reading from contlist and adding it to list tempcontlist for searching...
    tempcontlist[1] contains the contact details for node 3, and so on.
    tempcontlist[1] is again a list where each index represents
    - - - - 0:nodeID, 1:Ip addr, 2:Port num, 3:cert file for tls,
    - - - - 4:optional L to identify the leader
    numNodes tracks the total entries in contlist"""
    while 1:
        line = fp.readline()
        if not line:
            break
        numNodes += 1
        parse = re.search("([\S]+)\s([\S]+)\s([\S]+)\s([\S]+)\s([L]*)", line)
        tempcontlist.append([parse.group(1), parse.group(2), int(parse.group(3)) + 10, parse.group(4), parse.group(5)])
    fp.close()
    """Easiest way to retreive from tempcontlist
    jl = tempcontlist[int(nodeID)-1]
    print jl[2]"""


def read_sysparam():
    """This function will read system.param and initialize the values for n, t, f"""
    global sys_n, sys_t, sys_f
    fp = open("files/system.param", "r")
    n = fp.readline()
    t = fp.readline()
    f = fp.readline()
    p = fp.readline()
    u = fp.readline()
    fp.close()
    n = n.rstrip('\r\n')
    t = t.rstrip('\r\n')
    f = f.rstrip('\r\n')
    pr = re.search("(n)\s(\d)", n)
    if pr == None:
        print("Corrupted system.param(n). About to quit.")
        sys.exit()
    else:
        sys_n = int(pr.group(2))
    pr = re.search("(t)\s(\d)", t)
    if pr == None:
        print("Corrupted system.param(t). About to quit.")
        sys.exit()
    else:
        sys_t = int(pr.group(2))
    pr = re.search("(f)\s(\d)", f)
    if pr == None:
        print("Corrupted system.param(t). About to quit.")
        sys.exit()
    else:
        sys_f = int(pr.group(2))
    pr = re.search("(U)\s(.*)", u)
    if pr == None:
        print("Corrupted system.param(U). About to quit.")
        sys.exit()
    else:
        sys_u = pr.group(2)


def listen():
    """This socket will listen for all network messages"""
    global port, ip
    servsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        servsock.bind(('', int(port)))
    except Exception as e:
        print("Error : ", e)
    servsock.listen(5)
    while True:
        # print "Waiting for connection"
        conn, address = servsock.accept()
        # print "connection from ", address
        # print "Waiting for message"
        msg = conn.recv(1024)
        parse_msg(msg)
        print("Length of message received is ", len(msg))
    conn.close()
    servsock.close()
    return


def decrmsg(msg, nid):
    euvw = msg
    uvw = (c_ubyte * 168)(*map(ord, euvw))
    ibc.decompose(uvw)
    ibc.dirdecrypt()
    dmsg = (c_ubyte * 20).in_dll(ibc, "m")
    fmsg = (c_char * 20).from_buffer(dmsg).value
    fp = open("messages", "a")
    fp.write("From:", nid, ":Message:", fmsg, ":Time:", datetime.now(), ":END\n")
    fp.close()


def ibc_request_recv(stringid, nid):
    """On receiving an IBC_REQUEST, this will use PBC to hash^share the recvd ID
    and send it to the node from a new socket"""
    global tempcontlist, nodeID
    c_id = (c_char * 40)()
    c_id.value = stringid
    ibc.hash_id_s(c_id)
    hsid = (c_ubyte * 128).in_dll(ibc, "hid")
    ibcreply = (c_char * 128).from_buffer(hsid).value
    i = int(nid) - 1
    [nodeid, c_ip, c_port, cert_file, l] = tempcontlist[i]
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((c_ip, int(c_port)))
    except Exception as e:
        print("Unable to send : ", e, c_ip, c_port)
        return
    msg = "IBC_REPLY:" + ibcreply + ":" + nodeID + ":END"
    print("Sent (", len(msg), " bytes) : ", msg)
    sock.sendall(msg)
    sock.close()
    fp = open("contacts", "a")
    fp.write("ID:", nid, ":name:", stringid, "\n")
    fp.close()


def contactsretid(name):
    fp = open("contacts", "r")
    while 1:
        line = fp.readline()
        if not line:
            break
        pr = re.search("(ID:)([\d]+)(:name:)([\S]+)\s", line)
        if pr == None:
            return "None"
        else:
            if pr.group(4) == name:
                return pr.group(2)


def contactsretname(nid):
    fp = open("contacts", "r")
    while 1:
        line = fp.readline()
        if not line:
            break
        pr = re.search("(ID:)([\d]+)(:name:)([\S]+)\s", line)
        if pr == None:
            return "None"
        else:
            if pr.group(2) == nid:
                return pr.group(4)


def printallcontacts():
    fp = open("contacts", "r")
    while 1:
        line = fp.readline()
        if not line:
            break
        pr = re.search("(ID:)([\d]+)(:name:)([\S]+)\s", line)
        if pr == None:
            return "None"
        else:
            print
            pr.group(2), " ", pr.group(4)


def ibc_reply_recv(ibcreply, sender):
    global nodeID
    uchar = (c_ubyte * 128)(*map(ord, ibcreply))
    ibc.gen_privatekey(uchar, nodeID, sender)
    # sys.exit()


def parse_msg(msgstr):
    parse = re.search("([\w]+):(.*)", msgstr)
    if parse == None:
        print("Received invalid message : ", msgstr)
    elif parse.group(1) == "IBC_REQUEST":
        parseid = re.search("([\S]+):([\S]+)(:END)", parse.group(2))
        if parseid == None:
            print("Invalid IBC request : ", parse.group(2))
        else:
            print("Received : IBC request for the id ", parseid.group(1) + " from " + parseid.group(2))
            ibc_request_recv(parseid.group(1), parseid.group(2))
    elif parse.group(1) == "IBC_REPLY":
        parseid = re.search("([\S]+):([\S]+)(:END)", parse.group(2))
        if parseid == None:
            print("Received invalid IBC_REPLY : ", parse.group(2))
            # sys.exit()
        else:
            print("Received IBC_REPLY from ", parseid.group(2))
            ibc_reply_recv(parseid.group(1), parseid.group(2))
    elif parse.group(1) == "Message":
        parseid = re.search("([\S]+):ID:([\d]+)(:END)", parse.group(2))
        if parseid == None:
            print("Received invalid Message : ", parse.group(2))
            # sys.exit()
        else:
            print("Received Message from ", parseid.group(2))
            decrmsg(parseid.group(1), parseid.group(2))


def sendencrmsg(msg, strid, nid):
    if len(msg) > 20:
        tmsg = msg[:20]
    else:
        tmsg = msg
    cmsg = (c_ubyte * 20)(*map(ord, msg))
    cid = (c_char * 20)()
    cid.value = strid
    ibc.encrypt20(cmsg, cid)
    u = (c_ubyte * 128).in_dll(ibc, "u")
    cu = (c_char * 128).from_buffer(u).value
    i = int(nid) - 1
    [nodeid, c_ip, c_port, cert_file, l] = tempcontlist[i]
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((c_ip, int(c_port)))
    except Exception as e:
        print("Unable to send : ", e, c_ip, c_port)
        return
    msg = "Message:", tmsg, ":ID:", nodeID, ":END"
    sock.sendall(msg)
    sock.close()


def inbox():
    count = 0
    fp = open("messages", "r")
    print("No\tName\t\tTime\tMessage")
    while 1:
        line = fp.readline
        if not line:
            break
        count += 1
        pr = re.search("(From:)([\d]+)(:Message:)([\S]+)(:Time:)([\S]+)(:END\S)", line)
        if pr == None:
            print("Invalid line :", line)
        else:
            name = contactsretname(pr.group(2))
            print(count, "\t", name, "\t\t", pr.group(6), "\t", pr.group(4))


def sendRequest():
    """This socket will send IBC_REQUEST messages"""
    global tempcontlist, numNodes, nodeID, port
    for i in range(numNodes):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        [nodeid, c_ip, c_port, cert_file, l] = tempcontlist[i]
        if c_port == port:
            continue
        # print "i ", nodeID, "am trying to connect to ", nodeid, "at ", c_ip, int(c_port), c_port
        try:
            sock.connect((c_ip, int(c_port)))
        except Exception as e:
            print("Unable to send : ", e, c_ip, c_port)
            continue
        msg = "IBC_REQUEST:" + identity + ":" + nodeID + ":END"
        print("Sent : ", msg)
        sock.sendall(msg)
        sock.close()
    return


def sendReady():
    """This socket will send IBC_READY messages"""
    global tempcontlist, numNodes, nodeID, port
    for i in range(numNodes):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        [nodeid, c_ip, c_port, cert_file, l] = tempcontlist[i]
        if c_port == port:
            continue
        # print "i ", nodeID, "am trying to connect to ", nodeid, "at ", c_ip, int(c_port), c_port
        try:
            sock.connect((c_ip, int(c_port)))
        except Exception as e:
            print("Unable to send : ", e, c_ip, c_port)
            continue
        msg = "IBC_REQUEST:" + identity + ":" + nodeID + ":END"
        print("Sent : ", msg)
        sock.sendall(msg)
        sock.close()
    return


def init_pbc():
    read_contlist()
    read_sysparam()
    ibc.init_pairing(sys_n, sys_t, sys_f)
    ibc.read_share()
    gu = (c_char * 310)()
    gu.value = str(sys_u)
    ibc.readg(gu)


def start(username, nid):
    global port, ip, nodeID, identity
    identity = username
    nodeID = nid
    init_pbc()
    li = tempcontlist[int(nodeID) - 1]
    ip = li[1]
    port = li[2]
    threading.Thread(target=listen).start()
    option = input("Enter 1 to send request : ")
    if option == 1:
        threading.Thread(target=sendRequest).start()


def main():
    global port, ip, nodeID, identity
    # identity = username
    init_pbc()
    li = tempcontlist[int(nodeID) - 1]
    ip = li[1]
    port = li[2]
    threading.Thread(target=listen).start()
    option = input("Enter 1 to send request : ")
    if option == 1:
        threading.Thread(target=sendRequest).start()

    """r = input("Which row do you wish to print : ")
    r = r - 1
    print tempcontlist[r]"""


if __name__ == "__main__":
    main()
