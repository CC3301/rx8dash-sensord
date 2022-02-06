import socket
import logging
import threading
import time


class Connection:
    def __init__(self, bind_addr, bind_port, sensors):
        self.logger = logging.getLogger(__name__)
        self.bind_addr = bind_addr
        self.bind_port = bind_port
        # self.send_q = send_q
        self.sensors = sensors
        self.t = threading.Thread(target=self._serve, name=self.__class__.__name__)
        self.socket = None
        self.__keep_running = False

    def start(self):
        self.__keep_running = True
        self.__bind()
        self.socket.listen(5)
        self.t.start()

    def stop(self):
        self.__keep_running = False
        self.__disconnect()
        self.t.join()

    def __bind(self):
        if self.socket:
            self.logger.warning("Already connected")
        else:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((self.bind_addr, int(self.bind_port)))

    def __disconnect(self):
        self.socket.shutdown(1)

    def _serve(self):
        self.logger.info("sensord is waiting for connections")
        while self.__keep_running:
            (clientsocket, address) = self.socket.accept()
            self.logger.debug("Serving connection")
            connected = True
            while connected:
                data = self.sensors.fetch()
                if data is None:
                    continue
                else:
                    try:
                        data += b"0" * (1024 - len(data))
                        clientsocket.sendall(data)
                    except Exception as e:
                        self.logger.debug(f"Connection closed by client ({e})")
                        connected = False
