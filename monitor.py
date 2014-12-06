#!/bin/python
# -*- coding: utf-8 -*-
# vim:set ts=8 sts=8 sw=8 tw=80 noet cc=80:

import json
from messaging import open_connection, ROUTING_KEYS

if __name__ == "__main__":
	connection, exchange = open_connection()
	channel = connection.channel()
	channel.exchange_declare(exchange=exchange, type="direct")

	def receive(ch, method, properties, body):
		routing_key = method.routing_key
		data = json.loads(body.decode('utf-8'))
		print("[<=] [%s] %s" % (routing_key, data))

	result = channel.queue_declare(exclusive=True)
	queue_name = result.method.queue
	for routing_key in ROUTING_KEYS:
		channel.queue_bind(exchange=exchange, queue=queue_name,
				routing_key=routing_key)

	channel.basic_consume(receive, queue=queue_name, no_ack=True)

	try:
		channel.start_consuming()
	except KeyboardInterrupt: pass

	connection.close()
