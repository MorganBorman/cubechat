import enet #@UnresolvedImport

from Signals import SignalObject, Signal

class EnetHost(SignalObject):
    connected = Signal
    disconnected = Signal
    message = Signal
    
    peer = None
    
    def __init__(self, host, port):
        SignalObject.__init__(self)
        
        address = enet.Address(host, port)
        self._enet_client_host = enet.Host(None, 2, 3, 0, 0)
        self._enet_client_host.connect(address, 3, 0)
        self._enet_client_host.flush()
        
    def disconnect(self):
        if self.peer is not None:
            self.peer.disconnect()
        
    def service(self):
        event = self._enet_client_host.service(5)
        
        if event.type == enet.EVENT_TYPE_CONNECT:
            self.is_connected = True
            self.peer = event.peer
            self.failed = False
            self.connected.emit()
            
        elif event.type == enet.EVENT_TYPE_DISCONNECT:
            self.is_connected = False
            self.peer = None
            self.failed = False
            self.disconnected.emit()
                
        elif event.type == enet.EVENT_TYPE_RECEIVE:
            self.message.emit(event.channelID, event.packet.data)
            
    def send(self, channel, data, reliable=False):
        if self.peer is None or self.failed:
            return
        
        if reliable:
            flags = enet.PACKET_FLAG_RELIABLE
        else:
            flags = 0
        
        packet = enet.Packet(str(data), flags)
        status = self.peer.send(channel, packet)
        if status < 0:
            print("%s: Error sending packet!" % self.peer.address)
            self.failed = True

