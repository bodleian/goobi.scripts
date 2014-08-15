# -*- coding: utf-8 -*-

import sys, json, mimetypes

from databank.databank import Databank
from config.config_reader import ConfigReader
from rabbitmq.normal_queue import NormalQueue

class WorkerClearQueue:
	"""
		Create a dataset and add the list of files we have.
	"""
	def __init__( self ) :
		
		import config_ini
		self.config = ConfigReader( config_ini.file )
		self.queue = None
		
		self.ok = 0
		self.error = 1
		self.unknown = -1

	def __del__(self):
		if self.queue:
			self.queue.close()
		
	def work( self, queue ) :
		print self.config.rabbitmq.host, int(self.config.rabbitmq.port)
		self.queue = NormalQueue( queue, self.config.rabbitmq.host, int(self.config.rabbitmq.port), self.config.rabbitmq.virtual_host, self.config.rabbitmq.username, self.config.rabbitmq.password )
		self.queue.start_consuming( self.worker )
			
	
	def worker( self, ch, method, properties, body ):
		# message = json.loads( body )
		print ' Deleting message : ', body

		ch.basic_ack( delivery_tag = method.delivery_tag ) # Say completed and remove from queue.
		
		
if __name__ == '__main__' :

	queue = 'temp___databank_archiver'#'temp___databank_archiver222' 
	
	print 'This process will remove all messages in the queue "' + queue + '" and mark them completed. '
	print 'You will need to MANUALLY stop it or it will CONTINUE to delete messages!'
	print "Type 'Y' to empty the queue: " + queue
	clear = raw_input()
	
	if clear == "Y" :
		print "Clearing..."
		
		wtd = WorkerClearQueue()
		wtd.work( queue )
	else:
		print "Clear cancelled"


