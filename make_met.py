#!/usr/bin/python
from ed2k_metutils import *
import sys
import os
import re

if __name__ == "__main__":
	
	if len( sys.argv ) < 3:
		print "invocation: %s [temp-directory] [ed2k://...]" % sys.argv[ 0 ];
		print ;
		print "This script creates a new .part.met file in the directory of the first";
		print "argument, which represents the ed2k:// link provided as the second arg.";
		print ;
		print "Useful for adding things to your download list without actually opening ";
		print "Overnet / Donkey.";
		print ;
		sys.exit( -1 );
	
	temp_dir = sys.argv[ 1 ];
	ed2k_link = sys.argv[ 2 ];
		
	# Verify ed2k:// link.  Goddamn plague of backslashes.
	ed2k_reg = re.compile( "ed2k://\|file\|([^|]+)\|(\d+)\|([a-fA-F0-9]{32})\|" );
	matches = ed2k_reg.findall( ed2k_link );
	
	if not matches:
		print "Oh no!  This ( %s ) doesn't feel like an ed2k link!" % ( ed2k_link );
		print "ed2k file links have the form:";
		print "   ed2k://|file|<file name>|<file size>|<md4 hash>|";
		sys.exit( -1 );
	
	name, size, hash = ed2k_reg.findall( ed2k_link )[ 0 ];
	size = int( size );

	# Convert the printed hash into a byte representation.
	# Surely there's an easier way to do this.
	new_hash = "";	
	while hash:
		part = hash[ 0 : 2 ];
		hash = hash[ 2 : ];
		new_hash += chr( eval( "0x" + part ) );

	# Find the first unused download identifier.
	metfiles = [ int( x.split( "." )[ 0 ] ) for x in os.listdir( temp_dir ) if x.endswith( ".part.met" ) ];
	metfiles.sort();
	if not metfiles:
		prospective = [ 1 ];
	else:
		prospective = [ x for x in range( 1, metfiles[ -1 ] + 2 ) if x not in metfiles ];
	filename = ( "%s/%i.part.met" % ( temp_dir, prospective[ 0 ] ) ).replace ( "//", "/" );

	# Build the structure.
	new = MetFile();
	new.fileID = new_hash;
	new.AddTag( MetaTag( TAG_HANDLE_FILENAME, name ) );
	new.AddTag( MetaTag( TAG_HANDLE_FILESIZE, size ) );	
	new.AddTag( MetaTag( TAG_HANDLE_TEMP_NAME, "%i.part" % ( prospective[ 0 ] ) ) );
	new.AddTag( MetaTag( TAG_HANDLE_SOFAR, 0 ) );
	new.AddTag( MetaTag( TAG_HANDLE_GAP_START, 0 ) );
	new.AddTag( MetaTag( TAG_HANDLE_GAP_END, size - 1 ) );

	# Write it out.
	fh = open( filename, "w" );
	fh.write( new.ReduceToData() );
	fh.close();
	del( new );

	print "Wrote meta for %s to %s." % ( ed2k_link, filename );	
