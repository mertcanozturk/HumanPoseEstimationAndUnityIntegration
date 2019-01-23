import  socket


def sending_and_reciveing():
   s = socket.socket()
   print('socket created ')
   port = 1234
   s.bind(('127.0.0.1', port)) #bind port with ip address
   print('socket binded to port ')
   s.listen(5)#listening for connection
   print('socket listensing ... ')
   while True:
       c, addr = s.accept() #when port connected
       print("\ngot connection from ", addr)
       de=c.recv(1024).decode("utf-8") #Collect data from port and decode into  string
       print('Getting Data from the Unity : ',de)
       list=de.split(',') #cominda data is postion so we split into list on basis of ,
       UpdateValue=""
       for value in list: #loop for each value in the string single
           value=str(value)#sonvet list value into string
           if '(' in value or ')' in value: #coming data in to form of (1.0,2.2,3.0),when split then we check each value dosnt contan '(' or ')'
               value=value.replace('(','') #if it ( contain any one of these we remove it
               value=value.replace(')', '')#if it ) contain any one of these we remove it
           C_value=float(value) #convert string value into float
           UpdateValue=UpdateValue+(str(C_value+3.0))+" " #add 3.0 into float value and put it in a string
       print('After changing data sending back to Unity')
       c.sendall(UpdateValue[:-1].encode("utf-8"))#then encode and send taht string back to unity
       c.close()
sending_and_reciveing()#calling the function to run server