#!/usr/bin/env python3
# vim: sw=4 ts=4 noet

import	argparse
import	hawkey
import	os
import	socket
import	sys

try:
	from version import Version
except:
	Version = '0.0.0'

def	is_even( n ):
	n = int( n )
	return ((n/2)*2) == n

def	is_odd( n ):
	return not is_even( n )

def	make_even( n ):
	return (n+1) if is_odd( n ) else n

def	make_odd( n ):
	return (n+1) if is_even( n ) else n

if __name__ == '__main__':
	me      = os.path.basename( sys.argv[0] )
	if me == '__init__':
		me = 'yum-toc'
	prog   = os.path.splitext( me )[0]
	parser = argparse.ArgumentParser(
		prog        = prog,
		description = """Prints summary lines for all repo packages."""
	)
	NCOUNT=5
	parser.add_argument(
		'-n',
		'--every',
		dest    = "spacing",
		default = NCOUNT,
		help    = f'marker every N (default: {NCOUNT}) lines',
		metavar = "N",
		type    = int
	)
	#
	parser.add_argument(
		'-o',
		'--out',
		dest    = "ofile",
		help    = "write output to FILE",
		metavar = "FILE",
		default = None
	)
	parser.add_argument(
		'-s',
		'--system',
		dest   = 'with_hostname',
		action = 'store_true',
		help   = 'host-specific prefix',
	)
	#
	parser.add_argument(
		'--version',
		action = 'version',
		version = Version,
		help = '{0} Version {1}'.format(
			prog,
			Version
		)
	)
	opts = parser.parse_args()
	#
	if opts.with_hostname:
		for host in [
			os.getenv( 'HOST' ),
			os.getenv( 'HOSTNAME' ),
			socket.gethostname(),
			'localhost',
		]:
			if host and host != '':
				break
		opts.ofile = '-'.join([
			opts.ofile if opts.ofile else 'all',
			host
		])
	if opts.ofile:
		try:
			sys.stdout = open( opts.ofile, 'wt' )
		except:
			print(
				"%s: cannot open '%s' for writing." % (
					me,
					opts.ofile
				),
				file = sys.stderr
			)
			raise
	#
	sack = hawkey.Sack( make_cache_dir = True )
	sack.enable_repo( '*' )
	sack.load_system_repo( build_cache = True )
	query = hawkey.Query( sack ).filter(
#		reponame = hawkey.SYSTEM_REPO_NAME,
		name__glob = '*'
	)
	pkgs = [
		pkg for pkg in query
	]
	#
	line_width = os.getenv( 'COLUMNS' )
	if not line_width:
		line_width = 80
	line_fmt = '{{0:{0}.{0}}}'.format( line_width )
	#
	max_name = make_odd(
		max(
			map(
				len,
				[ pkg.name for pkg in pkgs ]
			)
		)
	)
	#
	if False:
		max_reponame = max(
			map(
				len,
				[ pkg.reponame for pkg in pkgs ]
			)
		)
	rpm_fmt = '{{0:{0}.{0}s}}  {{1}}'.format(
		max_name,
	)
	if False:
		for pkg in sorted( q[0:5] ):
	#		print 'dir(pkg)={0}'.format( dir( pkg ) )
			line = rpm_fmt.format(
				str( pkg.name ),
				str( pkg.reponame ),
				str( pkg.summary )
			)
			print( line_fmt.format( line ) )
		exit( 1 )
	#
	if False:
		for pat in [ '-debuginfo', '-devel' ]:
			pkgs[:] = (
				pkg for pkg in pkgs if not pkg.name.endswith( pat )
			)
	#
	lineno = 0
	prev = None
	for pkg in sorted(
		pkgs,
		key = lambda p : p.name.lower()
	):
		if pkg.name != prev:
			try:
				summary = pkg.summary.encode(
					'ascii', 'replace'
				).decode( 'utf-8')
			except:
				summary = '*** TBD ***'
				raise
			name = pkg.name
			if is_odd( len(name) ):
				name += ' '
			if (lineno % opts.spacing) == 0:
				padding = ' .' * int(
					(max_name - len(name)) / 2
				)
				name += padding
			line = rpm_fmt.format(
				name,
#				pkg.reponame,
				summary,
			)
			print( line_fmt.format( line ) )
			prev = pkg.name
			lineno += 1
