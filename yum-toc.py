#!/usr/bin/python
# vim: sw=4 ts=4 noet

import	hawkey
import	argparse
import	os
import	sys

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
	prog    = os.path.splitext( me )[0]
	version = '2.0.0'
	parser  = argparse.ArgumentParser(
		prog        = prog,
		version     = version,
		description = """Prints summary lines for all repo packages."""
	)
	NCOUNT=5
	parser.add_argument(
		'-n',
		'--line-every',
		dest    = "spacing",
		default = NCOUNT,
		help    = 'write marker line every {0} lines'.format( NCOUNT ),
		metavar = "COUNT",
		type    = int
	)
	parser.add_argument(
		'-o',
		'--out',
		dest    = "ofile",
		help    = "write output to FILE",
		metavar = "FILE",
		default = None
	)
	opts = parser.parse_args()
	if opts.ofile:
		try:
			sys.stdout = open( opts.ofile, 'wt' )
		except Exception, e:
			print >>sys.stderr, "%s: cannot open '%s' for writing." % (
				me,
				opts.ofile
			)
			raise e
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
			print line_fmt.format( line )
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
				summary = pkg.summary.decode(
					'utf-8', 'replace'
				).encode(
					'ascii', 'replace'
				)
			except:
				summary = '*** TBD ***'
			name = pkg.name
			if is_odd( len(name) ):
				name += ' '
			if (lineno % opts.spacing) == 0:
				padding = ' .' * (
					(max_name - len(name)) / 2
				)
				name += padding
			line = rpm_fmt.format(
				name,
#				pkg.reponame,
				summary,
			)
			print line_fmt.format( line )
			prev = pkg.name
			lineno += 1
