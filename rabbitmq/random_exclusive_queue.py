# -*- coding: utf-8 -*-

import pika

from queue import Queue

class RandomExclusiveQueue( Queue ):

	def __init__( self, host=None, port=None, virtual_host=None, username=None, password=None, name=None ) :
	
		super(RandomExclusiveQueue, self).__init__( host, port, virtual_host, username, password )
		
		self.queue_name = None
		if name == None:
			if self.channel:
				# Create a name
				result = self.channel.queue_declare( exclusive=True, durable=True )
				self.queue_name = result.method.queue
		else:
			self.queue_name = name

	def get_queue( self ):
		return self.queue_name

if __name__ == '__main__' :
	
	# Run a quick test
	import logging
	logging.basicConfig()
	
	import sys
	
	# 1st
	queue = RandomExclusiveQueue()
	
	# 2nd
	message = "This is a test message"
	if queue.send_message( message ) :
		print ' Message sent: "%r"' % ( message, )
	else:
		print ' Message NOT sent: "%r"' % ( message, )
	
	def callback( ch, method, properties, body ):
		# 4th
	    print ' Message received: "%r"' % ( body, )
	    
	    ch.basic_ack( delivery_tag = method.delivery_tag ) # Say completed.
	    sys.exit( )
	
	# 3rd
	print ' Looking for message.'
	queue.start_consuming( callback )
	
