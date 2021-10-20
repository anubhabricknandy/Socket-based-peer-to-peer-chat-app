#---------------------------------Importing Libraries
import tkinter
from tkinter import Button, StringVar
from tkinter import Tk
from tkinter import PhotoImage
import socket
import threading
from tkinter import Listbox
from tkinter import Entry
from tkinter import Scrollbar

#------------------A function to calculate power of a number
def fast_exp(b,e,m):

    if e==0:
        return 1
    half=int(e/2)
    
    ret=fast_exp(b,half,m)
    if e%2==0:
        return (ret*ret)%m
    else:
        return (((ret*ret)%m)*b)%m

#--------Extended Euclid's algorithm for calculating multiplicative inverse
def Extended_Euclid(x,y):
  if(y==0):
    return (x,0,1)
  g,x1,y1=Extended_Euclid(y,x%y)
  return (g,y1-int(x/y)*x1,x1)

#------Multiplicative inverse calculation
def Multiplicative_inverse(x,y):
    g,x1,y1=Extended_Euclid(y,x%y)
    if(g!=1):
        print("No multiplicative inverse exists for this pair")
        return "does not exist"
    else:
          return (x1%y)

#--------letter to digit coversion
def letter_to_digit(text):
    l=[]
    i=0
    while i<len(text):
        l.append(ord(text[i])-ord(" "))
        i+=1

    return l

#----------digit to letter conversion
def digit_to_letter(l):
    t=""
    for i in l:
        t+=chr(i+ord(" "))

    return t

#-----------encrypting each of the characters using letter to digit technique
#---------then converting the digits usingRSA then decrypting back using digit to letter
def encrypt(msg, public_key):
    n,e = public_key
    blocks = letter_to_digit(msg)
    cipher = []
    for i in blocks:
        c = pow(i,e,n)
        cipher.append(c)
    return digit_to_letter(cipher)

def decrypt(cipher, private_key):
    n,d = private_key
    msg = []
    blocks=letter_to_digit(cipher)
    for i in blocks:
        t = pow(i,d,n)
        msg.append(t)
    return digit_to_letter(msg)

#--------------------------------Sending message function
def sendm():
    global count
    global port
    global sock
    global public_key
    global Receiver_IP

    
    print("send",count,lstbox.size())
    #--------------------------Connection establishment to the socket happens only first time
    #------------------After that this socket is used for further sending of messages

    if count==0:
    #---------------first time connection establishment
#----------------------If the other user is not listning, cannot establish connections------------
    #-----------------If the other user stopped the connection, means this user's connection
    ###--- will also be stopped, so this user cannot establish the connection newly until the 
    ###--- other user comes back
        try:
            sock.connect((Receiver_IP,port))
        except :
            lstbox.insert(lstbox.size(),"Reciever may not be online")
            lstbox.insert(lstbox.size(),"Please click the + Button")
            return
        msg=msgbox.get()
        lstbox.insert(lstbox.size(),"You :: "+msg)
#-------------this send does not require a try because this will only happen when the connection
###--is established, if the connection gets closed by the other side then definately this
###--connection will be stopped and all will be initialized to starting state.
        msg=encrypt(msg,public_key)
#----------------for threading if the receiver thread is pre empted before reinitializing the
###-- count to zero this may happen
        try:
            sock.send(bytes(msg,"utf-8"))
        except:
            lstbox.insert(lstbox.size(),"It seems like other user has stopped the connection")
        count=1
    else:
        msg=msgbox.get()
        lstbox.insert(lstbox.size(),"You :: "+msg)
        msg=encrypt(msg,public_key)
        try:
            sock.send(bytes(msg,"utf-8"))
        except:
            lstbox.insert(lstbox.size(),"It seems like other user has stopped the connection")
        
        

        



#----------------------A function to send message thread
def threadsend():
    #------Creating a new thread for sending the message every time
    t=threading.Thread(target=sendm)
    t.start()

