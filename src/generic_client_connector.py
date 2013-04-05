from get_client_connector import get_client_connector

from enet_host import EnetHost

from Signals import SignalObject, Signal

class GenericClientConnector(SignalObject):
    connected = Signal
    disconnected = Signal
    message = Signal
    
    client_connected = Signal
    client_updated = Signal
    client_disconnected = Signal
    
    specific_connector = None
    
    def __init__(self, host, port, name):
        SignalObject.__init__(self)
        
        self.name = name
        
        self.enet_host = EnetHost(host, port)
        
        self.enet_host.connected.connect(self.on_connected)
        self.enet_host.disconnected.connect(self.on_disconnected)
        self.enet_host.message.connect(self.on_message)
        
    def disconnect(self):
        self.enet_host.disconnect()
    
    def service(self):
        self.enet_host.service()
        
    def on_connected(self):
        self.connected.emit()
        
    def on_disconnected(self):
        self.disconnected.emit()
        
    def on_connector_message(self, text):
        self.message.emit(text)
        
    def on_connector_client_connected(self, vc):
        self.client_connected.emit(vc)
        
    def on_connector_client_updated(self, vc):
        self.client_updated.emit(vc)
        
    def on_connector_client_disconnected(self, cn):
        self.client_disconnected.emit(cn)
        
    def on_message(self, channel, data):
        if self.specific_connector is None:
            if channel == 1:
                connector_class = get_client_connector(data)
                if connector_class is not None:
                    print "Got specific connector class:", connector_class
                
                    self.enet_host.disconnect_all_instance_signals(self)
                    self.specific_connector = connector_class(self.enet_host, data, self.name)
                    
                    self.specific_connector.message.connect(self.on_connector_message)
                    self.specific_connector.connected.connect(self.on_connected)
                    self.specific_connector.connected.disconnect(self.on_disconnected)
                    
                    self.specific_connector.client_connected.connect(self.on_connector_client_connected)
                    self.specific_connector.client_updated.connect(self.on_connector_client_updated)
                    self.specific_connector.client_disconnected.connect(self.on_connector_client_disconnected)
                    
    def send_chat(self, text):
        if self.specific_connector is not None:
            self.specific_connector.send_chat(text)
        
    def send_teamchat(self, text):
        if self.specific_connector is not None:
            self.specific_connector.send_teamchat(text)
            
            
