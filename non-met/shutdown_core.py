#!/usr/bin/python

# A python program to shutdown an ed2k core.
import sys;
import struct;
import socket;

HEADER_BYTE = 0xE3;
OP_LOGIN    = 0x64;
OP_SHUTDOWN = 0x65;

def make_login_packet( username, password ):
	"""Create a authentication packet."""
	# This looks like so:
	#	<length of username: 16bit><username><length of password: 16 bit><password>
	packet = struct.pack( "<BH%isH%is" % ( len( username ), len( password ) ), OP_LOGIN, len( username ), username, len( password ), password );
	# Hss hss.
	return packet;

def make_shutdown_packet( ):
	"""Create a shutdown packet."""
	packet = struct.pack( "<B", OP_SHUTDOWN );
	return packet;

def make_connection( hostname, port = 4663 ):
	"""Make a socket to the core."""
	connection = socket.socket();
	connection.connect( ( hostname, port ) );
	return connection;

def send_packet( connection, packet ):
	"""Send the packet to connection."""
	new_packet = struct.pack( "<BI%is" % len( packet ), HEADER_BYTE, len( packet ), packet );
	connection.send( new_packet );

if __name__ == '__main__':
	if len( sys.argv ) < 4:
		print "usage: %s <host[:port]> <uname> <pass>" % sys.argv[ 0 ];
		sys.exit( -1 );
	
	# Split out the hostname if necessary.
	t = sys.argv[ 1 ].split( ":" );
	if len( t ) == 1:
		hostname = t[ 0 ];
		port = 4663;
	else:
		hostname, port = t;
	username, password = sys.argv[ 2 : 4 ];
	
	# Make core connection.
	connection = make_connection( hostname, port );
	
	send_packet( connection, make_login_packet( username, password ) );
	send_packet( connection, make_shutdown_packet() );
	
	# Clean up.
	connection.close();
	
	sys.exit( 0 );	

