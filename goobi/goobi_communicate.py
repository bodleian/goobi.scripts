# -*- coding: utf-8 -*-

#Send a log message: 'http://127.0.0.1/goobi/wi?command=addToProcessLog&processId='+processId+'&value=Beginning&jpeg2000&conversion&type=error&token=PASSWORD'
# close a step automatically: 'http://127.0.0.1/goobi/wi?command=closeStep&stepId='+stepId+'&token=PASSWORD'
import urllib, urllib2

class GoobiCommunicate() :
	"""
		Simplfy the communication between python and Goobi.
		
	"""
	protocol = "http"
	url_base = "{protocol}://{host}/goobi/wi?"
	url_token = "&token={token}"
	url_command = "command={command}"
	
	def __init__( self, host, password_token, debugging=False ) :
	
		self.host = host if host is not None else '127.0.0.1'
		self.token = password_token
		self.debugging = debugging
		
		self._update_url_base()
	
	def addToProcessLog( self, level, message, process_id ) :
		
		goobi_levels = ['info', 'error', 'debug', 'user']
		
		if level not in goobi_levels:
			print "Level not recognised, use one of " + ",".join( goobi_levels )
			return False
		
		additional = {
			'processId' : process_id,
			'type' : level,
			'value' : message
		}
	
		return self._send( "addToProcessLog", additional )
	
	def closeStep( self, step_id=None, process_id=None ) :
		
		if not step_id and not process_id:
			print "Must have either a step id or a process id!"
		
		if step_id:
			additional = { "stepId" : step_id }
			
			return self._send( "closeStep", additional )
			
		if process_id:
			return self.closeStepByProcessId( process_id )
			
		return False
			
	def closeStepByStepId( self, step_id ) :
		return self.closeStep( step_id )
		
	def closeStepByProcessId( self, process_id ) :
	
		additional = { "processId" : process_id }
		
		return self._send( "closeStepByProcessId", additional )

	
	
	def reportProblem( self, step_id, destination_step_name, error_message=None ) :
		
		return self.reportProblemToPreviousStep( step_id, destination_step_name, error_message )
		
	def reportProblemToPreviousStep( self, step_id, previous_step_name, error_message=None ) :
		
		additional = {
			"stepId" : step_id,  
			"destinationStepName" : previous_step_name,
			"errorMessage" : error_message if error_message else "No error given"
		}

		return self._send( "reportProblem", additional )

		
	#http://goobi.bodleian.ox.ac.uk/goobi/wi?command=AddProperty&processId=105&property=testproperty&value=testvalue&token=PASSWORD
	def addProperty( self, process_id, name, value ):
		
		additional = {
			"processId" : process_id,  
			"property" : name,
			"value" : value
		}
		
		return self._send( "AddProperty", additional )
	
	def _update_url_base( self ):
		self.url_base = self.url_base.format( protocol=self.protocol, host=self.host )
		
	def _quote( self, string ):
		return urllib2.quote( str(string), safe="" )
	
	def _send( self, command, additional=None ) :
	
		url = self.url_base
		url += self.url_command.format( command=command )

		data=None
		if additional and len( additional ) > 0 :
			data = urllib.urlencode(additional)
			#equals = [ k+"="+self._quote( additional[k] ) for k in additional ]
			#url += "&" + "&".join( equals )

		url += self.url_token.format( token=self.token )
		
		if self.debugging:
			print "Debug: GoobiCommunicate() URL:", url

		response = None		
		success = False

		try:
			response = urllib2.urlopen( url, data )

			if response.code >= 400 :

				if self.debugging:
					print "Debug: GoobiCommunicate() None OK response from Goobi:", response.msg, response.code

			else:
				success = True

		except urllib2.HTTPError as e:
			print "Debug: GoobiCommunicate() HTTPError: " + str(e.code)

		except urllib2.URLError as e:
			print "Debug: GoobiCommunicate() URLError: " + e.reason

		finally:

			try:
				if response is not None:
					response.close()
			except:
				pass

		return success
			
		
if __name__ == '__main__' :

	comm = GoobiCommunicate( "127.0.0.1", "PASSWORD", True )
	
	#comm.addToProcessLog( "info", "A test message", 53 )
	
	comm.addProperty( 54, "test_property", "test_property_value" )
	
	

