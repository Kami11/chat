
import observer
from tornado.websocket import WebSocketHandler

from .struct import WSEndpoint


class WSHandlerFactory:


    def __new__(cls):


        class WSHandler(WebSocketHandler):

            newConnection = observer.Event()
            newData = observer.Event()
            droppedConnection = observer.Event()

            def open(self):
                self.newConnection.trigger(WSEndpoint(self))

            def on_message(self, message):
                self.newData.trigger(WSEndpoint(self), message)

            def on_close(self):
                self.droppedConnection.trigger(WSEndpoint(self))


        return WSHandler
