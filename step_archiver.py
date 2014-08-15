#!/usr/bin/python
# -*- coding: utf-8 -*-


'''
	The archive the images and metadata to Databank
	
	This creates IDs metadata files (from existing metadata) and starts a chain of messages to upload files to Databank
	
	Command line:
		needs: process_id, export_folder, exported_mets_file
		
	Relies on steps:
		Update METS URIs step. (step_mets_uri_update.py)
		
	Example run : 
		In Goobi:  
			/opt/digiverso/goobi/scripts/bdlss/step_archiver.py process_id={processid} export_folder=/opt/digiverso/export/{processtitle}/ exported_mets_file=/opt/digiverso/export/{processtitle}/{processtitle}.xml
		From command line:
			sudo -u tomcat6 python archiver.py process_id=54 exported_mets_file=/opt/digiverso/export/_7654321/_7654321.xml export_folder=/opt/digiverso/export/_7654321
'''

# example run (from goobi): 
# /usr/bin/python /opt/digiverso/goobi/scripts/databank/archiver.py process_id=54 exported_mets_file=/opt/digiverso/export/_7654321/_7654321.xml export_folder=/opt/digiverso/export/_7654321

import os, os.path

from lxml import etree

from archive_to_databank import ArchiveToDatabank
from goobi.goobi_step import Step


