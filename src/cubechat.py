#!/usr/bin/env python

import string

import gtk
import pango
import gobject
import gtk.gdk

import client_connectors

from generic_client_connector import GenericClientConnector

colors = {0: "green", 1: "blue", 2: "yellow", 3: "red", 4: "grey", 5: "magenta", 6: "orange", 7: "white"}

class CubeChatApplication(object):
    def __init__(self):
        self.connectors = []
        
        client_connector = GenericClientConnector("psl.sauerleague.org", 10000, "unnamed")
        self.connectors.append(client_connector)
        
        client_connector.connected.connect(self.on_connector_connected)
        client_connector.message.connect(self.on_connector_message)
        client_connector.disconnected.connect(self.on_connector_disconnected)
        
        client_connector.client_connected.connect(self.on_connector_client_connected)
        client_connector.client_updated.connect(self.on_connector_client_updated)
        client_connector.client_disconnected.connect(self.on_connector_client_disconnected)
        
        self.setup_ui()
        gobject.timeout_add(10, self.update)
        
        self.color_tags = {}
        for ci in colors:
            self.color_tags[ci] = self.chatbuffer.create_tag(colors[ci], foreground=colors[ci])
        
        self.current_color = self.color_tags[7]
        self.saved_color = self.current_color
        
    def on_connector_connected(self):
        self.display("Connected.")
        
    def on_connector_message(self, text):
        self.display(text)
        
    def on_connector_disconnected(self):
        self.display("Disconnected.")
        
    def on_connector_client_connected(self, vc):
        self.clients_liststore.append([vc.cn, vc.name])
        
    def on_connector_client_updated(self, vc):
        iter = self.clients_liststore.get_iter_first()
        while iter is not None and self.clients_liststore.iter_is_valid(iter):
            if self.clients_liststore.get_value(iter, 0) == vc.cn: break
            iter = self.clients_liststore.iter_next(iter)
            
        if iter is not None and self.clients_liststore.iter_is_valid(iter):
            self.clients_liststore.set_value(iter, 1, repr(vc.name)[1:-1])
        else:
            self.clients_liststore.append([vc.cn, vc.name])
        
    def on_connector_client_disconnected(self, cn):
        iter = self.clients_liststore.get_iter_first()
        while iter is not None and self.clients_liststore.iter_is_valid(iter):
            if self.clients_liststore.get_value(iter, 0) == cn: break
            iter = self.clients_liststore.iter_next(iter)
            
        if iter is not None and self.clients_liststore.iter_is_valid(iter):
            self.clients_liststore.remove(iter)
        
    def setup_ui(self):
        builder = gtk.Builder()
        builder.add_from_file("cubechat.glade")
        builder.connect_signals(self)
        builder.get_object("cubechat_window").show()
        
        self.chatbuffer = builder.get_object("chat_textbuffer")
        self.chatview = builder.get_object("chat_textview")
        
        self.clients_liststore = builder.get_object("clients_liststore")
        
        self.chatview.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse('#333333'))
         
    def display(self, text):
        sections = text.split("\x0c")

        for si in xrange(len(sections)):
            if si != 0:
                color_select = sections[si][0]
                if color_select == 's':
                    self.saved_color = self.current_color
                elif color_select == 'r':
                    self.current_color = self.saved_color
                elif color_select in string.digits:
                    self.current_color = self.color_tags[int(color_select)]
                text = sections[si][1:]
            else:
                text = sections[si]
            self._display(repr(text)[1:-1])
            
        self.chatbuffer.insert(self.chatbuffer.get_end_iter(), "\n")
        self.chatview.scroll_to_iter(self.chatbuffer.get_end_iter(), 0)
        
        self.current_color = self.color_tags[7]
        self.saved_color = self.current_color
            
    def _display(self, text):
        self.chatbuffer.insert(self.chatbuffer.get_end_iter(), text)
        
        iter = self.chatbuffer.get_end_iter()
        iter.backward_chars(len(text))
        
        self.chatbuffer.apply_tag(self.current_color, self.chatbuffer.get_end_iter(), iter)
    
    def update(self, *args):
        for connector in self.connectors:
            connector.service()
        return True
        
    def on_chat_input_key_press_event(self, widget, event):
        if gtk.gdk.keyval_name(event.keyval) == "Return":
            text = widget.get_text()
            widget.set_text("")
            for connector in self.connectors:
                connector.send_chat(text)
                self.display("<me>: {}".format(text))
            
    def gtk_main_quit(self, widget):
        for connector in self.connectors:
            connector.disconnect()
        gtk.main_quit()
        
    def on_server_connect_menuitem_activate(self, widget):
        print "Connect clicked!"
        
    def on_server_disconnect_menuitem_activate(self, widget):
        for connector in self.connectors:
            connector.disconnect()
        
app = CubeChatApplication()
gtk.main()

