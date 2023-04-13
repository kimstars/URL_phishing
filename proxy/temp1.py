import socket
import threading
import signal
import sys
import requests

config =  {
            "HOST_NAME" : "127.0.0.1",
            "BIND_PORT" : 5555,
            "MAX_REQUEST_LEN" : 1024,
            "CONNECTION_TIMEOUT" : 5
          }

def HTTP_request_he_to_she(http_request):
    lines = http_request.split('\n')
    index = False
    text = ""
    for i in range(len(lines)) :
        if lines[i] == "" :
            try :
                index = i+1
                text = lines[i+1]
            except IndexError :
                return False

        if "Content-Type: image" in lines[i] :
            return False

    text.replace(" he ", " she ")
    # print(text)
    if index != False :
        lines[index] = text
    else :
        return False
    return lines




class Server:
    """ The server class """

    def __init__(self, config):
    # Shutdown on Ctrl+C
        signal.signal(signal.SIGINT, self.shutdown) 

        # Create a TCP socket
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Re-use the socket
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # bind the socket to a public host, and a port   
        self.serverSocket.bind((config['HOST_NAME'], config['BIND_PORT']))
        
        self.serverSocket.listen(10) # become a server socket
        self.__clients = {}



    def listenForClient(self):
        """ Wait for clients to connect """
        while True:

            # Establish the connection
            (clientSocket, client_address) = self.serverSocket.accept() 
            
            d = threading.Thread(name=self._getClientName(client_address), 
            target = self.proxy_thread, args=(clientSocket, client_address))
            # d.setDaemon(True)
            d.daemon = True
            d.start()


    def proxy_thread(self, conn, client_addr):
        """
        *******************************************
        *********** PROXY_THREAD FUNC *************
          A thread to handle request from browser
        *******************************************
        """

        # request_from_browser = conn.recv(config['MAX_REQUEST_LEN'])        # get the request from browser
        # request_from_proxy = request_from_browser

        # get the request from browser
        request = conn.recv(config['MAX_REQUEST_LEN']) 

        a = str(request, 'UTF-8')

        # parse the first line
        first_line = a.split('\n')[0]


        try :                 # parse the first line
            url = first_line.split(' ')[1]   
        except IndexError :
            url = ""                     # get url
        
    
        # print(url[:50])

        if url.find('http') != -1:
            print(url)
            URL_host = "http://127.0.0.1:5000/url"
            PARAMS = {'url':url}
            r = requests.post(url = URL_host, params = PARAMS)
            print(r.text)


        http_pos = url.find("://") # find pos of ://
        if (http_pos==-1):
            temp = url
        else:
            temp = url[(http_pos+3):] # get the rest of url

        port_pos = temp.find(":") # find the port pos (if any)

        # find end of web server
        webserver_pos = temp.find("/")
        if webserver_pos == -1:
            webserver_pos = len(temp)

        webserver = ""
        port = -1
        if (port_pos==-1 or webserver_pos < port_pos): 

            # default port 
            port = 80 
            webserver = temp[:webserver_pos] 

        else: # specific port 
            port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
            webserver = temp[:port_pos] 

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            s.settimeout(config['CONNECTION_TIMEOUT'])
            s.connect((webserver, port))
            s.sendall(request)
            while 1:
                # receive data from web server
                data = s.recv(config['MAX_REQUEST_LEN'])

                if (len(data) > 0):
                    conn.send(data) # send to browser/client
                else:
                    break
            s.close()
            conn.close()
        except socket.error as error_msg:
            # print('ERROR: ',client_addr,error_msg)
            if s:
                s.close()
            if conn:
                conn.close()


    def _getClientName(self, cli_addr):
        """ Return the clientName.
        """
        return "Client"


    def shutdown(self, signum, frame):
        """ Handle the exiting server. Clean all traces """
        self.serverSocket.close()
        sys.exit(0)


if __name__ == "__main__":
    print("the program is starting")
    server = Server(config)
    
    server.listenForClient()
