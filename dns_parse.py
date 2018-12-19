import argparse
import binascii
import struct
import binascii

files ='test.bin'
parser = argparse.ArgumentParser()
parser.add_argument('--f',type=str, nargs='?')
args = parser.parse_args()
if (args.f):
    files = args.f

def extract(fileName):
    bytelist =[]
    with open(fileName,'rb') as f:
        while True:
            byte = binascii.hexlify(f.read(1))
            if not byte:
                break
            byte= str(byte)[2:4]
            bytelist.append(byte)
    f.close()
    return bytelist

def headers(l):
    '''l: list; Takes in a of bytes, prints headers and returns answer Count'''
    t_ID= l[0]+l[1]
    flags= l[2]+l[3]; bin = '{0:016b}'.format(int(flags, 16))
##header####
    qr = bin[0]
    opcode =''
    for x in range (1,4):
        opcode+=bin[x]
    opcode = int(opcode,2) # converting to decimal
    aa = bin[5]; tc = bin[6]; rd = bin[7]; ra = bin[8];
    z =''
    for x in range (9,11):
        z+=bin[x]
    z = int(z,2) # converting to dec
    rcode = ''
    for x in range (12,15):
        rcode+=bin[x]
    rcode = int(rcode,2) # converting to dec
    qdcount= int(l[4]+l[5],16); ancount= int(l[6]+l[7],16); nscount= int(l[8]+l[9],16) 
    arcount= int(l[10]+l[11],16)
    
##resolving indications##
##opcode###
    opstr =''
    if opcode == 0:
        opstr ='QUERY'
    if opcode ==1:
        opstr ='IQUERY'
    if opcode ==2:
        opstr ='STATUS'
    if opcode>2:
        opstr = 'RESERVED'
 ###RCODE###
    rstr=''
    if rcode == 0:
        rstr ='NOERROR'
    if rcode ==1:
        rstr ='FORMAT ERROR'
    if rcode ==2:
        rstr ='SERVER FAILURE'
    if rcode == 3:
        rstr ='NAME ERROR'
    if rcode ==4:
        rstr ='NOT IMPLEMENTED'
    if rcode ==5:  
        rstr ='REFUSED'

####
    print('->>HEADER<<---------\n|| opcode: ' +opstr+' ||status: '+rstr+ ' ||id: ', int(t_ID,16))
    print('||FlAGS--->>  qr: '+str(qr)+' aa: '+str(aa)+' tc: '+str(tc)+' rd: '+str(rd)
          +' ra: '+str(ra))
    print('||QUERY: '+str(qdcount)+'|| ANSWER: '+str(ancount)+' || AUTHORITY: '+str(+nscount)
          +'|| ADDITIONAL: '+str(arcount))
    return ( [ancount,nscount] )
###end Header###

def req(name,n,lists):    ##Recursive loop used to generage QNAME
    '''A loop to get the QNAME'''
    '''Takes in name provided by question function'''
    end=1
    while True:
        if lists[n+end] =='00': #or lists[n+end]=='03':
            break
        if int(lists[n+end],16)>= 32 and int(lists[n+end],16)<= 127: ###
            name+= chr(int(lists[n+end],16))
        else:
            name+= '.'
        end+=1
        #print(lists[n+end])
        #print(name)
    if lists[n+end] =='00':
        return (name+'.',n+end+1)
    #else:
     #   return (req(name+'.',n+end,lists),end)
    


def qORr(l,anscount,nscount):
    '''Takes in a byte list and answe count and checks if there's a query section
    also prints out the question and answe section'''
    lorp = l[12].strip()
    bin = '{0:08b}'.format(int(lorp, 16))
    qbool = False
    qloc = 12
    authN =0
    if (bin[0]+bin[1]) =='00':
        qbool =True
        qotuple = question(l,12)
        name =  qotuple[1]
        qloc =qotuple[0]
    if (qbool == True):
        authN= answer(l,qloc,name, anscount)
    if (qbool == False):
        authN= answer(l,12,name, anscount)
   # print('auth',authN)
    authority(l,authN,name,nscount)
    
def question(l,n): ### used in qORr
    '''Takes in a list of bytes and current list position n'''
    qname=''
    qtuple = req(qname,n,l)
    qname = qtuple[0]
    print('\n->QUESTION SECTION:')
    eoq = qtuple[1]
    qtype= int(l[eoq]+l[eoq+1],16)
    qclass= int(l[eoq+2]+l[eoq+3],16)
    
    print('{0:<34}'.format(qname),'{0:<4}'.format(classh(qclass)),
          '{0:<8}'.format(typeh(qtype)))
    return ( (eoq+4), (qname) )



