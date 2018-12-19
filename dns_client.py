import time
import socket
import argparse
import os
import binascii
### Universal setings###
type_ ='A'
HOST =''
PORT = 53
site =''
tcpbool = False
#addr = (HOST,PORT)
connectionU = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
connectionT = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
connection = connectionU
#connection.settimeout(5)

parser = argparse.ArgumentParser()
parser.add_argument('-t',type=str, nargs='*')
parser.add_argument('--tcp',type=str, nargs=2)
args = parser.parse_args()
print()
if args.tcp and args.t:
    connection = connectionT
    type_= args.t[0] 
    HOST = args.tcp[0]
    site = args.tcp[1]
    tcpbool = True
    print('<<>> dns_client 0.9 <<>>','-t',type_,'--tcp',HOST,site)
   
if args.t and not args.tcp:
    type_= args.t[0]
    HOST = args.t[1]
    site = args.t[2]
    print('<<>> dns_client 0.9 <<>>','-t',type_,HOST,site)
def converter(s):
    res =''
    for i in range (0,len(s)):
        X = ord(s[i])
        strHex = "%0.2X" % X
        res += str(strHex)
    return res

def typeResolver(type_):
    if type_ == 'A':
        return '01'
    if type_ == 'NS':
        return '02'
    if type_ == 'CNAME':
        return '05'
    if type_ == 'SOA':
        return '06'
    if type_ == 'WKS':
        return '0b'
    if type_ == 'PTR':
        return '0c'
    if type_ == 'HINFO':
        return '0d'
    if type_ == 'MINFO':
        return '0e'
    if type_ == 'MX':
        return '0f'
    if type_ == 'TXT':
        return '10'
    if type_ == 'ANY':
        return 'ff'
#if (tcpbool):
 #   HOST = '45.79.221.152'
def udp(bytes):
    try:
        connectionT = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    except:
        print('error. Unable to create Connection')
    connection.settimeout(5)
    try:
        connection.connect(addr)
    except:
        print('Unable to connect, RE-run again to retry')
    stime = time.time()
    connection.send(bytes)
    dat = connection.recv(12040)
    tm = time.time()-stime
    connection.close()
    return (dat,tm)

def tcp(bytes):
    try:
        connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    except:
        print('error. Unable to create TCP Connection')
    
    connection.settimeout(5)
    prepend = binascii.unhexlify((hex(len(bytes))[2:]).rjust(4,'0'))
    bytes = prepend+bytes
    try:
        connection.connect(addr)
        print('Connection Established')
    except:
        print('Conncetion not Established, RE-run again to retry')
    rd  =b''
    stime = time.time()
    connection.send(bytes)
    dat =connection.recv(4096)
    while(dat):
        rd += connection.recv(4096)
        dat+=rd
        if not rd:  
            break
    tm =time.time()-stime
    connection.close()
    return (dat[2:],tm)

def siteProcess(site):
    result = ''
    index =[]
    j=0;i=0
    while i < len(site):
        if site[i] == '.':
            result+=str(i-j).rjust(2, '0')# adjust to 03 instead of 3
            asci = site[j:i]
            result+=converter(asci)
            j =i+1
            i=i+1
        i+=1
    end = j
    result +=str(len(site)-end).rjust(2, '0') + converter(site[end : len(site)])
    return result
addr = (HOST,PORT)
head ='dead'+'0100'+'00010000'+'00000000'
#      src    dest    seq       #ack
tail ='0000'+typeResolver(type_)+'0001'
message = head+siteProcess(site)+tail
bytes = binascii.unhexlify(message)

data =b''
qTime =0
size=0
if (tcpbool):
    tupl= tcp(bytes)
    data= tupl[0]
    qTime=tupl[1] 
else:
    tupl= udp(bytes)
    data= tupl[0]
    qTime=tupl[1]
size = len(data)

print('Query time:','%.2fms'%(qTime*100) )
print('Server:',HOST+'#'+str(PORT)+'('+HOST+')')
print('When', time.strftime("%c"))
print('MSG SIZE  rcvd:',size)

if (data):
    f = open('data.bin','wb')
    f.write(data)
    f.close()
    os.system('python3 dns_parse.py --f data.bin')
else:
    print('Data is empty')
