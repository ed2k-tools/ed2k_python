#!/usr/bin/python
from ed2k_metutils import *
import os
import stat

try:
	# Not sure if Curses can be invoked everywhere.
	import curses
	win = curses.initscr();
	None, WIDTH = win.getmaxyx();
	curses.endwin();
except:
	WIDTH = 80;

if __name__ == "__main__":
	# Here's an example to cut and keep.
	#
	# Simple profiling of the download directory.  I use this to
	# see how much data I actually got from night to night.
	
	if len( sys.argv ) < 2:
		print "invocation: %s < <x.part.met> [x.part.met ...] | <temp_dir> >" % sys.argv[ 0 ];
		print
		print "This program will show the amount downloaded vs. the total size "
		print "for the .part.met files or directory listed on the command line." 
		sys.exit( -1 );
	
	total_size = total_down = 0;
	
	sta = os.stat( sys.argv[ 1 ] )[ 0 ];
	if stat.S_ISDIR( sta ):
		mets = [ "%s%s" % ( sys.argv[ 1 ], x ) for x in os.listdir( sys.argv[ 1 ] ) if x.endswith( ".met" ) ];
	else:
		mets = sys.argv[ 1 : ];
	
	for met_file in mets:
		
		fh = open( met_file, "r" );
		data = fh.read();
		fh.close();
		
		met_data = MetFile( data );
		del( data );
		
		# We're interested in the name, the total size, and some kind of... anti-gapping.
		size = met_data.FindTags( TAG_HANDLE_FILESIZE )[ 0 ].value;
		name = met_data.FindTags( TAG_HANDLE_FILENAME )[ 0 ].value;
		
		# Set the total downloaded to the file size.
		down = size;
		
		gap_starts = met_data.FindTags( TAG_HANDLE_GAP_START, 1 );
		gap_ends   = met_data.FindTags( TAG_HANDLE_GAP_END, 1 );
		gaps = {};
		
		# Build gap lists.
		for gap in gap_starts:
			gap_id = gap.name[ 1 : ];
			gaps[ gap_id ] = gap.value;
		for gap in gap_ends:
			gap_id = gap.name[ 1 : ];
			gaps[ gap_id ] = ( gaps[ gap_id ], gap.value );
			gap_length = gaps[ gap_id ][ 1 ] - gaps[ gap_id ][ 0 ];
			# Adjust downloaded figure.
			down -= gap_length;
		
		total_size += size;
		total_down += down;		

		# If we have two endcaps, that leaves 78 characters to represent "size" bytes.
		bytes_per_char = size / ( WIDTH - 2 );
		bar = "#" * ( WIDTH - 2 );
		for gap in gaps:
			gap_start, gap_end = gaps[ gap ];
			char_gap_start = gap_start / bytes_per_char;
			char_gap_end = gap_end / bytes_per_char;
			bar = bar[ : char_gap_start ] + " " * ( char_gap_end - char_gap_start ) + bar[ char_gap_end : ];
				
		# Print out our summary.  Limit the filenames.
		sizestring = " - %s - %iK of %iK" % ( met_file.split( "/" )[ -1 ], down / 1024, size / 1024 );
		max_name_size = WIDTH - len( sizestring );
		if len( name ) < max_name_size:
			name += " " * ( max_name_size - len( name ) );
		else:
			name = name[ : max_name_size ];
		print "%s%s" % ( name, sizestring );
		print "[%s]" % bar;
		print 
		del( met_data );
	print "Totals: %sK of %sK" % ( total_down / 1024, total_size / 1024 );
