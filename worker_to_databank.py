# -*- coding: utf-8 -*-

import sys, json, mimetypes, time, os.path
import logging, logging.handlers

from databank.databank import Databank
from config.config_reader import ConfigReader

from rabbitmq.normal_queue import NormalQueue
from rabbitmq.random_exclusive_queue import RandomExclusiveQueue

class WorkerToDatabank:
	"""
		Create a dataset and add the list of files we have.
	"""
	
	conflict_error = 409 # Something already exists (silo, datasets, etc.)
	
	class Status:
		ok = 0
		error = 1
		unknown = -1
	
	class MessageType:
		final = 'final'
		info = 'info'
		warning = 'warning'
		error = 'error'
	
	def __init__( self ) :
		
		import config_ini
		self.config = ConfigReader( config_ini.file ) # TODO: Need to lose this config file (so the worker stands by itself)
		
		self.queue = None
		self.debugging = False
		self.logger = None

	def __del__( self ):
		if self.queue:
			self.queue.close()
		
	def work( self ) :
		
		mimetypes.init()
		
		self._logging()

		# Create only static objects in this function, we don't want multiple threads changing member variables!
		self.queue = NormalQueue( self.config.rabbitmq.queue_to_databank, self.config.rabbitmq.host, int( self.config.rabbitmq.port ), self.config.rabbitmq.virtual_host, self.config.rabbitmq.username, self.config.rabbitmq.password )
		if not self.queue.connected():
			self._sendError( None, "rabbitmq", "Unable to connect to :" + self.config.rabbitmq.host )
			sys.exit(1)
		
		self._debug( "Worker waiting for messages..." )
		
		self.queue.return_callback( self.lost_message )
		
		self.queue.start_consuming( self.worker )
			
		
	def _logging( self ):
	
		#
		# Create our file logger
		#
		log_file = self.config.archiver.worker_log
		log_max_bytes = 50000000
		log_backup_count = 4

		try:
			log_max_bytes = int( self.config.archiver.log_max_bytes )
			log_backup_count = int( self.config.archiver.log_backup_count )
		
		except AttributeError:
			log_max_bytes = int( self.config.general.log_max_bytes )
			log_backup_count = int( self.config.general.log_backup_count )
		
		except ValueError:
			pass

		logger = logging.getLogger( "ArchiveWorkerLogger" )

		if self.config.archiver.debug:
			logger.setLevel = logging.DEBUG
			self.debugging = True
		else:
			logger.setLevel = logging.WARNING

		try:
			rotating_logger_handler = logging.handlers.RotatingFileHandler( log_file, maxBytes=log_max_bytes, backupCount=log_backup_count )  
			rotating_logger_handler.setFormatter( logging.Formatter( '%(asctime)s (%(levelname)s)   %(message)s' ) )
			logger.addHandler( rotating_logger_handler )
			
			self.logger = logger
			
		except IOError:
			self._debug( "ERROR: Unable to open log file at : " + log_file, True )
			sys.exit(1)
	
	def _debug( self, message, force=False ):
		if self.debugging or force:
			print "(debug) ", message
			print
			
		if self.logger:
			self.logger.debug( message )
		
	def _sendMessage( self, response_queue, type, subject, message = {}, message_text = None  ):
		""" Send a message back to the queue we need to respond on so archiver.py knows what is happening """
		
		self._debug( self._messageToString(type, subject, message, message_text) )
		
		message['type'] = type
		
		if subject :
			message['subject'] = subject
		
		if message_text :
			message['message'] = message_text
		
		if response_queue :
			message_json = json.dumps( message )
			
			try_repeat = 3
			if not response_queue.send_message( message_json, try_repeat=try_repeat ) :
				self.log_message_not_sent( message )
				
			# time.sleep(0.2) 
			
	def _messageToString( self, type, subject, message = {}, message_text = None  ):
		message_string = [type," : "]
		if subject :
			message_string.append( "( " + subject + " )" )
		if message_text :
			message_string.append( " - " + message_text )
		if message :
			message_string.append( "  [[[ message dict: " + str(message) + "]]]  " )
		return "".join(message_string)
	
	def _sendError( self, response_queue, subject, message_text = None, message={}  ):
		print "Error:", message_text
		self._sendMessage( response_queue, self.MessageType.error, subject, message, message_text )
		self.logger.error( self._messageToString( self.MessageType.error, subject, message, message_text ) )
		
		return self.Status.error, message_text
		
	def _sendInfo( self, response_queue, subject, message_text, message = {} ):
		self._sendMessage( response_queue, self.MessageType.info, subject, message, message_text )
		self.logger.info( self._messageToString( self.MessageType.info, subject, message, message_text ) )
		
	def _sendWarning( self, response_queue, subject, message_text, message={} ):
		self._sendMessage( response_queue, self.MessageType.warning, subject, message, message_text )
		self.logger.warning( self._messageToString( self.MessageType.warning, subject, message, message_text ) )
	
	
	def worker( self, channel, method, properties, body ):
	
		status = self.Status.unknown
		error = None
		response_queue = None
		
		if True:
		#try:
			
			self._debug( 'Have message, Worker STARTED: ' )
			
			message = json.loads( body )
			self._debug( 'worker message: ' + str(message) )

			# Check message in right format
			try:
				silo = message['silo']
				dataset = message['dataset']
				files = message['files']
				response_queue_name = message['response']
				
			except KeyError:
				status, error = self._sendError( None, "message", "Message missing required key, silo, dataset, files, response : " + str( message ), message )

				
			# Connect to queue we need to respond on
			if status != self.Status.error :
				response_queue = RandomExclusiveQueue( self.config.rabbitmq.host, int(self.config.rabbitmq.port), self.config.rabbitmq.virtual_host, self.config.rabbitmq.username, self.config.rabbitmq.password, response_queue_name )
				if not self.queue.connected():
					status, error = self._sendError( None, "message", "Unable to connect to message queue at: " + self.config.rabbitmq.host, message )

			
			# Connect to databank
			if status != self.Status.error :
				try:
					databank = Databank( self.config.databank.host, self.config.databank.username, self.config.databank.password )
				except:
					status, error = self._sendError( response_queue, "databank", "Unknown error when connecting to Databank: " + self.config.databank.host )
				else:
					# Test connection
					connection_status, connection_error = self._checkDatabankConnection( databank )
					if connection_status != self.Status.ok :
						status, error = self._sendError( response_queue, "databank", 'Problem connecting to databank: ' + connection_error  )	
			
			# Attempt to Create silo
			if status != self.Status.error :
				silo_status = self._createSilo( databank, silo )
				if silo_status != self.Status.ok :
					status, error = self._sendError( response_queue, "silo", 'Unable to create silo [' + silo + '] in Databank'  )
				
			
			
			if status != self.Status.error :
			
				self._debug( "We have silo : " + silo )
				
				# Attempt to create dataset
				dataset_status = self._createDataset( databank, silo, dataset )
				
				if dataset_status != self.Status.ok :
					status, error = self._sendError( response_queue, "dataset", "Unable to create dataset [" + dataset + "] in databank" )
				else:
					self._debug( "Dataset created : " + dataset )
				
				if status != self.Status.error :
				
					# COULD TODO: Maybe we should check the files aren't already there, but this is quite hard to know, Are the files there but the wrong size? Are the files earlier versions? May as well just upload again, databank will create new versions when necessary.
					# response = databank.getFiles( silo, dataset )
					
					status = self.Status.ok 
					
					for file in  files:
						filename = None

						if isinstance( file, dict ) :
							# We check this so we can support older versions where "file" was a string
							if "filename" in file:
								filename = file['filename']
							file = file["file"]

						self._debug( "Uploading : " + file )
						
						if os.path.exists( file ):
						
							file_status = self._uploadFile( response_queue, databank, silo, dataset, file, filename )
							
							if file_status == self.Status.ok :
								self._sendInfo( response_queue, file, "File uploaded" )
							
							else:
								status, error = self._sendError( response_queue, "file", "Unable to upload file : [" + file + "]" ) # with mimetype : " + mime )

								break # To continue or not to continue... Not to.
					
						else :
							self._sendWarning( response_queue, file, file + " - File doesn't exists!" )
							# This file doesn't exists... is that Good or bad? Do we keep the message? We'll have to remove it as it'll never get processed and stay in the list. So we'll pretend it's OK... we have sent a warning.

			
			if status == self.Status.ok:
				channel.basic_ack( delivery_tag = method.delivery_tag )  # Say completed and remove from queue.
				self._debug( 'Worker FINISHED' )
			else:
				self._debug( 'Worker ERRORED' )

		#except :
		#
		#	status, error = self._sendError( None, "exception", "There has been a serious unknown exception in " + __name__ )
		#	self._debug( 'Worker EXCEPTION - ' + error )
		#	self._debug( sys.exc_info()[0] )
		#	
		#	#raise # Re throw the exception.
			
		# Responde and say if it succeeded on not.
		message['ok'] = status == self.Status.ok
		message['error'] = error
		
		self._sendMessage( response_queue, self.MessageType.final, None, message )
			
		response_queue.close()
			
		# sys.exit() # Stop after one completed, for debugging!
	
		if status != self.Status.ok :
			# If something is broken, wait until ending, it might be a temporary thing (e.g. network down)
			time.sleep( 30 )
	
	
	def lost_message( self, channel, method, properties, body ):
		""" Add failed messages to FILE log """
		message = json.loads( body )
		
		self.log_message_not_sent( message )
	
	def log_message_not_sent( self, message ):
		
		if 'type' in message and (message['type'] == self.MessageType.error or message['type'] == self.MessageType.final ) :
			self._sendError( None, "message", "Unable to send message: " + str(message), message )
		else:
			self._sendWarning( None, "message", "Unable to send message: " + str(message), message )
			
	def _uploadFile( self, response_queue, databank, silo, dataset, file, filename=None ) :
		"""" Attempt to upload the file """
		mime = mimetypes.guess_type( file )[0]
		
		try_repeat = 3
		
		for tries in range( try_repeat ):
			response = databank.uploadFile( silo, dataset, file, format=mime, filename=filename )
			if Databank.responseGood( response ) :
				return self.Status.ok
			else:
				if tries != try_repeat-1:
					self._sendWarning( response_queue, file, "File failed to upload, trying " + str(try_repeat - tries - 1) + " more time [" + file + "]'" )
					
				time.sleep( 10 )
			
		return 	self.Status.error
	
	def _createDataset( self, databank, silo, dataset ):
		''' Attempt to create dataset. If it's already created continue.'''
		response = databank.createDataset( silo, dataset )
		
		if not Databank.responseGood( response, [self.conflict_error] ) :
			self._debug( "Create Dataset: " + response.error )
			return self.Status.error
		
		return 	self.Status.ok
	
	def _createSilo( self, databank, silo ):
		''' Check silo exists, if not create it '''
		# It doesn't really need to do this everytime but doesn't cost much to do.
		# Actually it doesn't even work in the current databank implemetation [1] (at least not with normal rights on a user)
		
		silos = databank.getSilos().results
		if silo not in silos:
			response = databank.createSilo( silo ) # [1] Errors with Forbidden at the moment (possibly due to needing admin rights!)
			if not databank.responseGood( response, [self.conflict_error] ):
				self._debug( "Create silo: " + response.error )
				return self.Status.error
			
		return self.Status.ok

		
	def _checkDatabankConnection( self, databank ):
		''' Check we can request silos from databank and the response is good '''
		response = databank.getSilos()
		
		if not databank.responseGood( response ):
			self._debug( "Database Connection: " + response.error )
			return self.Status.error
		
		return self.Status.ok, None
	
	
		
if __name__ == '__main__' :

	wtd = WorkerToDatabank()
	
	wtd.work()