def answer(l,n,name,anscount):
    '''prints the answer section and RR data'''
    pos =0
    if (anscount>0):
        print('->ANSWER SECTION<-')
        pos =answerloop(l,n,anscount,name)
    else:
        pos = n;
    #print('pos',pos, l[pos])
    return pos 

def answerloop(l,n,k,name): #used in answer function
    '''Takes in data from answer function and loops over till all data is compiled'''
    pos =processor(l,n)[1]
    if (k>1):
        return answerloop(l,pos,k-1,name)
    else:
        return pos

def authority(l,n,name,nscount):
    '''prints the authority section and RR data'''
    pos =n
    if (nscount>0):
        print('\n->Authority SECTION<-')
    pos =authorityloop(l,n,nscount,name)
    return pos

def authorityloop(l,n,k,name): #used in answer function
    '''Takes in data from answer function and loops over till all data is compiled'''
    try:
        gotdata = l[n]
    except IndexError:
        return
    pos = processor(l,n)[1]
    if (k>1):
        return authorityloop(l,pos,k-1,name)
    else:
        return pos

def classh(t):
    if (t==1):
        return 'IN'
    if (t==2):
        return 'CS'
    if (t==4):
        return 'HS'
    if (t==3):
        return 'CH'
    else:
      #  print('class',t)
        return 'UNSUPPORTED'

def typeh(t):
    if (t==1):
        return 'A'
    if (t==2):
        return 'NS'
    if (t==5):
        return 'CNAME'
    if (t==6):
        return 'SOA'
    if (t==11):
        return 'WKS'
    if (t==12):
        return 'PTR'
    if (t==13):
        return 'HINFO'
    if (t==14):
        return 'MINFO'
    if (t==15):
        return 'MX'
    if (t==16):
        return 'TXT'
    if (t==255):
        return 'ANY'
    else:
     #   print('type',t)
        return 'UNSUPPORTED'

   ####TYPE Handling####

def formatting(l,c,rdlength,pos,name):
    '''function handling NS A and CNAME types'''
    rdata =''
    if c==2: ##handle NS
        rdata =''
        act = recursor(l,pos)
        rdata = ascii(act[0])

    if c==1: ## handle A
        for x in range(0,rdlength):
            rdata+= str(int(l[pos+x],16))

            if x!=rdlength-1:
                rdata+='.'
    
    if c==5: #CNAME Authority HAndling
        rdata =''
        act =recursor(l,pos)
        rdata = ascii(act[0])
        
        '''
        lr = l[pos:pos+rdlength]
        print('lr',lr)
        for x in range(pos,pos+rdlength):
            rdata+= str(int(l[x],16))
            '''
###soa Handling###
    if c == 6:
        act1 = recursor(l,pos)
        mname= ascii(act1[0])
        act2 = recursor(l,act1[1])
        rname = ascii(act2[0])
        #serial#
        pointer = act2[1]
        serial = int(''.join(l[pointer:pointer+4]),16)
        pointer = pointer+4
        refresh = int(''.join(popper(l[pointer:pointer+4])),16)
        pointer = pointer+4
        retry = int(''.join(popper(l[pointer:pointer+4])),16)
        pointer = pointer+4
        expire = int(''.join(popper(l[pointer:pointer+4])),16)
        pointer = pointer+4
        minimum = int(''.join(popper(l[pointer:pointer+4])),16)

        rdata =mname+' '+rname+' '+str(serial)+' '+str(refresh)
        rdata+=' '+str(retry)+' '+str(expire)+' '+str(minimum)
        
#### WKS #####
    if c==11:
        dat = l[pos:pos+rdlength]
        temp = dat[0:4]
        address=''
        for x in range(0,4):
            address+= str(int(temp[x],16))
            if x!=len(dat)-1:
                address+='.'
        protocol = str(int(''.join(dat[4:5]),16))
        bitmap = dat[5:]
        bin =''
        for i in range (0,len(bitmap)):
            bin+= '{0:08b}'.format(int(bitmap[i],16))
        bitmap =''
        for i in range (0,len(bin)):
            if bin[i] == '1':
                bitmap+=str(i)+' '
        
        rdata = address+' '+protocol+' '+bitmap
#### PTR ###
    if c ==12:
        act = recursor(l,pos)
        rdata = ascii(act[0])
###HINFO####
    if c ==13:
        cpu =''
        os =''
        act1 = recursor(l,pos)
        cpu= ascii(act1[0])
        act2 = recursor(l,act1[1])
        os = ascii(act2[0])        
        rdata = cpu+' '+ os

