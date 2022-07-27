import socket, os, threading, random, sys, signal


def signal_handler(signal, frame):
    try:
      if( sock ):
        sock.close()
    finally:
        print('\r\n Ctrl + C pressed: exit from the server \r\n')
        sys.exit(0)

def set_connection(ip, port, port_dict):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    new_port = port + random.randint(1, 100)
    lock.acquire()
    while new_port in port_dict.values():
        new_port = port + random.randint(1, 100)
    port_dict[sock] = new_port
    lock.release()
    addr = (ip, new_port)
    sock.bind(addr)
    return sock, port_dict

class daemon(threading.Thread):
    def __init__(self, s, client_address):
        threading.Thread.__init__(self)
        self.sock = s
        self.client_address = client_address
    def run(self):
        global port_dict
        self.sock.sendto(welcome_message.encode(), self.client_address)
        while(True):
            data, client_address = self.sock.recvfrom(1024)
            data = data.decode()
            print('\r\n Command: ' + data)
            
            if data == '1':
                lock.acquire()
                data = '\r\n'+str(os.listdir())+'\r\n'
                self.sock.sendto(data.encode(), client_address)
                lock.release()
                
            elif data == '2':
                lock.acquire()
                data, client_address = self.sock.recvfrom(4096)        
                try:
                    f = open(data.decode().strip(),'rb')
                    self.sock.sendto('0'.encode(), client_address)  
                    data = f.read(4096)
                    while (data):
                        if(self.sock.sendto(data, client_address)):
                            data = f.read(4096)
                    f.close()
                except FileNotFoundError:
                    self.sock.sendto('1'.encode(), client_address)
                lock.release()
                
            elif data == '3':
                lock.acquire()
                data, client_address = self.sock.recvfrom(4096)
                if data.decode() != '':
                    f = open(data.decode().strip(),'wb')
                    try:
                        data, client_address = self.sock.recvfrom(4096)
                        while(data):
                            f.write(data)
                            self.sock.settimeout(2)
                            data, addr = self.sock.recvfrom(4096)
                    except socket.timeout:
                        f.close()
                        self.sock.settimeout(None)
                    self.sock.sendto('0'.encode(), client_address)
                lock.release()
                
            elif data == '4':
                break
            
            else:
                self.sock.sendto(welcome_message.encode(), client_address)
        
        self.sock.close()
        lock.acquire()
        port_dict.pop(self.sock)
        lock.release()


if len(sys.argv) != 2:
    print('\r\n ! Indicare il numero di porta !')
    sys.exit()
    
ip = '127.0.0.1'
port = int(sys.argv[1])

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = (ip, port)
sock.bind(addr)
port_dict = dict()

lock = threading.Lock()
  
welcome_message = ('\r\n\r\nBenvenuto sul Server\r\n\r\nOpzioni Disponibili\r\n\r\n'
                   + '1. Visualizzazione dei file disponibili\r\n'
                   + '2. Download di un file\r\n'
                   + '3. Upload di un file\r\n'
                   + '4. Esci\r\n'
                   + 'Qualsiasi altro tasto per visualizzare l\'elenco dei comandi\r\n')

signal.signal(signal.SIGINT, signal_handler)

while (True):
    data, client_address = sock.recvfrom(1024)
    s, port_dict = set_connection(ip, port, port_dict)
    print(port_dict)
    daemon(s, client_address).start()
