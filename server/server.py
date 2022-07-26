import socket, os

ip = '127.0.0.1'
port = 321

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = (ip, port)
sock.bind(addr)
  
welcome_message = ('\r\nBenvenuto sul Server\r\n\r\nOpzioni Disponibili\r\n\r\n'
                   + '1. Visualizzazione dei file disponibili\r\n'
                   + '2. Download di un file\r\n'
                   + '3. Upload di un file\r\n'
                   + '4. Esci\r\n'
                   + 'Qualsiasi altro tasto per visualizzare l\'elenco dei comandi\r\n')

data, client_address = sock.recvfrom(1024)
sock.sendto(welcome_message.encode(), client_address)
while(True):
    data, client_address = sock.recvfrom(1024)
    data = data.decode()
    print('\r\n Command: ' + data)
    
    if data == '1':
        data = '\r\n'+str(os.listdir())+'\r\n'
        sock.sendto(data.encode(), client_address)
        
    elif data == '2':
        data, client_address = sock.recvfrom(4096)        
        try:
            f = open(data.decode().strip(),'rb')
            sock.sendto('0'.encode(), client_address)  
            data = f.read(4096)
            while (data):
                if(sock.sendto(data, client_address)):
                    data = f.read(4096)
            f.close()
        except FileNotFoundError:
            sock.sendto('1'.encode(), client_address)  
        
    elif data == '3':
        data, client_address = sock.recvfrom(4096)
        if data.decode() != '':
            f = open(data.decode().strip(),'wb')
            try:
                data, client_address = sock.recvfrom(4096)
                while(data):
                    f.write(data)
                    sock.settimeout(2)
                    data, addr = sock.recvfrom(4096)
            except socket.timeout:
                f.close()
                sock.settimeout(None)
            sock.sendto('0'.encode(), client_address)
        
    elif data == '4':
        break
    
    else:
        sock.sendto(welcome_message.encode(), client_address)

sock.close()
