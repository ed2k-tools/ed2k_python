# ed2k_metutils
#    python framework for working with the download meta-information
#    storage in overnet and edonkey2K.
#
#    curious@ihug.com.au
#      tested on macosx 10.2.4, python 2.2

import struct;
import types;
import sys;

# Some defines.

TAG_TYPE_STRING  = 2;
TAG_TYPE_INTEGER = 3;

TAG_HANDLE_FILENAME   = chr( 1 );
TAG_HANDLE_FILESIZE   = chr( 2 );
TAG_HANDLE_FILETYPE   = chr( 3 );
TAG_HANDLE_FILEFORMAT = chr( 4 );
TAG_HANDLE_SOFAR      = chr( 8 );
TAG_HANDLE_GAP_START  = chr( 9 );
TAG_HANDLE_GAP_END    = chr( 10 );
TAG_HANDLE_TEMP_NAME  = chr( 18 );
TAG_HANDLE_PRIORITY   = chr( 19 );
TAG_HANDLE_PAUSED     = chr( 20 );

class MetFile:
	"""Class designed to hold the data of a .part.met file."""
	
	def __init__( self, dstore = None ):
		"""Construct a metfile class from a data stream, which is just read straight from disk, or as a blank."""
		self.p_hashes = [];
		self.m_tags = [];
		
		if not dstore:
			self.version = 224;
			self.modDate = 0;
			self.fileID = '\0' * 16; 
			return;
			
		header_struct = "<BI16sH";
		header_size = struct.calcsize( header_struct );
		
		self.version, self.modDate, self.fileID, numhashes = struct.unpack( header_struct, dstore[ 0 : header_size ] );
		
		dstore = dstore[ header_size : ];
		
		for i in range( numhashes ):
			p_hash, = struct.unpack( "<16s", dstore[ : 16 ] );
			self.p_hashes.append( p_hash );
			dstore = dstore[ 16 : ];
			
		n_meta, = struct.unpack( "<I", dstore[ : 4 ] );
		dstore = dstore[ 4 : ];
		
		for meta in range( n_meta ):
			t_type, = struct.unpack( "<B", dstore[ 0 ] );
			dstore = dstore[ 1 : ];
			
			name_len, = struct.unpack( "<H", dstore[ : 2 ] );
			dstore = dstore[ 2  : ];
			name, = struct.unpack( "<%is" % name_len, dstore[ : name_len ] );
			dstore = dstore[ name_len : ];
			
			if t_type == TAG_TYPE_INTEGER:
				value, = struct.unpack( "<I", dstore[ : 4 ] );
				dstore = dstore[ 4 : ];
			else:
				value_len, = struct.unpack( "<H", dstore[ : 2 ] );
				dstore = dstore[ 2 : ];
				value, = struct.unpack( "<%is" % value_len, dstore[ : value_len ] );
				dstore = dstore[ value_len : ];
			
			self.AddTag( MetaTag( name, value, t_type ) );
			
	def getMD4( self ):
		"""Return a string representation of the file MD4."""
		data = "";
		for i in range( len( self.fileID )  ):
			data += "%02x" % ord( self.fileID[ i ] );
		return data.upper();
	
	def getEd2K( self ):
		"""Return the ed2k:// link associated with this met file."""
		size = self.FindTags( TAG_HANDLE_FILESIZE )[ 0 ].value;
		name = self.FindTags( TAG_HANDLE_FILENAME )[ 0 ].value;
		return "ed2k://|file|%s|%s|%s|" % ( name, size, self.getMD4() );
		
	def ReduceToData( self ):
		"""Reduce a class instance back into a stream suitable for writing to disk."""
		header_struct = "<BI16sH";
		data = struct.pack( header_struct, self.version, self.modDate, self.fileID, len( self.p_hashes ) );
		for hash in self.p_hashes:
			data += struct.pack( "<16s", hash );
		data += struct.pack( "<I", len( self.m_tags ) );
		for tag in self.m_tags:
			data += tag.ReduceToData();
		return data;
	
	def AddTag( self, tag ):
		"""Append a meta-tag instance to our list of tags."""
		self.m_tags.append( tag );
	
	def FindTags( self, tagHandle, gaptags = 0 ):
		"""Return an array of tags matching the supplied handle.
		   Tags relating to gaps do no obey the usual 'special tag' 
		   semantics, so set the flag to 1 if you are dealing with them."""
		if gaptags: return [ x for x in self.m_tags if x.name[ 0 ] == tagHandle ];
		else: return [ x for x in self.m_tags if x.name == tagHandle ];
			
	def PurgeTags( self, tagHandle, gaptags = 0 ):
		"""This is the same as FindTags, except it removes the 
		   matching tags from the meta-tag store."""
		if gaptags: self.m_tags = [ x for x in self.m_tags if x.name[ 0 ] != tagHandle ];
		else: self.m_tags = [ x for x in self.m_tags if x.name != tagHandle ];
		
class MetaTag:
	"""Class holding the data for one  meta-tag."""
	
	def __init__( self, name, value, t_type = None ):
		"""Construct a meta-tag from name, value and type."""
		self.name = name;
		self.value = value;
		if t_type == None:
			# Rudiments of Autodetection...
			if type( value ) == types.IntType:
				self.tag_type = TAG_TYPE_INTEGER;
			else:
				self.tag_type = TAG_TYPE_STRING;
		else:
			self.tag_type = t_type;
		
	def ReduceToData( self ):
		"""Reduce a meta-tag to its binary representation."""
		struct_format = "<BH%is" % len( self.name );
		if self.tag_type == TAG_TYPE_STRING:
			struct_format += "H%is" % len( self.value );
			return struct.pack( struct_format, self.tag_type, len( self.name ), self.name, len( self.value ), self.value );
		else:
			struct_format += "I";
			return struct.pack( struct_format, self.tag_type, len( self.name ), self.name, self.value );


