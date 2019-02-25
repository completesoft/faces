import cv2
import requests
import asyncore
import socket
import logging
import time
import threading


DEBUG =  True

SocketServerHOST = '127.0.0.1'
SocketServerPORT = 9000


class Server(asyncore.dispatcher):
    def __init__(self, address):
        asyncore.dispatcher.__init__(self)
        self.logger = logging.getLogger('Server')
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(address)
        self.address = self.socket.getsockname()
        self.logger.debug('binding to %s', self.address)
        self.listen(5)
        self.client_pool = []

    def handle_accept(self):
        # Called when a client connects to our socket
        client_info = self.accept()
        if client_info is not None:
            self.logger.debug('handle_accept() -> %s', client_info[1])
            client = ClientHandler(client_info[0], self)
            self.client_pool.append(client)


class ClientHandler(asyncore.dispatcher):
    def __init__(self, sock, server):
        asyncore.dispatcher.__init__(self, sock)
        self.logger = logging.getLogger('Client ')
        self.server = server
        self.data_to_write = []

    def writable(self):
        return bool(self.data_to_write)

    def handle_write(self):
        print('Handle write')
        data = self.data_to_write.pop()
        if data:
            print('DATA', data)
            sent = self.send(data)
        self.logger.debug('handle_write() -> (%d) "%s"', sent, data[:sent].rstrip())

    def say_str(self, str):
        self.data_to_write.insert(0, str.encode("utf8"))

    def readable(self):
        return False

    def handle_read(self):
        data = self.recv(1024)
        self.logger.debug('handle_read() -> (%d) "%s"', len(data), data.rstrip())
        if not data:
            return

    def handle_close(self):
        self.logger.debug('handle_close()')
        print('client pool', self.server.client_pool)
        self.server.client_pool.remove(self)
        self.close()


class ServerThread(threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger('ServerTHREAD')
        self.daemon = True  # if thread is a daemon, it'll be killed when main program exits
        self.cliente = Server((host, port))
        self.start()

    def run(self):
        self.logger.debug('Starting server thread...')
        asyncore.loop(timeout=1)



logging.basicConfig(level=logging.DEBUG, format='%(name)s:[%(levelname)s]: %(message)s')

socket_server_thread = ServerThread(SocketServerHOST, SocketServerPORT)



url = 'rtsp://admin:iPQzvWpx32@gk-11.ddns.mksat.net:55554/Streaming/Channels/101'


while True:
    # video_capture = cv2.VideoCapture(url)
    # # Grab a single frame of video
    # ret, frame = video_capture.read()
    # video_capture.release()


    frame = cv2.imread('11-victims-2.jpg')
    ret = True

    if not ret:
        print('NO SIGNAL')
        continue

    # Resize frame of video to 1/2 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    # small_frame = cv2.resize(frame, (0, 0), fx=1, fy=1)
    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]



    img = cv2.imencode('.webp', rgb_small_frame)[1]
    print('Len encode', len(img))

    # send http request with image and receive response
    files = {'img': img}
    # data = {'x': str(x), 'y': str(y), 'z': str(z)}
    response = requests.post('http://localhost:8000/detector/detect/', files=files)
    recive_url = response.json()


    print('URL', recive_url)
    # Display the results

    # for kategory in coord.keys():
    #     for top, right, bottom, left in coord[kategory]:
    #         # Draw a box around the face
    #         font = cv2.FONT_HERSHEY_DUPLEX
    #         cv2.rectangle(small_frame, (left, top), (right, bottom), (150, 0, 155), 5)
    #         cv2.putText(small_frame, kategory, (left + 6, top-20), font, 1.0, (0, 204, 255), 2)

    # Display the resulting image

    # cv2.imshow('Video', small_frame)

    if recive_url['URL']:
        for client in socket_server_thread.cliente.client_pool:
            client.say_str('PNG '+recive_url['URL'])


    if DEBUG:
        time.sleep(10)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        # conn.close()
        break

cv2.destroyAllWindows()