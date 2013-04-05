from CubeDataStream import CubeDataStream

import get_client_connector

from ...base import *
from .constants import message_types
from .stream_spec import stream_spec

class ElaraConnector(ClientConnector):
    gamemode = 0

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
                messages = self.stream_spec.read(data, {}, {'gamemode': self.gamemode})
                #print "#"*100
                
                for message_type, message in messages:
                    self.process_message(message_type, message)
                    
            else: #channel == 2:
                pass
                
        except:
            traceback.print_exc()
            quit()

    def is_init_message(self, message_type):
        return message_type=="N_SERVERINIT"
        
    def process_init_message(self, message_type, message):
        self.cn = message['clientnum']
        self.sessionid = message['sessionid']
        self.serverhaspwd = bool(message['haspwd'])
        self.serverdescription = message['hostname']
        
    def process_other_messages(self, message_type, message):
        #if message_type not in ["N_CLIENTPING", "N_TIMEUP"]:
        #    print message_type, message
            
        if message_type == "N_SPAWNSTATE" and message['clientnum'] == self.cn:
            self.send_spectate()
        elif message_type == "N_WELCOME":
            self.client_updated.emit(self)
        elif message_type == "N_MAPCHANGE":
            self.gamemode = message['gamemode']
        elif message_type == "N_DISCONNECT":
            self.vc_disconnected(message['clientnum'])
        elif message_type in ("N_CLIENTINIT", "N_INITAI"):
            vc = self.vc_get(message['clientnum'])
            vc.name = message['name']
            vc.team = message['team']
            self.client_updated.emit(vc)
        elif message_type == "N_TEXT":
            vc = self.vc_get(message['clientnum'])
            self.message.emit("{}({}): {}".format(vc.name, vc.cn, message['message']))
        elif message_type == "N_SERVMSG":
            self.message.emit("<server>: {}".format(message['message']))
            
    def send_connect(self):
        self.sendf(1, 'isiisss', [message_types.N_CONNECT, self.name, 0, 0, "", "", ""], True)
        
    def send_spectate(self):
        self.sendf(1, 'iii', [message_types.N_SPECTATOR, self.cn, 1], True)
        
    def send_chat(self, text):
        self.sendf(1, 'iiis', [message_types.N_TEXT, self.cn, 0, text], True)
        
    def send_teamchat(self, text):
        self.sendf(1, 'iiis', [message_types.N_TEXT, self.cn, 2, text], True)
        
ElaraConnector.stream_spec = stream_spec

get_client_connector.client_connectors[220] = ElaraConnector
