from CubeDataStream import CubeDataStream

import get_client_connector

from ...base import *
from .constants import message_types
from .stream_spec import stream_spec

class CollectConnector(ClientConnector):
    def is_init_message(self, message_type):
        return message_type=="N_SERVINFO"
        
    def process_init_message(self, message_type, message):
        self.cn = message['clientnum']
        self.sessionid = message['sessionid']
        self.serverhaspwd = bool(message['haspwd'])
        self.serverdescription = message['description']
        
    def process_other_messages(self, message_type, message):
        #if message_type not in ["N_CLIENTPING", "N_TIMEUP"]:
        #    print message_type, message
            
        if message_type == "N_SPAWNSTATE" and message['clientnum'] == self.cn:
            self.send_spectate()
        elif message_type == "N_WELCOME":
            self.client_updated.emit(self)
        elif message_type == "N_CDIS":
            self.vc_disconnected(message['clientnum'])
        elif message_type == "N_INITCLIENT":
            self.vc_init(message['clientnum'], message['name'], message['team'])
        elif message_type == "N_SWITCHNAME":
            vc = self.vc_get(message['clientnum'])
            vc.name = message['name']
            self.client_updated.emit(vc)
        elif message_type == "N_TEXT":
            vc = self.vc_get(message['clientnum'])
            self.message.emit("{}({}): {}".format(vc.name, vc.cn, message['text']))
        elif message_type == "N_SERVMSG":
            self.message.emit("<server>: {}".format(message['text']))
            
    def send_connect(self):
        self.sendf(1, 'issi', [message_types.N_CONNECT, self.name, "", 0], True)
        
    def send_spectate(self):
        self.sendf(1, 'iii', [message_types.N_SPECTATOR, self.cn, 1], True)
        
    def send_chat(self, text):
        self.sendf(1, 'is', [message_types.N_TEXT, text], True)
        
    def send_teamchat(self, text):
        self.sendf(1, 'is', [message_types.N_SAYTEAM, text], True)
        
CollectConnector.stream_spec = stream_spec

get_client_connector.client_connectors[259] = CollectConnector
