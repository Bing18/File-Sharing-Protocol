import socket
import sys
import hashlib
import re
import subprocess
import os
from datetime import datetime

def printfileinf(temp):
    if temp[0][0]=='-':
        print "File ",
    elif temp[0][0]=='d':
        print "directory ",
    print temp[1]," ",
    print temp[2]," ",
    print temp[3]," ",
    print temp[4]," ",
    print temp[5]

def regex(var,pattern):
    var=var.split("\n")
    fnames=[]
    for i in xrange(0,len(var)-1):
        temp=var[i].split(" ")
        fnames.append(temp[5])
    regnames=[]
    for element in fnames:
        m=re.match(pattern,element)
        if m:
            t=m.group()
            regnames.append(t)
    for i in xrange(0,len(var)-1):
        temp=var[i].split(" ")
        for j in xrange(0,len(regnames)):
            if temp[5]==regnames[j]:
                printfileinf(temp)

def shortlist(var,start="",end="",flag=1):
    var=var.split("\n")
    for i in xrange(0,len(var)-1):
        temp=var[i].split(" ")
        res=0
        if flag==0:
            res=compare(start,end,temp)
        if  res==1 or flag==1:
            printfileinf(temp)

def compare(start,end,temp):
    timestamp1=temp[2]+" "+temp[3]+" "+temp[4]
    t1=datetime.strptime(timestamp1,"%b %d %H:%M")
    stime=datetime.strptime(start,"%b %d %H:%M")
    etime=datetime.strptime(end,"%b %d %H:%M")
    if stime<=t1 and t1<=etime:
        return 1
    else:
        return 0

def verify():
    a=c.recv(1024)
    if a!='notfile':
        print a #hashvalue
        c.send('info')
        temp=c.recv(1024)
        temp=temp.split("\n")
        for i in xrange(0,len(temp)-1):
                tem=temp[i].split(" ")
                if tem[5]==inp[2]:
                    print tem[2],tem[3],tem[4]

def checkall():
    l=int(c.recv(1024))
    c.send('ok')
    for i in xrange(0,l-1):
        var=c.recv(1024)
        c.send('givehash')
        var=var.split(" ")
        hsh=c.recv(1024)
        if hsh!='notfile':
            print hsh," ",
            print var[5],var[2],var[3],var[4]

def changeperm(temp):
    user=0;grp=0;oth=0;
    if(temp[1]=='r'):
        user+=4;
    if(temp[2]=='w'):
        user+=2;
    if(temp[3]=='x'):
        user+=1;
    if(temp[4]=='r'):
        grp+=4;
    if(temp[5]=='w'):
        grp+=2;
    if(temp[6]=='x'):
        grp+=1;
    if(temp[7]=='r'):
        oth+=4;
    if(temp[8]=='w'):
        oth+=2;
    if(temp[9]=='x'):
        oth+=1;
    return '0'+str(user)+str(grp)+str(oth);

def download(ftype,fname):
    downrecv=c.recv(1024)
    if downrecv=='fileexist':
        if ftype=='UDP':
            udps=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udpport=34523
            udps.bind((host,udpport))
            c.send(str(udpport))
            udp_data,addr=udps.recvfrom(1024)
            if udp_data=="recv":
                try:
                    f=open(fname,'wb')
                    while True:
                        data, addr = udps.recvfrom(1024)
                        if data == "done":
                            break
                        f.write(data)
                        udps.sendto("received", addr)
                    f.close()
                    udps.close()
                except:
                    print "Connection Error"
                    return

        elif ftype=='TCP':
            try:
                print fname
                f=open(fname,'wb')
                length=int(c.recv(16))
                c.send('lenrecv')
                templen=0
                totdata=""
                while length>templen:
                    data=c.recv(1024)
                    if not data:
                        break
                    templen+=len(data)
                    totdata+=data
                f.write(totdata)
                f.close()
            except:
                print "Connection Error"
                return
        else:
            print "Wrong arguments"
            return

        c.sendall('downdone')
        #checking hash values
        with open(fname,'rb') as f:
            data=f.read()
        hashval=hashlib.md5(data).hexdigest()
        orighash=c.recv(1024)
        if orighash==hashval:
            print "downloaded succesfully"
            c.sendall('fileinfo')
            some=c.recv(1024)
            if some=='givenfile':
                c.send('recvfileinfo')
                temp=c.recv(1024) #ls -l output includes directory
                temp=temp.split("\n")
                for i in xrange(0,len(temp)-1):
                        tem=temp[i].split(" ")
                        if tem[5]==fname:
                            mode=changeperm(tem[0])
                            subprocess.call(['chmod',mode,fname])
                            print tem[5],tem[1],tem[2],tem[3],tem[4]
                            print hashlib.md5(data).hexdigest()
                            break
            elif some=='givendirfile':
                c.send('recvdirinfo')
                #print "y1"
                temp=c.recv(1024)
                #print "y2",temp #ls -l output includes directory
                temp=temp.split("\n")
                for i in xrange(0,len(temp)-1):
                        tem=temp[i].split(" ")
                        if tem[5]==fname:
                            mode=changeperm(tem[0])
                            subprocess.call(['chmod',mode,fname])
                            print tem[5],tem[1],tem[2],tem[3],tem[4]
                            print hashlib.md5(data).hexdigest()
                            break

        else:
            print "donwload unsuccesfull"
        f.close()
    elif downrecv=='notexist':
        print "File doesn't exist"

