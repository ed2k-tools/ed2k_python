#!/usr/bin/python
from ed2k_metutils import *

if __name__ == "__main__":
	# Here's an example to cut and keep.
	#
	# Overnet MacOSX 0.46.1 seems to annihilate the SOFAR tag ( 0x08 )
	# whenever it exits ( more likely it does it at load time and never
	# remembers to update the value on disk... ).
	#
	# This will undo the damage.
	
	if len( sys.argv ) < 2:
		print "invocation: %s [ -f ] <x.part.met> [x.part.met ...]" % sys.argv[ 0 ];
		print
		print "Some versions of Overnet on MacOSX seem not to write the 0x08 'sofar' tag"
		print "on exiting, this gives the appearance that the next time you boot overnet,"
		print "nothing has been downloaded.  It's only cosmetic, however."
		print
		print "If you want to create new .met files with this 'bug' corrected, run this"
		print "program with the affected .met files as the command line arguments.  You"
		print "will get new .met files titled X.new, where X was the original .part.met"
		print "file.  Copy these over the top of your originals if you're sure thats what"
		print "you want to do."
		print
		print "-f as the first argument, 'force', will directly overwrite the files."
		print "It is unsupported.  If it breaks your files, don't come to me about it."
		print
		print "Of course, Overnet will re-break these files on its next exit.  You'll"
		print "need to run this program a lot to keep everything setup."
		print
		sys.exit( -1 );
	
	# Throw away argv[ 0 ].
	args = sys.argv[ 1 : ];

	if args[ 0 ] == "-f":
		force = 1;
		args = args[ 1: ];
	else:
		force = 0;
	
	for met_file in args:
		
		fh = open( met_file, "r" );
		data = fh.read();
		fh.close();
		
		met_data = MetFile( data );
		del( data );
		
		length = met_data.FindTags( TAG_HANDLE_FILESIZE )[ 0 ].value;
		
		# Restructure SOFAR - Build gap lists.
		gap_starts = met_data.FindTags( TAG_HANDLE_GAP_START, 1 );
		gap_ends   = met_data.FindTags( TAG_HANDLE_GAP_END, 1 );
		
		gaps = {};
		for g_e in gap_ends:
			gap_id = g_e.name[ 1 : ];
			gaps[ gap_id ] = g_e.value;	
		for g_s in gap_starts:
			gap_id = g_s.name[ 1 : ];
			gaps[ gap_id ] -= g_s.value;
			
		so_far = length;
		for gap in gaps.keys():
			so_far -= gaps[ gap ];
		
		print "%s: %s" % ( met_file, met_data.FindTags( TAG_HANDLE_FILENAME )[ 0 ].value );
		print "MD4: %s" % ( met_data.getMD4() );
		print "Obtained size / total: %i / %i" % ( so_far, length );
		
		met_data.PurgeTags( TAG_HANDLE_SOFAR );
		met_data.AddTag( MetaTag( TAG_HANDLE_SOFAR, so_far, TAG_TYPE_INTEGER ) );
		if force: fh = open( "%s" % met_file, "w" );
		else: fh = open( "%s.new" % met_file, "w" );
		fh.write( met_data.ReduceToData() );
		fh.close();
		del( met_data );
