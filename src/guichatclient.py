from Tkinter import *

import client_connectors

from generic_client_connector import GenericClientConnector

class GuiChatClient(object):
    def __init__(self, tk_root):
        self.connectors = []
        
        client_connector = GenericClientConnector("psl.sauerleague.org", 10000, "unnamed")
        self.connectors.append(client_connector)
        
        client_connector.connected.connect(self.on_connector_connected)
        client_connector.message.connect(self.on_connector_message)
        client_connector.disconnected.connect(self.on_connector_disconnected)
        
        self.tk_root = tk_root
        self.setup_widgets()
        self.tk_root.title('Sauerbraten chat client')
        self.tk_root.after(12, self.update)
        
    def on_connector_connected(self):
        self.display("Connected.")
        
    def on_connector_message(self, text):
        self.display(text)
        
    def on_connector_disconnected(self):
        self.display("Disconnected.")
        
    def setup_widgets(self):
        # put an entry widget at the bottom to type into
        self.tk_entry = Entry(self.tk_root)
        self.tk_entry.pack(side=BOTTOM, fill=X)
        
        def get(event):
            text = event.widget.get()
            for connector in self.connectors:
                connector.send_chat(text)
                self.display("<me>: {}".format(text))
            event.widget.delete(0, END)
            
        self.tk_entry.bind('<Return>', get)
        
        self.tk_frame=Frame(self.tk_root)
        self.tk_frame.pack(fill=BOTH, expand=1)
        
        #define a new frame and put a text area in it
        self.tk_textfr=Frame(self.tk_frame)
        self.tk_text=Text(self.tk_textfr, background='white')
        
        # put a scroll bar in the frame
        self.tk_scroll=Scrollbar(self.tk_textfr)
        self.tk_text.configure(yscrollcommand=self.tk_scroll.set)
        
        #pack everything
        self.tk_text.pack(side=LEFT, fill=BOTH)
        self.tk_scroll.pack(side=RIGHT, fill=Y)
        self.tk_textfr.pack(side=TOP, fill=BOTH, expand=1)
            
    def display(self, text):
        self.tk_text.insert(END, text)
        self.tk_text.insert(END, "\n")
        self.tk_text.see(END)
    
    def update(self):
        for connector in self.connectors:
            connector.service()
        self.tk_root.after(12, self.update)
        
        
tk_root = Tk()
gui_chat_client = GuiChatClient(tk_root)
tk_root.mainloop()

