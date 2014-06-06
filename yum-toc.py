#!/usr/bin/python
# vim: sw=4 ts=4 noet

import	yum
import	os
import	sys
import	optparse

def	is_even( n ):
	n = int( n )
	return ((n/2)*2) == n

def	is_odd( n ):
	return not is_even( n )

def	make_even( n ):
	if is_odd( n ):
		return (n+1)
	return n

def	make_odd( n ):
	if is_even( n ):
		return n+1
	return n

if __name__ == '__main__':
	me = os.path.basename( sys.argv[0] )
	report = sys.stdout
	parser = optparse.OptionParser(
		usage="usage: %prog [options]",
		version="%prog 1.0.0",
		description="""Prints summary lines for all repo packages."""
	)
	NCOUNT=5
	parser.add_option(
		'-n',
		'--line-every',
		dest="spacing",
		default=NCOUNT,
		help="write marker line every COUNT lines; default is %d lines" % NCOUNT,
		metavar="COUNT",
		type="int"
	)
	parser.add_option(
		'-o',
		'--out',
		dest="ofile",
		help="write output to FILE",
		metavar="FILE",
		default=None
	)
	(options, args) = parser.parse_args()
	if options.ofile is not None:
		try:
			report = open( options.ofile, 'wt' )
		except Exception, e:
			print >>sys.stderr, "%s: cannot open '%s' for writing." % (
				me,
				options.ofile
			)
			raise e
	#
	yb = yum.YumBase()
	yb.conf.cache = os.geteuid() != 0
	#
	from urlgrabber.progress import TextMeter
	sys.path.insert( 0, '/usr/share/yum-cli' )
	import output
	if sys.stdout.isatty():
		yb.repos.setProgressBar( TextMeter(fo=sys.stdout) )
		yb.repos.callback = output.CacheProgressCallback()
		yumout = output.YumOutput()
		freport = ( yumout.failureReport, (), {} )
		yb.repos.setFailureCallback( freport )
	yb.repos.doSetup()
	#
	pkgs = sorted( yb.pkgSack.returnPackages(), key = lambda p : p.name.lower() )
	max_name = 6
	for pkg in pkgs:
		max_name = max( max_name, len(pkg.name) )
	max_name = make_odd( max_name )
	fmt = '%%-%ds%%s   (%%s)' % max_name
	prev = None
	lineno = 0
	for pkg in pkgs:
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
			if (lineno % 5) == 0:
				padding = ' .' * (
					(max_name - len(name)) / 2
				)
				name += padding
			print >>report,  fmt % (
				name,
				summary,
				pkg.repo.name
			)
			prev = pkg.name
			lineno += 1
