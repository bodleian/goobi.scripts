# -*- coding: utf-8 -*-

import logging
logging.basicConfig(level=logging.INFO)

import pika, pika.exceptions, pika.credentials

class Queue(object):

	def __init__( self, host, port, virtual_host=None, username=None, password=None ):
	
		if host is None:
			import config
			
			host = config.host
			port = config.port
			
			virtual_host = config.virtual_host
			username = config.username
			password = config.password
	
		# Connect to RabbitMQ
		self.channel = None
		
		logger = logging.getLogger('pika')
		logger.setLevel(logging.INFO)
		
		
		try:
			if username:
				credentials = pika.credentials.PlainCredentials( username, password )
				self.connection = pika.BlockingConnection( pika.ConnectionParameters( host, int(port), virtual_host, credentials ) )
			else:
				self.connection = pika.BlockingConnection( pika.ConnectionParameters( host, int(port), virtual_host ) )
		except	pika.exceptions.AMQPConnectionError:
			self.connection = None
		else:
			self.channel = self.connection.channel( )
			self.channel.basic_qos( prefetch_count=1 ) # Set rabbitMQ to only send one message at a time to workers. (When a worker is doing nothiong, send a message)
			
			self.channel.confirm_delivery() # Confirm our messages!
			
		self.consuming = False
		
		
	
	def connected( self ):
		return self.connection != None
	
	def send_message( self, message, content_type = 'text/json', try_repeat=1 ):
	
		response = None
		
		if self.channel:
			for tries in range( try_repeat ):
				
				response = self.channel.basic_publish(  exchange='', 
						routing_key=self.queue_name, 
						body=message,
						properties=pika.BasicProperties(
							content_type=content_type,
							delivery_mode = 2, # make message persistent
						),
						mandatory=True )

				if response:
					return True
				
			
			if not response:
				print "ERORRROROROR - Message not confirmed!!!!!!!"
			
		return False
	
	def start_consuming( self, consumer ) :
	
		if self.channel:
			self.channel.basic_consume(consumer,  queue=self.queue_name, no_ack=False )
		
			self.consuming = True
			self.channel.start_consuming( )
	
	def stop_consuming( self ) :
		if self.consuming :
			self.channel.stop_consuming( )	
			self.consuming = False
			
	def return_callback( self, callback ) :
		if self.channel :
			self.channel.add_on_return_callback( callback )
			
	def close( self ):
		if self.connection:
			self.connection.close( )
