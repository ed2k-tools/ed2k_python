#!/usr/bin/python
from ed2k_metutils import *

if __name__ == "__main__":
	# Here's an example to cut and keep.
	#
	# Simple profiling of the download directory.  I use this to
	# see how much data I actually got from night to night.
	
	if len( sys.argv ) < 2:
		print "invocation: %s [-quiet] [x.part.met ...]" % sys.argv[ 0 ];
		print
		print "This program will show the amount downloaded vs. the total size "
		print "for the .part.met files listed on the command line.  It relies on"
		print "the 0x08 'sofar' tag being set however - mac users check out the"
		print "documentation for fix_sofar.py!"
		print
		print "If you pass it the argument '-quiet' as the first argument, it will"
		print "only print the grand total.  Useful to see how much you got since"
		print "last time you checked."
		print
		sys.exit( -1 );
	
	total_size = 0;
	total_down = 0;	

	if sys.argv[ 1 ] == '-quiet':
		sys.argv.remove( '-quiet' );
		quiet = 1;
	else:
		quiet = 0;
	
	for met_file in sys.argv[ 1 : ]:
		
		fh = open( met_file, "r" );
		data = fh.read();
		fh.close();
		
		met_data = MetFile( data );
		del( data );
		
		size = met_data.FindTags( TAG_HANDLE_FILESIZE )[ 0 ].value;
		down = met_data.FindTags( TAG_HANDLE_SOFAR )[ 0 ].value;
		name = met_data.FindTags( TAG_HANDLE_FILENAME )[ 0 ].value;
		
		total_size += size;
		total_down += down;
		
		if quiet == 0:
			down2 = down / 1024;
			size2 = size / 1024;
			print "%s%s%iK/%iK ( %s )" % ( name, ' ' * ( 80 - len( name ) - len( str( down2 ) ) - len( str( size2 ) ) - 1 ), down2, size2, met_file );
		
		del( met_data );
	
	if quiet == 0: 
		print
	total_size /= 1024;
	total_down /= 1024;
	print "Total:%s%iK/%iK" % ( ' ' * ( 73 - len( str( total_down ) ) - len( str( total_size ) ) ), total_down, total_size );
