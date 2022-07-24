import socket, threading
import os

def set_connection(t_address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(t_address)
    return sock

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
addr = ('127.0.0.1', 9993)
s.bind(addr)
 
lock = threading.Lock()
 
welcome_message = ('\r\nBenvenuto su Telnet Server\r\n\r\nOpzioni Disponibili\r\n\r\n'
                   + '1. Visualizzazione dei file disponibili\r\n'
                   + '2. Download di un file\r\n'
                   + '3. Upload di un file\r\n'
                   + '4. Esci\r\n')
t_ip = '127.0.0.1'
t_port = 10000
t_address = (t_ip, t_port)


class daemon(threading.Thread):
    def __init__(self, s, addr):
        threading.Thread.__init__(self)
        self.socket = s
        self.address = addr
        
    def run(self):
        data, client_address = self.socket.recvfrom(1024)
        self.socket.sendto(welcome_message.encode(), client_address)
        while(True):
            data, client_address = self.socket.recvfrom(1024)
            print(data.decode())
            
            if data[0] == '1':
                self.socket.sendto(t_address.encode(), client_address)
                skt = set_connection(t_address)
                data = '\r\n'+str(os.listdir())+'\r\n'
                skt.sendto(data.encode(), client_address)
                skt.close()
                
            elif data[0] == '2':
                self.socket.sendto(t_address.encode(), client_address)
                skt = set_connection(t_address)
                data, client_address = skt.recvfrom(4096)
                ret_msg = '0'
                
                try:
                    f = open(data.decode().strip(),'rb')
                    data = f.read(4096)
                    skt.sendto(data, client_address)
                    while (data):
                        if(s.sendto(data, client_address)):
                            data = f.read(4096)
                    f.close()
                except FileNotFoundError:
                    print('\r\nFile to download not found\r\n')
                    ret_msg = '1'
                    
                self.socket.sendto(ret_msg.encode(), client_address)
                skt.close()    
                
            elif data[0] == '3':
                self.socket.sendto(t_address.encode(), client_address)
                skt = set_connection(t_address)
                data, client_address = skt.recvfrom(4096)
                f = open(data.decode().strip(),'wb')
# =============================================================================
#                 try:
#                     while(data):
#                         f.write(data)
#                         skt.settimeout(2)
#                         data,addr = skt.recvfrom(4096)
#                 except socket.timeout:
#                     f.close()
#                     skt.close()
#                     print('\r\nFile uploaded\r\n')
# =============================================================================
                    
                while(data):
                    f.write(data)
                    data,addr = skt.recvfrom(4096)
                f.close()
                skt.close()
                print('\r\nFile uploaded\r\n')
                self.socket.sendto('0'.encode(), client_address)
                
            elif data[0] == '4':
                break
            
            else:
                self.socket.sendto(welcome_message.encode(), client_address)
        
        self.socket.close()

     
while True:
    daemon(s, addr).start()