#####MINFO#####
    if c ==14:
        rmail =''
        email =''
        ext =''
        ext2 =''
        act1 = recursor(l,pos)
        rmail = act1[0]
        act2 = recursor(l,act1[1])
        email = act2[0]
        rdata = ascii(rmail)+' '+ascii(email)
        '''
        i =pos+1
        while(i< len(l) and l[i]!='c0' and l[i] !='00'):
            rmail+= l[i]
            ext += l[i] +','
            i+=1
        i=i+2
        while(i< len(l) and l[i]!='c0' and l[i] !='00'):
            email+= l[i]
            ext2 += l[i] +','
            i+=1
        rdata = rmail+' '+email
        '''

###MX####
    if c ==15:
        rdata =''
        data = l[pos:pos+rdlength]
        ref  = int(data[0]+data[1],16)
        act = recursor(l,pos+2)
        rdata = str(ref)+' '+ascii(act[0])
        
        
#### TXT 16 ##
    if c ==16:
        text =''
        '''
        i =pos+1
        while(i< len(l) and l[i]!='c0' and l[i] !='00'):
            text+= l[i]
            i+=1            
        rdata = '"'+ascii(text)+'"'
        '''
        act = recursor(l,pos+1)[0]
        data = l[pos+1:pos+rdlength]
        rdata = '"'+ ascii(''.join(data))+'"'
        rdata ='"'+ascii(act)+'"'
    return rdata


def ascii(hexstr):
    asciistr=''
    x =1
    while x < len(hexstr):
        integ =int(hexstr[x-1]+hexstr[x],16)
        if integ not in range (32,127):
            asciistr+='.'
        else:
            asciistr+= chr(integ)
        x+=2
    i =1
    if len(asciistr)>0 and asciistr[0] =='.':
        asciistr =asciistr[1:]
    while (i<len(asciistr)):
        if (asciistr[i-1] =='.' and asciistr[i]=='.'):
            asciistr.replace('.','',i-1)
        i+=1
    if len(asciistr)>0 and asciistr[len(asciistr)-1] =='.':
        return asciistr
    else:
        return asciistr+'.'

def recursor(l,n):
    '''function used to show Authority and Answers'''
    holder=''
    pointer =[]
    p = n
    
    flag =False
    while (1):
        if not p<len(l):
            break
        if  l[p]=='00': #and l[p+1]=='00' and :
            break
        if (l[p]== 'c0'):
            pointer.append(p)
            flag =True
            bin = '{0:08b}'.format(int(l[p], 16))
            bin+= '{0:08b}'.format(int(l[p+1], 16))
            bin = bin[2:]
            loc = int(bin,2)
            p = loc
        holder+=l[p]
        p+=1
    if flag:
        #print('flag',pointer[0]-4,l[pointer[0]-4:pointer[0]],ascii(holder),l[pointer[0]])
        return(holder,pointer[0]+2)
    else:
        return(holder,p+1)

####
def processor(l,n):
    '''function used to show Authority and Answers'''
    holder=''
    p = n
    pointers =[]
    flag =False
    while (p<len(l)):
        if not p<len(l):
            break
        if l[p]=='00' and l[p+1]=='00':
            break
        if (l[p]== 'c0'):
            pointers.append(p)
            flag =True
            bin = '{0:08b}'.format(int(l[p], 16))
            bin+= '{0:08b}'.format(int(l[p+1], 16))
            bin = bin[2:]
            loc = int(bin,2)
            p = loc
        holder+=l[p]
        p+=1
    if (flag):
        ptr = pointers[0]+2
    else:
        ptr =p+1
    ty= int(''.join(l[ptr:ptr+2]),16)
    cl= int(''.join(l[ptr+2:ptr+4]),16)
    ttl=int(''.join(l[ptr+4:ptr+8]),16)
    rdlength = int(''.join(l[ptr+8:ptr+10]),16)
    rrname = ascii(holder)
    pos = ptr+10
    
    print('{0: <25}'.format(rrname),'{0: <8}'.format(ttl),
          '{0: <4}'.format(classh(cl)),
          '{0: <6}'.format(typeh(ty)),
          formatting(l,ty,rdlength,pos,rrname)) 
          
    
    pos =pos+rdlength
    return (ascii(holder),pos)

def popper(ls):
    if  len(ls) ==4 and ls[3]=='00' :
        ls.pop(3)
    if ls[1]!='00' and ls[2]=='00':
        ls.pop(2)
    if ls[1]=='00' and ls[2]!='00':
        ls.pop(1)
    if ls[0] =='00':
        ls.pop(0)
    return ls


print()        
bytes = extract(files)
#processor(bytes,29)
ac = headers(bytes)
print(ac)
qORr(bytes,ac[0],ac[1])

print()





