# -*- coding: utf-8 -*-

import json, uuid

# from databank.databank import Databank

from rabbitmq.normal_queue import NormalQueue
from rabbitmq.random_exclusive_queue import RandomExclusiveQueue

from worker_to_databank import WorkerToDatabank

class ArchiveToDatabank:
	"""
		Create a queue each message being a dataset
		Each message has one or more files to place in the dataset
		
		We then create a unique queue to keep track of the process happening in the worker (see "worker_to_databank.py")
	"""
	def __init__( self, config, logger=None ) :
		
		# TODO: Remove relience on config file. Parameters should be passed in...
		self.config = config
		self.logger = logger
		
	def archive( self, silo, datasets ): 
		"""
			datasets in form:

				new version
				[
					{
						'dataset': '7d22ca7a-2d84-41ed-a911-f230c6dec91d',
						'files' :
							[
								{
									file: 'some/file.xml',
									filename: "file.new.name.xml"
								},
								{
									'file': 'another/file.jpg' 
								}
							]
					},
					...
					...
				]



				old version:
				[
					{
						'dataset': '7d22ca7a-2d84-41ed-a911-f230c6dec91d',
						'files' :
							[
								'some/file.xml',
								'another/file.jpg'
							]
					},
					...
					...
				]
		"""
		host = self.config.rabbitmq.host
		port = int(self.config.rabbitmq.port)
		virtual_host = self.config.rabbitmq.virtual_host
		username =self.config.rabbitmq.username
		password = self.config.rabbitmq.password
		
		# Register a queue for responses before we do anything else. (So that worker can still send message)
		queue_response = RandomExclusiveQueue( host, port, virtual_host, username, password )
		if not queue_response.connected():
			self._error( "Unable to connect to message queue at: " + self.config.rabbitmq.host  )
			return False

		queue_response_name = queue_response.get_queue()
		
		queue_send = NormalQueue( self.config.rabbitmq.queue_to_databank, host, port, virtual_host, username, password )
		if not queue_send.connected():
			self._error( "Unable to connect to message queue at: " + self.config.rabbitmq.host  )
			return False
		
		
		# send messages of files.
		self.sent_messages = []
		
		for dataset in datasets:
			
			message = {
				"silo" : silo, 
				"response" : queue_response_name, 
				"done" : False,
				"dataset" : dataset['dataset'],
				"files" : dataset['files']
			}
		
			json_message = json.dumps( message )
			queue_send.send_message( json_message )
			#queue_send.sleep(0.2)
			
			self.sent_messages.append( message )
			
			#count += 1
		
		queue_send.close()
		
		for message in self.sent_messages:
			print message
		
		try:
			queue_response.start_consuming( self.response )
		except KeyboardInterrupt:
			pass
		finally:
			queue_response.close()
		
		if self._checkComplete() :
			# We've done and successfully.
			return True
			
		return False

	
	def response( self, channel, method, properties, body ) :
		# Read in one message at time.
		
		#print "From reponse() : ", body
		
		print "Got Response..."
		
		stop = False
		
		message = json.loads( body )
		
		if message['type'] == WorkerToDatabank.MessageType.warning : 
			self._warning( message['message'] )
			
		elif message['type'] == WorkerToDatabank.MessageType.error : 
			self._error( message['message'] )
			# Something has broken. The most likely reason is that networking is down
			# I guess we should wait for a bit before we give up...
			# Although, Is there ever a reason to give up?
			# stop = True  
			
		elif message['type'] == WorkerToDatabank.MessageType.info : 
			# self._info( message['message'] ) # Unfortunately sending the info back for every file can fill in the tiny mysql field goobi uses for its log... so I've disabled it (this "info" isn't essential to the running of the system - just a nice to know)
			print "Info: " + message['message']
			
		elif message['type'] == WorkerToDatabank.MessageType.final : 
			if message['ok'] == True :
				self._setDone( message['dataset'] )
				
				if self._checkComplete() :
					stop = True
				
			else :
				self._error( 'A dataset failed to be stored in databank: "' + message['dataset'] + '"' )
				
		else :
			self._warning( "Message type unknown" )
		
		
		print "Message Recieved: (" + message['type'] + ") " + str(message)
				
		channel.basic_ack( delivery_tag = method.delivery_tag )
		
		print "...closed Response."
		print
		
		if stop:
			channel.stop_consuming()

				
	def _setDone( self, dataset ):
		message = self._findMessage( dataset )
		if message:
			message['done'] = True
			#print "_setDone: done"
			return True
			
		#print "_setDone: FAILED"
		return False
	
	
	def _findMessage( self, dataset ) :
		#print "sent messages", self.sent_messages
		#print "Datasets: ", dataset, self.sent_messages[0]['dataset']
		for message in self.sent_messages:
			if message['dataset'] == dataset:
				return message
			
		return None
	
	
	def _checkComplete( self ):
		for message in self.sent_messages:
			if message['done'] == False: 
				#print "_checkComplete: Not complete"
				return False
				
		#print "_checkComplete:complete"
		return True
	
	
	def _error( self, message ):
		if self.logger:
			self.logger.error( message )
	def _warning( self, message ):
		if self.logger:
			self.logger.warning( message )
	def _info( self, message ):
		if self.logger:
			self.logger.info( message )
	def _debug( self, message ):
		if self.logger:
			self.logger.debug( message )
	
	
		


if __name__ == '__main__' :

	from config.config_reader import ConfigReader
	import config_ini
	
	gotoda = ArchiveToDatabank( ConfigReader(config_ini.file) )
	
	datasets = [
		 {
			'dataset': '000_a_temp_dataset',
			'files' : [
				'testing/text.txt',
			]
		}
	]
	
	gotoda.archive( "temp___Imaging", datasets )
	
	
