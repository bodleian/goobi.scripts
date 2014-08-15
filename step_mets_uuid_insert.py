#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
	The Mets UUID Insertion for Goobi
	
	This creates IDs and inserts them into the meta.xml file which goobi outputs
	
	Command line:
		needs: process_id and metadata_file
		optional: auto_complete
		
	Relies on:
		property inserter (uuid). (step_goobi_uuid_property_insert.py)
		Goobi export

	Example run : 
		In Goobi:  
			/usr/bin/python /opt/digiverso/goobi/scripts/bdlss/step_mets_uuid_insert.py process_id={processid} uuid_property={process.uuid} exported_mets_file=/opt/digiverso/export/{processtitle}/{processtitle}.xml
		From command line:
			sudo -u tomcat6 /usr/bin/python /opt/digiverso/goobi/scripts/bdlss/step_mets_uuid_insert.py process_id=54 uuid_property=urn:uuid:8c1bebab-f5aa-4caf-ae38-bf92cc82c731 exported_metadata_file=/opt/digiverso/export/_7654321/_7654321.xml

'''

from lxml import etree

from goobi.goobi_step import Step
from databank.databank import Databank
from uuid_insert.insert_uuid import InsertUUID

class Step_METS_UUID_Insert( Step ) :

	def setup( s ) :

		s.name = "Mets UUID insert"
		
		s.config_main_section = "uuid_insert"
		s.essential_config_sections = set( [ "saxon", "databank" ] )
		s.essential_commandlines = {
			"process_id":					Step.type_number,
			"exported_mets_file":		Step.type_file,
			"uuid_property" : 	Step.type_string
		}

		
	def step( self ) :
	
		error = None
		object_uuid = self.command_line.uuid_property
	
		if ":uuid:" not in  object_uuid:
			error = "Commandline object_uuid - from property uuid - does not have a valid format. e.g. urn:uuid:fdc407b6-c825-41df-a2e4-a078f26a3231"
			
		else:
			# Check already in databank, if so we need to grab the DC file which has the list of generated UUIDs for all the child pages. (Actually just those children already archived, not necessarily the same number we have now...)
			
			found, file_content, error = self._inDatabank( object_uuid )
			
			if error :
			
				return error
				
			else:
			
				error = None
				
				child_uuids = []
				
				if found:
					
					dc = etree.fromstring( file_content )
					
					for element in dc.iterfind( "./{dcterms}hasPart" ) :
						child_uuids.append( element.text )
						print element.text
			
				insert_uuid = InsertUUID( self.glogger, self.debug )
				
				success = insert_uuid.insert( self.command_line.exported_mets_file, object_uuid, child_uuids, make_backup=self.debug )

				if not success:
					error = "Error from InsertUUID"
		
		return error
		
	def _inDatabank( self, object_uuid ) :
		
		found, file_contents, error = False, "", None
		
		try:
			databank = Databank( self.config.databank.host, self.config.databank.username, self.config.databank.password )
		except:
			error = "Unknown error when connecting to Databank"
		else:
			# response = databank.getDataset( self.config.databank.silo, object_uuid[9:] )
			
			#print databank.getFileUrl( self.config.databank.silo, object_uuid[9:], "dc_" + object_uuid[9:] + "-master.xml" )
			response = databank.getFile( self.config.databank.silo, object_uuid[9:], "dc_" + object_uuid[9:] + "-master.xml" )
			
			if Databank.good( response ) :
				# It IS in databank
				
				#Databank.printResponse( response )
				file_contents = response.data # unicode( response.data.decode("UTF-8") )
			
				found = True
			
			elif response.status == 404:
				# It ISN'T in databank
				found = False
				file_contents = ""
				
			else :
				# It broke!
				error = "Unknown error working out if file exits in databank. Status=" + response.status
		
		return found, file_contents, error
				

if __name__ == '__main__' :

	import config_ini
	Step_METS_UUID_Insert( config_ini.file ).begin( )