host='127.0.0.1'
port=12345

def createclient():
    c=socket.socket()
    c.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        c.connect((host,port))
    except:
        print "No available server found"
        c.close()
        exit(0)
    return c

shrdir=raw_input("Shared folder: ")

if not os.path.exists(shrdir):
    print "Doesn't exist"
    exit(0)

elif not os.access(shrdir,os.R_OK):
    print "No permissions"
    exit(0)

try:
    log=open("server_log","a+")
except:
    print "Cannot create a log file"
    exit(0)

else:
    os.chdir(shrdir)



times = datetime.now().strftime("%I:%M%p %B %d, %Y")
log.write("\nClient connnection started at"+times+"\n")


currdict={}
oppdict={}
dict_dir={}

while True:

    c=createclient()
    c.send('sync')

    syncinit=c.recv(4096).split(" ");
    if(syncinit[0]=="sent"):
        c.send("recv msg");##MSG2
        rem=int(syncinit[1]);
        data_1=""
        while rem:
            temp=c.recv(1024);
            rem-=len(temp);
            data_1+=temp;
        c.send("Recieved Data");##MSG3
        dict_arr=data_1.split();
        for i in range(0,len(dict_arr),3):
            dict_dir[dict_arr[i]]=float(dict_arr[i+2]);

    else:
        c.send("Failed socket");##MSG2
        print "Socket operation Failed due to wrong arguments or loss of data";




    syncinit=c.recv(1024)
    syncinit=syncinit.split(" ")
    if syncinit[0]=="sent":
        c.send('recv msg')
        synlen=int(syncinit[1])
        syndata=""
        while synlen:
            temp=c.recv(1024)
            synlen-=len(temp)
            syndata+=temp
        #c.send('Recv data')
        syncmsg=syndata.split(" ")
        for i in range(0,len(syncmsg)-1,3):
            oppdict[syncmsg[i]]=syncmsg[i+1]+" "+syncmsg[i+2]
    else:
        print "Connection error"
    #c.close()

    files=[]
    subdirs=[]
    for root,dirs,fnames in os.walk(shrdir):
        for sub in dirs:
            subdirs.append(os.path.relpath(os.path.join(root,sub),shrdir))
        for f in fnames:
            files.append(os.path.relpath(os.path.join(root,f),shrdir))
    for each in files:
        with open(each,'rb') as f:
            data=f.read()
        hsh=hashlib.md5(data).hexdigest()
        currdict[each]=hsh+" "+str(os.path.getmtime(each))

    os.chdir(shrdir)
    for m in dict_dir.keys():
        if m not in subdirs:
            print "New "+m+" directory is Added";
            os.makedirs(m);

    samplist=''
    for k in oppdict.keys():
        if k in currdict.keys():
                a=oppdict[k].split(" ")
                b=currdict[k].split(" ")
                if float(a[1])>float(b[1]): #recent file on other side
                    samplist+=k+" "
                else:
                    pass

        else:
            samplist+=k+" "

    samplist=samplist.split(" ")
    print len(samplist),samplist
    c.send('lendict'+" "+str(len(samplist)))
    c.recv(1024)
    for i in range(0,len(samplist)-1):
        c.send('fildownload'+" "+samplist[i])
        download('TCP',samplist[i])

    c.close()

    print 'prompt->',
    inp=raw_input()
    c=createclient()
    log.write("Commands: "+inp+"\n")
    c.send(inp)
    inp=inp.split(" ")
    if inp[0]=='download':
        if(len(inp)<3):
            print "Wrong Arguments"
        else:
            download(inp[1],inp[2])

    elif inp[0]=='exit':
        break
    elif inp[0]=='index':
        if inp[1]=='longlist':
            var=c.recv(1024)
            shortlist(var)
        elif inp[1]=='shortlist':
            var=c.recv(1024)
            start=inp[2]+" "+inp[3]+" "+inp[4]
            end=inp[5]+" "+inp[6]+" "+inp[7]
            shortlist(var,start,end,0)
        elif inp[1]=='regex':
            c.sendall('longlist')
            var=c.recv(1024)
            regex(var,inp[2])
        else:
            print "111Wrong arguments"
    elif inp[0]=='hash':
        if inp[1]=='verify':
            verify()
        if inp[1]=='checkall':
            checkall()
        else:
            print "wrong arguments"
    else:
        print "22Wrong Arguments"

    #c.send('Thanks for connecting')
    c.close()
log.close()
exit(0)