#-------------------A function to receive message
def receivem():
    global count
    global ls
    global lport
    global conn
    global flag
    global sock
    global private_key

    flag=1
    print(type(ls))
    ls.bind((socket.gethostbyname(socket.gethostname()),lport))
    ls.listen(100)
    print("user_2 is listning")
    #-------------Other user is not present in the system
    #-------After connection establishment and before getting the first message it stands here
    #---Even if user has started sending until it receives a msg it stays here
    try:
        conn,addr=ls.accept()
    except:
        print("check")
        return
    print("connection established")

    while True:
        print("receive",count,lstbox.size())
        try:
#--------------------Aborted by the other user
            data = conn.recv(64)
            if  not data:
                lstbox.insert(lstbox.size(),"Other user has stopped the connection")
                conn.close()
                ls.close()
                sock.close()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                count=0
                flag=0
                break
        #-----closing all connections from this side
        #-----Redefining the sockets because the other user may come back
        #-----Already closed sockets cannot be reused
        #-----If we do not close the old sockets and redefine the variable,
        ###--we cannot reconnect the socket with new address.
        #----------Also for new connection the two flags should be reinitialized to 0
        except :
#----------------------Aborted by this user
            print("connection stopped")
            conn.close()
            ls.close()
            sock.close()
            break
        #-----closing all connections from this side
        #-----Redefining the sockets because the other user may come back
        #-----Already closed sockets cannot be reused
        #-----If we do not close the old sockets and redefine the variable,
        ###--we cannot reconnect the socket with new address.
        #----------Also for new connection the two flags should be reinitialized to 0
        recvd_msg=str(data.decode("utf-8"))
        recvd_msg=decrypt(recvd_msg,private_key)
        lstbox.insert(lstbox.size(),"client ::"+recvd_msg)
        




#----------------------function to create a thread to receive msgs--------------
def threadreceive():
    global flag
    global count
    #------Already receive Thread started or not
    if flag==1:
        lstbox.insert(lstbox.size(),"already connected")
        return

    t=threading.Thread(target=receivem)
    t.start()
    print("statement")



#---------------------------function occurs during closing the chatbox app-------
def on_closing():
        print("user_2 closing")
        global ls
        global sock
        global conn
        ls.close()
        conn.close()
        sock.close()
#-----IMP----If only sending is done the receiver is still at conn,addr=ls.accept,
###--so to get to the esceotion ls must be closed from here also sock is not closed anywhere
###-- It should be closed from here
        root.destroy()
#-----------Close the listening socket, once this is closed the recv function will throw exception
#-------the exception will be in receivem----------------
#-----------all threads executed and sockets reassigned along with chat app closed--------
    


sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
ls=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
conn=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

lport=12345 ##sender port
flag=0  ##flag for the receiver
count=0 ## flag for sender

Receiver_IP=""
print("Please Enter REceiver_IP")
Receiver_IP=input()
port=""
print("Please Enter Receiver's port")
port=int(input())

p = 19
q = 5
e = 5
n = p * q
phi = (p-1)*(q-1)
d=Multiplicative_inverse(e,phi)
public_key = (n,e)
private_key = (n,d)



root=Tk()
root.geometry("300x400")
root.resizable(False, False)




msg=StringVar()
msgbox=Entry(root,textvariable=msg,font=('calibre',10,'normal'),border=2,width=35)
msgbox.place(x=10,y=350)


scrollbar = Scrollbar(root, orient="vertical")
lstbox=Listbox(root,height=20,width=45,yscrollcommand=scrollbar.set)
scrollbar.config(command=lstbox.yview)
lstbox.place(x=10,y=30)
scrollbar.pack( side = "right", fill ="y" )


start_img=PhotoImage(file="new_start_b.png")
startb=Button(root,image=start_img,command=threadreceive,borderwidth=0,height=30,width=30)
startb.place(x=120,y=0)

send_img=PhotoImage(file="send_resized.png")
sendb=Button(root,image=send_img,command=threadsend,borderwidth=0,height=30,width=30)
sendb.place(x=250,y=345)

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()


