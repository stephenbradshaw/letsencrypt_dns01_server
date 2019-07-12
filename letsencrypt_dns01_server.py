#!/usr/bin/env python

import datetime
import sys
import time
import threading
import traceback
import SocketServer
import dnslib
from dnslib import *
import json


class DomainName(str):
    def __getattr__(self, item):
        return DomainName(item + '.' + self)


# Can change bind address of server here
BIND_HOST = '0.0.0.0'
BIND_PORT = 53

TTL = 30

bp = ''
if sys.path[0]:
    bp = sys.path[0] + os.sep

config_name= bp + 'config.json'

# records and associated filenames resolved by this server
my_records = json.load(open(config_name))


def dns_response(data):
    try:
        request = DNSRecord.parse(data)
    except:
        traceback.print_exc(file=sys.stderr)
        return None

    #print request

    reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)

    qname = request.q.qname
    qn = str(qname).lower()
    qtype = request.q.qtype
    qt = QTYPE[qtype]


    if qn in my_records.keys():
        r = [my_records[a] for a in my_records.keys() if a == qn][0]
        if r:
            try:
                if str(r[0]).startswith('file://'):
                    rdata = getattr(dnslib.dns, r[-1])(open(bp + r[0].lstrip('file://')).read().rstrip())
                else:
                    rdata = getattr(dnslib.dns, r[-1])(*r[:-1])
                reply.add_answer(RR(rname=qname, rtype=getattr(QTYPE, r[-1]), rclass=1, ttl=TTL, rdata=rdata))
                #print "---- Reply:\n", reply
            except Exception:
                traceback.print_exc(file=sys.stderr)
                return None

    return reply.pack()


class BaseRequestHandler(SocketServer.BaseRequestHandler):

    def get_data(self):
        raise NotImplementedError

    def send_data(self, data):
        raise NotImplementedError

    def handle(self):
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        #print "\n\n%s request %s (%s %s):" % (self.__class__.__name__[:3], now, self.client_address[0], self.client_address[1])
        try:
            data = self.get_data()
            #print len(data), data.encode('hex')  # repr(data).replace('\\x', '')[1:-1]
            resp = dns_response(data)
            if resp:
                self.send_data(resp)
        except Exception:
            traceback.print_exc(file=sys.stderr)


class TCPRequestHandler(BaseRequestHandler):

    def get_data(self):
        data = self.request.recv(8192).strip()
        sz = int(data[:2].encode('hex'), 16)
        if sz < len(data) - 2:
            raise Exception("Wrong size of TCP packet")
        elif sz > len(data) - 2:
            raise Exception("Too big TCP packet")
        return data[2:]

    def send_data(self, data):
        sz = hex(len(data))[2:].zfill(4).decode('hex')
        return self.request.sendall(sz + data)


class UDPRequestHandler(BaseRequestHandler):

    def get_data(self):
        return self.request[0].strip()

    def send_data(self, data):
        return self.request[1].sendto(data, self.client_address)


if __name__ == '__main__':
    print "Starting nameserver..."

    servers = [
        SocketServer.ThreadingUDPServer((BIND_HOST, BIND_PORT), UDPRequestHandler),
        SocketServer.ThreadingTCPServer((BIND_HOST, BIND_PORT), TCPRequestHandler),
    ]
    for s in servers:
        thread = threading.Thread(target=s.serve_forever)  # that thread will start one more thread for each request
        thread.daemon = True  # exit the server thread when the main thread terminates
        thread.start()
        print "%s server loop running in thread: %s" % (s.RequestHandlerClass.__name__[:3], thread.name)

    try:
        while 1:
            time.sleep(1)
            sys.stderr.flush()
            sys.stdout.flush()

    except KeyboardInterrupt:
        pass
    finally:
        for s in servers:
            s.shutdown()
