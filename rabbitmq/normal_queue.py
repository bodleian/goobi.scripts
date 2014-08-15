# -*- coding: utf-8 -*-


from queue import Queue

class NormalQueue(Queue):

	def __init__( self, queue_name, host=None, port=None, virtual_host=None, username=None, password=None ) :
	
		super(NormalQueue, self).__init__( host, port, virtual_host, username, password )
	
		self.queue_name = queue_name
		
		# Create a persistent queue
		if self.channel:
			self.channel.queue_declare( queue=queue_name, durable=True )


if __name__ == '__main__' :
	
	# Run a quick test
	import logging
	logging.basicConfig()

	import sys, time

	import config
	
	# 1st
	queue_name = "this_is_a_test_queue"
	queue = NormalQueue( queue_name, config.host, config.port, config.virtual_host, config.username, config.password )
	
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
	print ' Looking for message in 5 seconds...'
	time.sleep(5)    # pause 5 seconds
	queue.start_consuming( callback )
	
