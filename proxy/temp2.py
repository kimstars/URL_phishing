import SimpleWebSocketServer
import SimpleHTTPSServer
import urllib
PORT = 9012
class JustAProxy(SimpleHTTPSServer.SimpleWebSocketServer):
   def do_GET(self):
    #   url=self.path[1:]
    #   self.send_response(200)
    #   self.end_headers()
    #   self.copyfile(urllib.urlopen(url), self.wfile)
    print("DŨNG")
httpd = SimpleWebSocketServer.SimpleWebSocketServer('',PORT,JustAProxy)
print ("Proxy Srever at" , str(PORT))
httpd.serveforever()