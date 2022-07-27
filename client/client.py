import socket, sys, signal


def signal_handler(signal, frame):
    try:
      if( sock ):
        sock.close()
    finally:
        print('\r\n Ctrl + C pressed: exit from the client \r\n')
        sys.exit(0)


if len(sys.argv) != 2:
    print('\r\n ! Indicare il numero di porta del server !')
    sys.exit()
    
signal.signal(signal.SIGINT, signal_handler)

server_ip = '127.0.0.1'
server_port = int(sys.argv[1])

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
server_addr = (server_ip, server_port)

sock.sendto('hello'.encode(), server_addr)
data, server_addr = sock.recvfrom(4096)
data = data.decode()

if data == 'full':
    print('\r\n Il server non può gestire nuovi client, riprovare più tardi\r\n')
    sock.close()
    sys.exit(1)

print(data)

while(True):
    value = input('Scegli l\'operazione da eseguire: ')
    sock.sendto(value.encode(), server_addr)
    
    if value == '1':
        data, server = sock.recvfrom(4096)
        print(data.decode() + '\r\n')
        
    elif value == '2':
        file = input('Inserisci il nome del file da scaricare: ')
        sock.sendto(file.encode(), server_addr)
        data, server = sock.recvfrom(4096)
        if data.decode() == '0':
            f = open(file.strip(),'wb')
            data, client_address = sock.recvfrom(4096)
            try:
                while(data):
                    f.write(data)
                    sock.settimeout(2)
                    data, addr = sock.recvfrom(4096)
            except socket.timeout:
                f.close()
                sock.settimeout(None)
                print('\r\nFile scaricato con successo\r\n\r\n')
        else:
            print('\r\nFile non trovato sul server\r\n\r\n')
            
    elif value == '3':
        file = input('Inserisci il nome del file da caricare: ')
        try:
            f = open(file.strip(),'rb')
            sock.sendto(file.encode(), server_addr)  
            data = f.read(4096)
            while (data):
                if(sock.sendto(data, server_addr)):
                    data = f.read(4096)
            f.close()
            data, server = sock.recvfrom(4096)
            if data.decode() == '0':
                print('\r\nFile caricato con successo\r\n\r\n')
        except FileNotFoundError:
            sock.sendto(''.encode(), server_addr) 
            print('\r\nFile locale non trovato\r\n\r\n')
            
    elif value == '4':
        break
     
    else:
        data, server = sock.recvfrom(4096)
        print(data.decode())
        
sock.close()