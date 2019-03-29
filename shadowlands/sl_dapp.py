from abc import ABC, abstractmethod
from asciimatics.widgets import (
    Frame, ListBox, Layout, Divider, Text, Button, Label, FileBrowser, RadioButtons, CheckBox, QRCode
)
from asciimatics.exceptions import NextScene
from asciimatics.event import KeyboardEvent, MouseEvent
from asciimatics.scene import Scene
from asciimatics.effects import Effect
from shadowlands.credstick import SignTxError
from shadowlands.tui.effects.transaction_frame import TransactionFrame
from shadowlands.tui.effects.message_dialog import MessageDialog
from decimal import Decimal
import pyperclip

from shadowlands.tui.debug import debug, end_debug

from shadowlands.sl_frame import SLFrame, SLWaitFrame, AskClipboardFrame

from shadowlands.sl_transaction_frame import SLTransactionFrame, SLTransactionWaitFrame

import pdb

class SLDapp():
    def __init__(self, screen, scene, eth_node, config, price_poller, destroy_window=None):
        self._screen = screen
        self._scene = scene
        self._node = eth_node
        self._config = config
        self._price_poller = price_poller
        self.initialize()

        if destroy_window is not None:
            destroy_window.close()

    @property
    def node(self):
        return self._node

    @property
    def config(self):
        return self._config
        
    @property
    def price_poller(self):
        return self._price_poller

    @abstractmethod
    def initialize(self):
        pass

    # cls is a custom subclass of SLFrame
    def add_frame(self, cls, height=None, width=None, title=None, **kwargs):
        # we are adding SLFrame effects.  asciimatics can do a lot more
        # than this, but we're hiding away the functionality for the 
        # sake of simplicity.
        frame = cls(self, height, width, title=title, **kwargs)
        self._scene.add_effect(frame)
        return frame 

    def show_wait_frame(self, message="Please wait a moment..."):
        preferred_width= len(message) + 6
        self.waitframe = SLWaitFrame(self, message, 3, preferred_width)
        self._scene.add_effect( self.waitframe ) 

    def hide_wait_frame(self):
        try:
            self._scene.remove_effect( self.waitframe ) 
        except:
            # We need to be able to call this method without consequence
            pass


    def add_message_dialog(self, message, **kwargs):
        preferred_width= len(message) + 6
        self._scene.add_effect( MessageDialog(self._screen, message, width=preferred_width, **kwargs))

    def add_transaction_dialog(self, tx_fn, title="Sign & Send Transaction", tx_value=0, destroy_window=None, gas_limit=None, **kwargs):
        self._scene.add_effect( 
            SLTransactionFrame(self, 16, 59, tx_fn, destroy_window=destroy_window, title=title, gas_limit=gas_limit, tx_value=tx_value, **kwargs) 
        )

    def add_transaction_wait_dialog(self, tx_fn, wait_message, title="Sign & Send Transaction", tx_value=0, destroy_window=None, gas_limit=None, receipt_proc=None, **kwargs):
        self._scene.add_effect( 
            SLTransactionWaitFrame(self, 16, 59, wait_message, tx_fn=tx_fn, gas_limit=gas_limit, receipt_proc=receipt_proc, **kwargs) 
        )


    def quit(self):
        # Remove all owned windows
        self._scene.remove_effect(self)
        raise NextScene(self._scene.name)

    def _update():
        pass
    def reset():
        pass
    def stop_frame():
        pass

    


class ExitDapp(Exception):
    pass

class RunDapp(Exception):
    pass
