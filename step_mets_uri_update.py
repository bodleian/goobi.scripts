#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
	Update METS
	
	Replace the image paths in the METS file with urls in Databank, save a backup first (we need the original so we can find the images to put them into databank!)
	
	Command line:
		needs: process_id,  and metadata_file
		
	Relies on steps:
		METS uuid inserter step. (step_mets_uuid_inserter.py)

	Example run : 
		In Goobi:  
			/opt/digiverso/goobi/scripts/bdlss/step_mets_uri_update.py process_id={processid} exported_mets_file=/opt/digiverso/export/{processtitle}/{processtitle}.xml
		From command line:
			sudo -u tomcat6 python step_mets_uri_update.py process_id=54 exported_mets_file=/opt/digiverso/export/_7654321/_7654321.xml

'''

import os.path, codecs, shutil
from lxml import etree

from databank.databank import Databank
from goobi.goobi_step import Step

class Step_Mets_URI_Update( Step ) :

	def setup( s ) :
	
		s.name = "Update METS URLs"
	
		s.config_main_section = "update_mets" # Info for this particular step
		s.essential_config_sections = set( ['general'] )
		s.essential_commandlines = {
			"process_id" : 					Step.type_number,
			"exported_mets_file":		Step.type_file
		}
	
	def step( self ) :
	
		error = None
		
		mets_file = self.command_line.exported_mets_file
		mets_file_original = mets_file + self.config.general.mets_file_original_extension 
		
		# Duplicate METS so we always have the original file (This has the current image paths)
		if self.debug:
			print "File locations:", mets_file, mets_file_original
		
		shutil.copyfile( mets_file, mets_file_original )
		error = self.checkFile( mets_file_original )
		
		if error == None:
			
			silo = self.config.databank.silo
			
			mets, error = self._open( mets_file )
			
			if mets:
			
				error = None
				
				schema = r"{http://www.loc.gov/METS/}"
				
				pretty_print = False
				if self.debug:
					pretty_print = True
					
				root = mets.getroot()
				for div_element in root.iterfind( r"./{0}structMap[@TYPE='PHYSICAL']/{0}div/{0}div".format (schema) ) :
				
					uuid = div_element.get( "CONTENTIDS" )[9:]
					
					for fptr in div_element.iterfind( "{0}fptr".format(schema) ) :
					
						xpath = r"./{0}fileSec/{0}fileGrp/{0}file[@ID='{1}']/{0}FLocat".format( schema, fptr.get( "FILEID" ) )
						
						file_link = root.find( xpath )
						file_href_basename = os.path.basename( file_link.get( "{http://www.w3.org/1999/xlink}href" ) )
						
						databank_href = self.config.update_mets.databank_url + Databank.getFileUrl( silo, uuid, file_href_basename )
						file_link.set( "{http://www.w3.org/1999/xlink}href", databank_href )
				
				success, error = self._save( mets_file, unicode( etree.tostring( root, xml_declaration=True, encoding='UTF-8', method='xml', pretty_print=pretty_print ), "utf-8" ) )
				
				if success:
					error = None
					
		else:
		
			error += " Unable to copy the METS file"
		
		return error

	def _save( self, file, text ) :
	
		""" Save file. """
		
		try:
			fout = codecs.open( file, 'w', "utf_8" )
			fout.write( text )
			fout.close()
			
			return True, None
		
		except IOError:
		
			return False, "Failed to write file: " + file
		
		
	def _open( self, file ):
		""" Open a file and pass it into the tree parser """
		try:
			xml = etree.parse( file )
		except IOError:
			return None, "Failed to open file: " + file
		except etree.XMLSyntaxError as ex:
			return None, "XML syntax error: " + file + " - " + ex.msg

		return xml, ''
		
if __name__ == '__main__' :

	import config_ini
	Step_Mets_URI_Update( config_ini.file ).begin( )






