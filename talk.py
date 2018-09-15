#!/bin/python
# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import sys
import json
from messaging import open_connection, ROUTING_KEY_SENDMUC

if __name__ == "__main__":
	connection, exchange = open_connection()
	channel = connection.channel()
	channel.exchange_declare(exchange=exchange, exchange_type="direct")

	result = channel.queue_declare(exclusive=True)
	queue_name = result.method.queue
	channel.queue_bind(exchange=exchange, queue=queue_name,
			routing_key=ROUTING_KEY_SENDMUC)

	def send(key, data):
		channel.basic_publish(exchange=exchange,
				routing_key=key,
				body=json.dumps(data).encode('utf-8'))

	def send_muc(msg):
		send(ROUTING_KEY_SENDMUC, msg)

	try:
		while True:
			sys.stdout.write('> ')
			sys.stdout.flush()
			line = sys.stdin.readline()
			if not line:
				break
			msg = line.strip()
			if len(msg) == 0:
				continue
			send_muc(msg)
	except KeyboardInterrupt: pass

	connection.close()
