import socket
import hashlib
import os
import subprocess
from datetime import datetime

def verify(var):
    try:
        with open(var[2],'rb') as f:
            data=f.read()
    except:
        conn.send('notfile')
        return

    md5hash=hashlib.md5(data).hexdigest()
    conn.send(md5hash)
    if conn.recv(1024)=='info':
        inf=subprocess.check_output('ls -l| sed \'1 d\'| awk \'{print $1" "$5" " $6" " $7" "$8" " $9}\'',shell=True)
        conn.sendall(inf)

def checkall():
    inf=subprocess.check_output('ls -l| sed \'1 d\'| awk \'{print $1" "$5" " $6" " $7" "$8" " $9}\'',shell=True)
    inf=inf.split("\n")
    conn.send(str(len(inf)))
    if conn.recv(1024)=='ok':
        for i in xrange(0,len(inf)-1):
            temp=inf[i].split(" ")
            conn.send(inf[i])
            if conn.recv(1024)=='givehash':
                if temp[0][0]=='-':
                    with open(temp[5],'rb') as f:
                        data=f.read()
                    md5hash=hashlib.md5(data).hexdigest()
                    conn.send(md5hash)
            else:
                conn.send('notfile')
def download(dtype,sendfile):
    #print sendfile
    if os.path.isfile(sendfile):
        conn.send('fileexist')
        if dtype=='UDP':
            udpport=int(conn.recv(1024))
            udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            addr = (host,udpport)
            print addr
            udps.sendto('recv',addr)
            f = open(sendfile, "rb")
            byte = f.read(1024)
            while byte:
                udps.sendto(byte, addr)
                data, addr = udps.recvfrom(1024)
                if data != "received":
                    break
                byte = f.read(1024)
            udps.sendto("done", addr)
            udps.close()
        if dtype=='TCP':
            with open(sendfile,'rb') as f:
                    data=f.read()
            l=len(data)
            conn.sendall('%16d' % l)
            ss=conn.recv(1024)
            if ss=='lenrecv':
                conn.sendall(data)
            f.close()

        t=conn.recv(1024)
        if t=='downdone':
            with open(sendfile,'rb') as f:
                data=f.read()
            md5hash=hashlib.md5(data).hexdigest()
            conn.sendall(md5hash)
            q=conn.recv(1024)
            if q=='fileinfo':
                fileinfo=subprocess.check_output('ls -l| sed \'1 d\'| awk \'{print $1" "$5" " $6" " $7" "$8" " $9}\'',shell=True)
                tempfileinfo=fileinfo
                fileinfo=fileinfo.split("\n")
                g=sendfile.split('/')
                for i in xrange(0,len(fileinfo)-1):
                        tem=fileinfo[i].split(" ")
                        if tem[5]==g[0]:
                            if tem[0][0]=='-':
                                conn.send('givenfile')
                                qq=conn.recv(1024)
                                if qq=="recvfileinfo":
                                    conn.sendall(tempfileinfo)
                            elif tem[0][0]=='d':
                                print "ddddd"
                                conn.send('givendirfile')
                                temp_file=sendfile.split('/');
                                temp_dir='/'.join(temp_file[:-1]);
                                os.chdir(temp_dir);
                                temp_arr_1=subprocess.check_output('ls -l| sed \'1 d\'| awk \'{print $1" "$5" " $6" " $7" "$8" " $9}\'',shell=True).split('\n')
                                if conn.recv(1024)=='recvdirinfo':
                                    conn.send(temp_arr_1)
                                os.chdir(shrdir)
                            break
                f.close()
    else:
        conn.send('notexist')

def index():
    longlist=subprocess.check_output('ls -l| sed \'1 d\'| awk \'{print $1" "$5" " $6" " $7" "$8" " $9}\'',shell=True)
    conn.sendall(longlist)

host='127.0.0.1'
port = 12345
s=socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host='127.0.0.1'
try:
    s.bind((host,port))
except:
    print "Socket creation error"
    exit(0)

s.listen(5)

shrdir=raw_input("Shared folder: ")

if not os.path.exists(shrdir):
    print "Doesn't exist"
    exit(0)

elif not os.access(shrdir,os.R_OK):
    print "No permissions"
    exit(0)
else:
    os.chdir(shrdir)

try:
    log=open("server_log","a+")
except:
    print "Cannot create a log file"
    exit(0)


while True:
    try:
        conn,addr=s.accept()
    except:
        s.close()
        timel = datetime.now().strftime("%I:%M%p %B %d, %Y")
        log.write("Server closed at"+timel+"\n")
        log.close()
        exit(0)
    var=conn.recv(1024)
    var=var.split(" ")
    if var[0]=='download':
        #conn.send('ok')
        if(len(var)<3):
            print "Wrong arguments"
        else:
            download(var[1],var[2])

    if var[0]=='index' and len(var)==2:
        index()

    if var[0]=='hash':
        if var[1]=='verify' and len(var)==3:
            verify(var)
        if var[1]=='checkall' and len(var)==2:
            checkall()
        else:
            print "wrong arguments"

    if var[0]=='sync':
        files=[]
        subdirs=[]
        for root,dirs,fnames in os.walk(shrdir):
            for sub in dirs:
                subdirs.append(os.path.relpath(os.path.join(root,sub),shrdir))
            for f in fnames:
                files.append(os.path.relpath(os.path.join(root,f),shrdir))
        msg=''
        dirs_to_client='';
        for given_file in subdirs:
                hash_val='0';
                mod_t = str(os.path.getmtime(given_file));
                dirs_to_client+=given_file+' '+hash_val+' '+mod_t+" ";
        rem=len(dirs_to_client);
        conn.send("sent "+str(len(dirs_to_client)));
        rem=conn.recv(1024);
        conn.send(dirs_to_client);
        rem=conn.recv(1024);

        for each in files:
            hshfile=os.path.join(shrdir,each)
            with open(hshfile,'rb') as f:
                data=f.read()
            hsh=hashlib.md5(data).hexdigest()
            tmod=str(os.path.getmtime(each))
            msg+=each+" "+hsh+" "+tmod+" "
        msglen=len(msg)
        conn.send("sent"+" "+str(msglen))
        if conn.recv(1024)=='recv msg':
            conn.send(msg)
            #temmsg=conn.recv(1024)
            #if temmsg=='Recv data':
                #conn.send('compare')
            p=conn.recv(1024)
            p=p.split(" ")
            print p[1]
            if p[0]=="lendict":
                conn.send('okrecv')
                #print "hi",len(plen)," "
                for i in range(0,int(p[1])):
                    z=conn.recv(1024)
                    z=z.split(" ")
                    if z[0]=='fildownload':
                        download('TCP',z[1])
                    else:
                        pass

conn.close()
s.close()
