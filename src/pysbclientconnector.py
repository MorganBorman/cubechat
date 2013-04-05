import enet #@UnresolvedImport

import traceback

from Signals import SignalObject, Signal

from ClientReadStreamSpec import sauerbraten_stream_spec

from CubeDataStream import CubeDataStream

from Constants import * #@UnusedWildImport

class ProtocolVersionMismatchError(Exception):
    '''Protocol versions do not match'''
    def __init__(self, value=''):
        Exception.__init__(self, value)
        
class VirtualClientState(object):
    state = client_states.CS_ALIVE
    
    def __init__(self):
        pass
        
class VirtualClient(object):
    state = None
    
    def __init__(self):
        self.state = VirtualClientState()

class ClientConnector(SignalObject):
    def __init__(self, host, port, name):
        SignalObject.__init__(self)
        
        address = enet.Address(host, port)
        self._enet_client_host = enet.Host(None, 2, 3, 0, 0)
        self._enet_client_host.connect(address, 3, 0)
        self._enet_client_host.flush()
        
        self.connected = False
        self.failed = False
        
        self.peer = None
        self.name = name
        self.cn = -1
        self.sessionid = -1
        
        self.virtual_clients = {}
    
    def service_host(self):
        try:
            event = self._enet_client_host.service(5)
        except KeyboardInterrupt:
            raise
        
        if event.type == enet.EVENT_TYPE_CONNECT:
            print("%s: CONNECT" % event.peer.address)
            self.connected = True
            self.peer = event.peer
            self.failed = False
            
        elif event.type == enet.EVENT_TYPE_DISCONNECT:
            print("%s: DISCONNECT" % event.peer.address)
            self.connected = False
            self.peer = None
            self.failed = False
                
        elif event.type == enet.EVENT_TYPE_RECEIVE:
            self.on_receive_event(event.channelID, event.packet.data)
    
    def update(self):
        self.service_host()
        
    def send(self, channel, data, reliable=False):
        if self.peer is None or self.failed:
            return
        
        if reliable:
            flags = enet.PACKET_FLAG_RELIABLE
        else:
            flags = 0
            
        #print "Sending: '%s' to client cn: %d" %(repr(str(data)), self.cn)
        
        packet = enet.Packet(str(data), flags)
        status = self.peer.send(channel, packet)
        if status < 0:
            print("%s: Error sending packet!" % self.peer.address)
            self.failed = True
            
    def sendf(self, channel, fmt, data_items, reliable=False):
        fmt = list(fmt)
        
        try:
            ic = fmt.index('c')
            while ic >= 0:
                fmt[ic] = 'i'
                data_items[ic] = data_items[ic].cn
                ic = fmt.index('c')
        except ValueError:
            pass
            
        self.send(channel, CubeDataStream.pack_format(fmt, data_items), reliable)
        
    def on_receive_event(self, channel, data):
        if len(data) <= 0:
            pass
        
        try:
            if channel == 0:
                try:
                    #cds = CubeDataStream(data)
                    #message_type = cds.getint()
                    #cn = cds.getint()
                    #self.getclient(cn).state.position = data
                    pass
                except:
                    traceback.print_exc()
            elif channel == 1:
                messages = sauerbraten_stream_spec.read(data, {})
                
                for message_type, message in messages:
                    
                    if message_type == "N_SERVINFO":
                        if message['protocol_version'] != PROTOCOL_VERSION:
                            ProtocolVersionMismatchError("The server is using a different protocol. You: %d Server: %d" % (PROTOCOL_VERSION, message['protocol_version']))
                        self.cn = message['clientnum']
                        self.sessionid = message['sessionid']
                        self.serverhaspwd = bool(message['haspwd'])
                        self.serverdescription = message['description']
                        self.send_connect()
                        self.send_spectate()
                    elif message_type == "N_SPAWNSTATE" and message['clientnum'] == self.cn:
                        self.send_spectate()
                    elif message_type == "N_CLIENTPING":
                        pass
                    else:
                        print message_type, message
                    
            else: #channel == 2:
                pass
        except ProtocolVersionMismatchError:
            traceback.print_exc()
            quit()
        except:
            traceback.print_exc()
            quit()
            
    def send_connect(self):
        self.sendf(1, 'issi', [message_types.N_CONNECT, self.name, "", 0], True)
        
    def send_spectate(self):
        self.sendf(1, 'iii', [message_types.N_SPECTATOR, self.cn, 1], True)
        
                    
client_connector = ClientConnector("forgottendream.org", 28785, "cxsbs_streamer")

while True:
    client_connector.update()