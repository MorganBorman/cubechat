from CubeDataStream import CubeDataStream

import get_client_connector

from ...base import *
from .constants import message_types, AC_VERSION, CR_DEFAULT, teams
from .stream_spec import stream_spec

class v1_1_0_4Connector(ClientConnector):
    def is_init_message(self, message_type):
        return message_type=="SV_SERVINFO"
        
    def process_init_message(self, message_type, message):
        self.cn = message['clientnum']
        self.sessionid = message['sessionid']
        self.serverhaspwd = bool(message['haspwd'])
        self.serverdescription = ""
        
    def process_other_messages(self, message_type, message):
        #if message_type != "N_CLIENTPING":
        #    print message_type, message
        
        if message_type == "SV_SPAWNSTATE":
            self.send_spectate()
        elif message_type == "SV_WELCOME":
            self.client_updated.emit(self)
        elif message_type == "SV_CDIS":
            self.vc_disconnected(message['clientnum'])
        elif message_type == "SV_INITCLIENT":
            self.vc_init(message['clientnum'], message['name'], message['team'])
        elif message_type == "SV_SWITCHNAME":
            vc = self.vc_get(message['clientnum'])
            vc.name = message['name']
            self.client_updated(vc)
        elif message_type in ("SV_TEXT", "SV_TEXTME"):
            if 'clientnum' in message:
                vc = self.vc_get(message['clientnum'])
                self.message.emit("{}({}): {}".format(vc.name, vc.cn, message['text']))
            else:
                self.message.emit("<motd>: {}".format(message['text']))
        elif message_type == "SV_SERVMSG":
            self.message.emit("<server>: {}".format(message['text']))
            
    def send_connect(self):
        self.sendf(1, 'iiisssiiii', [message_types.SV_CONNECT, AC_VERSION, 0, self.name, "", "en", CR_DEFAULT, 0, 0, 0], True)
        
    def send_spectate(self):
        self.sendf(1, 'ii', [message_types.SV_SWITCHTEAM, teams.TEAM_SPECT], True)
        
    def send_chat(self, text):
        self.sendf(1, 'is', [message_types.SV_TEXT, text], True)
        
    def send_teamchat(self, text):
        #self.sendf(1, 'is', [message_types.SV_SAYTEAM, text], True)
        pass
        
v1_1_0_4Connector.stream_spec = stream_spec

get_client_connector.client_connectors[1132] = v1_1_0_4Connector
