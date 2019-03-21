"""
this library is use basic library to simulate simple Server
"""
__all__ = ["httpserver", "httpserver_stop"]

# import default system library
import http.server
import socketserver
import threading
import time
import requests
# import shared library
# import 3rd party library

def httpserver(servername="localhost", port=8080, waittime=5):
    """ simple http server"""
    httphandler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer((servername, port), httphandler)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()
    time.sleep(waittime)
    return httpd

def httpserver_stop(httpd):
    """stop http server"""
    httpd.shutdown()
    return True

def localtest_funcs():
    """ local unit test for functs"""
    serins = httpserver()
    rresponse = requests.head(f"http://localhost:8080")
    if rresponse.status_code == 200:
        print(f"http simple server is runing now")
        serstatus = True
    else:
        serstatus = False
    time.sleep(5)
    result = httpserver_stop(serins)
    print(f"http server is stopped")
    time.sleep(5)
    return [serstatus, result]

def timediff_server(servername):
    """
    checking the script server and target server time diff
    this is only working when http server is running on remote
    used for domino windows control machine to unix server
    """
    url = f"http://{servername}"
    response = requests.get(url)
    ddate = response.headers['Date']
    dtime = datetime.datetime.strptime(ddate, '%a, %d %b %Y %H:%M:%S GMT')
    stime = datetime.datetime.utcnow()
    timediff = stime-dtime
    if timediff.days == 0:
        diffsecs = -timediff.seconds
    else:
        timediff = dtime-stime
        diffsecs = timediff.seconds
    print(f"There are {diffsecs} seconds between localmachine and remote server {servername}")
    returnvalue = (datetime.datetime.now()+timedelta(seconds=serverdiff)).isoformat().split('.')[0]
    return diffsecs



def localtest_classes():
    """ local unit test for classes"""
    pass

def main():
    """ main function for local usage"""
    pass

if __name__ == "__main__":
    main()
