# -*- coding: utf-8 -*-

import os
import logging
import redis
import asyncio
from flask import Flask, render_template
from flask_sockets import Sockets
from rq import Queue
from worker import conn
from worker_tasks import print_time

REDISCLOUD_URL = os.environ['REDISCLOUD_URL']
REDIS_CHAN = 'chat'

app = Flask(__name__)
app.debug = 'DEBUG' in os.environ
q = Queue(connection=conn)

sockets = Sockets(app)
redis = redis.from_url(REDISCLOUD_URL)



class ChatBackend(object):
    """Interface for registering and updating WebSocket clients."""

    def __init__(self):
        self.clients = list()
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(REDIS_CHAN)

    def __iter_data(self):
        for message in self.pubsub.listen():
            data = message.get('data')
            if message['type'] == 'message':
                app.logger.info(u'Sending message: {}'.format(data))
                yield data

    def register(self, client):
        """Register a WebSocket connection for Redis updates."""
        self.clients.append(client)

    def send(self, client, data):
        """Send given data to the registered client.
        Automatically discards invalid connections."""
        try:
            client.send(data)
        except Exception:
            self.clients.remove(client)

    def run(self):
        """Listens for new messages in Redis, and sends them to clients."""
        for data in self.__iter_data():
            for client in self.clients:
                self.send(client, data)

    def start(self):
        """Maintains Redis subscription in the background."""
        loop = asyncio.get_event_loop()
        loop.run_forever(self.run)
        loop.close()
        

chats = ChatBackend()
chats.start()

@app.route('/')
def hello():
    q.enqueue(print_time)
    return render_template('index.html')

@sockets.route('/submit')
def inbox(ws):
    """Receives incoming chat messages, inserts them into Redis."""
    while not ws.closed:
        message = ws.receive()
        if message:
            app.logger.info(u'Inserting message: {}'.format(message))
            redis.publish(REDIS_CHAN, message)

@sockets.route('/receive')
def outbox(ws):
    """Sends outgoing chat messages, via `ChatBackend`."""
    chats.register(ws)