class Step_Archiver( Step ) :

	def setup( s ):
		
		s.name = "Archiver"
	
		s.config_main_section = "archiver"
		s.essential_config_sections = set( [ "databank","rabbitmq" ] )
		s.essential_commandlines = {
			"process_id"	: "number",
			"exported_mets_file"	: "file",
			"export_folder"	: "folder"
		}
		
		s.datasets = []
	
	
	def step( self ) :
		
		error = None
		
		export_folder = self.command_line.export_folder
		exported_mets_file = self.command_line.exported_mets_file
		exported_mets_file_original = self.command_line.exported_mets_file + self.config.general.mets_file_original_extension 
		
		#
		# Create databank datasets list
		#
		object_uuid = ""
	
	
		# First read UUID's from (original) Mets file, and collect together files mentioned in it.
		mets, error = self._open( exported_mets_file_original )
		if mets:
			
			root = mets.getroot( )
			
			#At: 	/mets:mets/@OBJID
			object_uuid = root.get( "OBJID" )[9:] # whole object
			self.dataset( object_uuid )
			
			# At:    /mets:mets/mets:structMap[@TYPE='PHYSICAL']/mets:div/mets:div 
			for div_element in root.iterfind( r"./{http://www.loc.gov/METS/}structMap[@TYPE='PHYSICAL']/{http://www.loc.gov/METS/}div/{http://www.loc.gov/METS/}div" ) :
				
				uuid = div_element.get( "CONTENTIDS" )[9:]
				id = div_element.get( "ID" )
				
				# print id, uuid
				
				self.dataset( uuid )
				
				for fptr in div_element.iterfind( r"{http://www.loc.gov/METS/}fptr" ) :
				
					xpath = r"./{http://www.loc.gov/METS/}fileSec/{http://www.loc.gov/METS/}fileGrp/{http://www.loc.gov/METS/}file[@ID='" + fptr.get( "FILEID" ) + r"']/{http://www.loc.gov/METS/}FLocat"
					
					file_link = root.find( xpath )
					fileGrp_name = file_link.getparent().getparent().get("USE")
					file_location = file_link.get( "{http://www.w3.org/1999/xlink}href" )
				
					file = file_location
					filename = fileGrp_name + os.path.splitext(file_location)[1]
					self.dataset( uuid, { "file":file, "filename":filename } )
	
					#print file, filename
			
			
		else:
			error = "Cannot open the Mets file in the archiver"
	
		#import sys
		#sys.exit()
	
		
		# Now look in sub folders for additional metadata derivatives.
		if not error:

			# Get the files in the export folder
			#archive_files = os.listdir( export_folder )
			sub_folders = self.getSubFolders( export_folder )
			uuids = self.get_dataset_names()
			
			for sub_folder in sub_folders:
				
				sub_folder_files = os.listdir( sub_folder )
				for sub_folder_file in sub_folder_files:
				
					for uuid in uuids:
						# For each file in each sub directory we check whether it contains a matching uuid for all our uuids
					
						if uuid in sub_folder_file:
							file = os.path.join( sub_folder, sub_folder_file )
							filename = os.path.basename(sub_folder) + os.path.splitext(sub_folder_file)[1]

							self.dataset( uuid, { "file":file,"filename":filename } )

		
			
		# Add in the main mets file
		self.dataset( object_uuid, { "file": exported_mets_file, "filename": "mets.xml"} )
		self.dataset_rename( object_uuid, "master_" + object_uuid ) # Change it last so that id matching still works until this point.
		
	
		file_exists_error = None
		if not error:
			files_missing = []
			# Check the files exist
			for dataset in self.datasets :
				if self.debugging:
					print "uuid:", dataset['dataset']
				
				for file_obj in dataset['files'] :
					if self.debugging:
						print "   ",file_obj["file"]
						
					file_exist_error = self.checkFile( file_obj["file"] )
					if file_exist_error:
						files_missing.append( file_exist_error )
		
			if files_missing:
			
				self.warning_message( "In Archiver." + ", ".join(files_missing) )
				file_exist_error = "Missing archiver files, see warnings.";
		
		
		for dataset in self.datasets[:10]:
			print dataset["dataset"]

			for file_obj in dataset["files"]:
				if "filename" in file_obj:
					print file_obj["file"], file_obj["filename"]
				else:
					print "Missing filename", file_obj["file"]

		#import sys
		#sys.exit()
		
		if not error and self.datasets:
		
			self.info_message( "Have " + str( len( self.datasets ) ) + " datasets to archive. Beginning..." )
			gotoda = ArchiveToDatabank( self.config, self.glogger )
			
			silo = self.config.databank.silo
			success = gotoda.archive( silo, self.datasets ) #self.command_line.process_id, self.command_line.exported_mets_file, self.command_line.original_images_folder )
			
			if not success:
				error = "Error archiving the files to databank in ArchiveToDatabank"
			
			elif file_exist_error:
				error = file_exist_error + " However, I have archived what I can."
		
		
		if not self.datasets:
			error = "Nothing to archive?!?!"

			
		return  error

	
	def get_dataset_names( self ):
	
		names = []
		
		for dataset in self.datasets:
			names.append( dataset['dataset'] )
		
		return names
	
	def dataset( self, uuid, files=None ):
		
		dataset = None
		
		for existing_dataset in self.datasets:
			if existing_dataset['dataset'] == uuid:
				dataset = existing_dataset
				
		if not dataset:
			dataset = { "dataset" : uuid }
			
			self.datasets.append( dataset )
			
		
		self._dataset_files( dataset, files )
		
	def dataset_rename( self, oldname, newname ):
		for existing_dataset in self.datasets:
			if existing_dataset['dataset'] == oldname:
				existing_dataset["dataset"] = newname
				break
			
	def _dataset_files( self, dataset, files ):
	
		if "files" not in dataset:
			dataset['files'] = []
	
		if files:
			if isinstance( files, list ):
				for file in files:
					self._dataset_file( dataset, file )
					#dataset["files"].append( self._dataset_file_clean(file) )
			else:
				self._dataset_file( dataset, files )
				#dataset["files"].append( self._dataset_file_clean(files) )

	def _dataset_file( self, dataset, file ):

		if isinstance( file, dict ):
			file_object = {
				"file" : self._dataset_file_clean(file["file"])
			}

			if "filename" in file:
				file_object["filename"] = file["filename"]
		else:
			file_object = {
				"file" : self._dataset_file_clean(file)
			}


		dataset["files"].append( file_object )

	def _dataset_file_clean( self, file ):
		if file.startswith("file://") :
			file = file[7:]
		return file

	def getSubFolders( self, folder ) :
		
		return [os.path.join(folder,item) for item in os.listdir(folder) if os.path.isdir(os.path.join(folder,item))]
	
	
	
	def _open( self, file ) :
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
	archiver = Step_Archiver( config_ini.file ).begin()










