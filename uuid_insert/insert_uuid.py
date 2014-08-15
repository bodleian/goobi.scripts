# -*- coding: utf-8 -*-

import uuid, codecs,os.path, shutil

from lxml import etree

class InsertUUID:
	"""
		Insert UUID in the generated METS files.
		
		
	"""
	def __init__( self, logger=None, debugging=False ) :
		
		self.debugging = debugging
		self.logger = logger
		
		self.object_id_attribute = "OBJID"
		self.content_id_attribute = "CONTENTIDS"
		
		
		
	def insert( self, mets_file, object_uuid, children_uuid=[], make_backup=False ) :
	
		mets, error = self._open( mets_file )

		if mets:
	
			root = mets.getroot()
			
			if self.object_id_attribute not in root.attrib : 
			
				# Add object ID
				root.set( self.object_id_attribute, object_uuid )
				
				# Add contents ID to all structMap divs
				uuids = self.uuid_generator( children_uuid )
				
				# /mets:mets/mets:structMap[@TYPE='PHYSICAL']/mets:div/mets:div
				for element in root.iterfind( "./{http://www.loc.gov/METS/}structMap[@TYPE='PHYSICAL']/{http://www.loc.gov/METS/}div/{http://www.loc.gov/METS/}div" ) :
					if self.content_id_attribute not in element.attrib:
						element.set( self.content_id_attribute, uuids.next() )
				
				# Debug
				pretty_print = False
				if self.debugging:
					pretty_print = True
					#print etree.tostring( root, xml_declaration=True, encoding='UTF-8', method='xml', pretty_print=pretty_print )
				
				
				# Make a backup of the original file
				if make_backup:
					count = 1
					try:
						while os.path.exists( mets_file + ".uuid." + str(count) ) :
							count += 1
							
						shutil.copyfile( mets_file, mets_file + ".uuid." + str(count) )
					except:
						filename = "Unknown"
						try:
							filename =  + mets_file + ".uuid." + str( count )
						except:
							pass #
							
						self._warning( "Couldn't create backup file in UUID creation: " + filename )
				
				# Replace file
				success, error = self._save( mets_file, unicode( etree.tostring( root, xml_declaration=True, encoding='UTF-8', method='xml', pretty_print=pretty_print ), "utf-8" ) )
			
				if not success:
					self._error( error )
				
					return False
			
		else :
			self._error( error )
			return False
		
		return True
	
	
	def uuid_generator( self, children ) :
		""" 
			Return a child from the children list or generate a new one if we run out 
			(We simply return the order which is in the original metadata. If at some point a new file was inserted then technically later files will not point back at the same page. In most situations this won't matter and it'll rarely happen in practive.)
		"""
		
		for child in children:
			yield child
			
		while 1:
			yield self._uuid()
	
	
	def _uuid( self ):
		return "urn:uuid:" + str( uuid.uuid4() )
	
	def _save( self, file, text ) :
		""" 
			Save to a temp file then copy over the entire file.
			This avoids the original file being empty if the write fails... which is bad... ! (codecs.open will empty the file when it opens)
		"""
		tempfile = file + ".temp"
		
		try:
			fout = codecs.open( tempfile, 'w', "utf_8" )
			fout.write( text )
			fout.close()
			
			os.rename( tempfile, file )
			
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
	
	
	def _error( self, message ):
		if self.logger:
			self.logger.error( message )
		self._debugging( "Error: " + message )
	def _warning( self, message ):
		if self.logger:
			self.logger.warning( message )
		self._debugging( "Warning: " + message )
	def _info( self, message ):
		if self.logger:
			self.logger.info( message )
		self._debugging("Info: " + message)
	def _debug( self, message ):
		if self.logger:
			self.logger.debug( message )
		self._debugging("Debug: " + message)
		
	def _debugging( self, message ):
		if self.debugging :
			print message
		
		
if __name__ == '__main__' :

	insert_uuid = InsertUUID( debugging=True)

	import sys
	
	#insert_uuid.insert( "meta-small.xml", True )
	#insert_uuid.insert( "meta-large.xml", True )
	print "File name: " + sys.argv[1]
	
	insert_uuid.insert( sys.argv[1], True )
	

