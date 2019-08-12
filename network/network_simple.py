"""
this library is use basic library to simulate simple Server
"""
__all__ = ["httpserver", "httpserver_stop"]

# import default system library
import http.server
import socketserver
import threading
import time, socket
import requests
# import shared library
# import 3rd party library
from itertools import groupby
import collections    
import nmap

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


def dns_get_ipv4(filename):
    """ get ip v4 address from the file"""
    with open(filename,'r') as filehandle:
        fc = filehandle.read()
    content = [entry for entry in fc.splitlines() if entry != ""]
    
    ipv4h = []
    ipv4a = []    
    
    for entry in content:
        entrys = entry.split()
        if len(entrys) == 5:
            dnse = {}
            dnse['name'] = entrys[0].strip()
            dnse['ip'] =  entrys[3].strip()
            dnse['type'] = entrys[2].strip()
            if dnse['type'] == "(A)":
                ipv4h.append(dnse)             
            elif dnse['type'] == "(CNAME)":
                try:
                    dnse['ip'] = socket.gethostbyname(dnse['ip'])
                    ipv4h.append(dnse)
                except:
                    ipv4a.append(dnse)
            else: 
                ipv4a.append(dnse)
    return ipv4h

def dns_split_subnet(ips, subnetfilter=None, nmapstate=False):
    """ split ips based on subnets"""
    subnets = {}
    subnetlist = sorted(set(map(lambda x: ".".join(x['ip'].split('.')[0:3]),ips)))
    count = 0
    for key,group in groupby(ips,lambda x: ".".join(x['ip'].split('.')[0:3])):
#    listofsubnet =    [entry['ip']    for entry in group]
#    print "subnet %s have %s entries" % (key,len(listofsubnet))
        for thing in group:
            count +=1
    print("there are total %s ipv4 addresses" % count)

    for entry in ips:
        ips = entry['ip'].split('.')
        subnet = ".".join(ips[0:3])
        entry['subnet'] = subnet
        entry['address'] = ips[-1]

        if subnet in subnets.keys():
            subnets[subnet].append(entry)
        else:
            subnets[subnet]    =    []
            subnets[subnet].append(entry)
    
    if subnetfilter is None:
        subnetfilter = subnets.keys()

    for key_ in subnetfilter:
        existinglist = []
        for entry in subnets[key_]:
            if entry['address'] not in existinglist:
                existinglist.append(int(entry['address']))
        leftaddress = sorted(list(set(range(1,254))-set(existinglist)))
        print("total address found in subnet %s is %s" % (key_,len(subnets[key_])))
        print("total left address is %s\n%s" % (len(leftaddress), leftaddress))
        ladlist = ["%s.%s" % (key_,entry) for entry in leftaddress]
        if nmapstate:
            print(f'checking subnet {key_} free address with nmap, will take long time')
            n=nmap.PortScanner()
            nr=n.scan(hosts=" ".join(ladlist))
            print ("nmap scan result is \n%s" % nr['nmap']['scanstats'])
            nupmachine    =    nr['scan'].keys()
            amachine    =    list(set(ladlist)-set(nupmachine))
            print (" Avaialble ip in subnet %s are %s:\n %s" % (key_,len(amachine),amachine))
        

def dns_export_analyst(filename, subnetfilter=None, nmapstate=False):
    """ read dns export result and provide analyst result"""
    ipv4 = dns_get_ipv4(filename)
    dns_split_subnet(ipv4,
                     subnetfilter=subnetfilter,
                     nmapstate=nmapstate)

def localtest_classes():
    """ local unit test for classes"""
    pass

def main():
    """ main function for local usage"""
    pass

if __name__ == "__main__":
    main()
    
"""

filename = r"C:\Users\qlu\Downloads\logs\devemc_20190617.txt"
from base0.network.network_simple import dns_export_analyst

dns_export_analyst(filename)

"""
