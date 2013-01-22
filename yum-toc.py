#!/usr/bin/python
# vim: sw=4 ts=4 noet

import	yum
import	os
import	sys
import	optparse

if __name__ == '__main__':
	me = os.path.basename( sys.argv[0] )
	report = sys.stdout
	parser = optparse.OptionParser(
		usage="usage: %prog [options]",
		version="%prog 1.0.0",
		description="""Prints summary lines for all repo packages."""
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
	pkgs = sorted( yb.pkgSack.returnPackages() )
	max_name = 7
	# max_repo = 7
	for pkg in pkgs:
		max_name = max( max_name, len(pkg.name) )
		# max_repo = max( max_repo, len(pkg.repo.name) )
	# fmt = '%%-%ds %%-%ds %%s' % (max_name, max_repo)
	fmt = '%%-%ds %%s' % max_name
	for pkg in pkgs:
		# print fmt % (pkg.name, pkg.repo.name, pkg.summary)
		print >>report,  fmt % (pkg.name, pkg.summary)
