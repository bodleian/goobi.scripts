#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
	Insert UUID property into Goobi process we need this to track the file through to databank.
	
	Command line:
		needs: process_id,  and uuid_property (={process.uuid} e.g. "urn:uuid:fdc407b6-c825-41df-a2e4-a078f26a3231" )
		
	Relies on:
		None
	
	Example run : 
		In Goobi:  
			/usr/bin/python /opt/digiverso/goobi/scripts/bdlss/step_goobi_uuid_property_insert.py process_id={processid} uuid_property={process.uuid}
		From command line:
			sudo -u tomcat6 python step_goobi_uuid_property_insert.py process_id=73 uuid_property=uuid_property=\(process.uuid\)

			urn:uuid:fdc407b6-c825-41df-a2e4-a078f26a3231

'''

import uuid

from goobi.goobi_step import Step
from goobi.goobi_communicate import GoobiCommunicate

class Step_Goobi_UUID_Property_Insert( Step ) :

	def setup( s ) :
	
		s.name = "Goobi UUID Property Insert"
	
		s.config_main_section = "property_inserter"
		s.essential_config_sections = set( [] )
		s.essential_commandlines = {
			"process_id"	: Step.type_number,
			"uuid_property" 	: Step.type_string # Try to extract {process.uuid} if already there. We don't want to overwrite it.
		}
	
	def step( self ) :
		
		error = None
		
		# print "uuid '" + self.command_line.uuid_property + "'"
		
		properties = {}
		broken_properties = []
	
		if self.command_line.uuid_property == "" or "(process." in self.command_line.uuid_property : # If you request a process property from goobi that doesn't exist, it will return the name of what you asked for. e.g. "(process.uuid)" , therefore if it containts "(process." it must not have been set yet.
			
			# Set a property if not set already.
			properties['uuid'] = "urn:uuid:" + str( uuid.uuid4() )
		
			goobi_com = GoobiCommunicate( self.config.goobi.host, self.config.goobi.passcode, self.debug )
			
			success = True
			for property, value in properties.iteritems() :
				if not goobi_com.addProperty( self.command_line.process_id, property, value ) :
					broken_properties.append( str(property) + ":" + str(value) )
					success = False
			
			if not success:
				error = "Failed to create properties:- " + str(broken_properties)
		
		return error
	
	
if __name__ == '__main__' :

	import config_ini
	Step_Goobi_UUID_Property_Insert( config_ini.file ).begin()




