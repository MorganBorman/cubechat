import traceback

from Signals import SignalObject, Signal

from CubeDataStream import CubeDataStream

SPECTATOR = object()
PLAYER = object()

ALIVE = object()
DEAD = object()
        
class VirtualClient(object):
    cn = -1
    role = SPECTATOR
    state = DEAD
    name = ""
    team = ""
    
    def __init__(self, cn):
        self.cn = cn

class ClientConnector(SignalObject):
    connected = Signal
    disconnected = Signal
    message = Signal
    
    client_connected = Signal
    client_updated = Signal
    client_disconnected = Signal
    
    def __init__(self, enet_host, initial_message_data, name):
        SignalObject.__init__(self)
        
        self.enet_host = enet_host
        
        self.enet_host.connected.connect(self.on_connected)
        self.enet_host.disconnected.connect(self.on_disconnected)
        self.enet_host.message.connect(self.on_message)
        
        self.peer = None
        self.name = name
        self.cn = -1
        self.sessionid = -1
        
        self.virtual_clients = {}
        
        self.on_message(1, initial_message_data)
        
    def vc_disconnected(self, cn):
        if cn in self.virtual_clients:
            del self.virtual_clients[cn]
            
        self.client_disconnected.emit(cn)
            
    def vc_get(self, cn):
        if not cn in self.virtual_clients:
            self.virtual_clients[cn] = VirtualClient(cn)
        return self.virtual_clients[cn]
            
    def vc_init(self, cn, name, team):
        vc = self.vc_get(cn)
        
        vc.name = name
        vc.team = team
        
        self.client_connected.emit(vc)
            
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
            
        self.enet_host.send(channel, CubeDataStream.pack_format(fmt, data_items), reliable)
        
    def on_connected(self):
        self.connected.emit()
        
    def on_disconnected(self):
        self.disconnected.emit()
        
    def on_message(self, channel, data):
        if len(data) <= 0:
            pass
        
        try:
            if channel == 0:
                try:
                    pass
                except:
                    traceback.print_exc()
                    
            elif channel == 1:
                messages = self.stream_spec.read(data, {})
                
                for message_type, message in messages:
                    self.process_message(message_type, message)
                    
            else: #channel == 2:
                pass
                
        except:
            traceback.print_exc()
            quit()
            
    def process_message(self, message_type, message):
        if self.is_init_message(message_type):
            self.process_init_message(message_type, message)
            self.send_connect()
            self.send_spectate()
        else:
            self.process_other_messages(message_type, message)
            
    def is_init_message(self, message_type):
        raise Exception("Not implemented.")
        
    def process_init_message(self, message_type, message):
        raise Exception("Not implemented.")
        
    def process_other_messages(self, message_type, message):
        raise Exception("Not implemented.")
            
    def send_connect(self):
        raise Exception("Not implemented.")
        
    def send_spectate(self):
        raise Exception("Not implemented.")
        
    def send_chat(self, text):
        raise Exception("Not implemented.")
        
    def send_teamchat(self, text):
        raise Exception("Not implemented.")
        
