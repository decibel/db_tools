#!/usr/bin/env python
"""Create symlinks in a project that point to our relevant tools.
"""

__author__ = "Jim Nasby"
__version__ = "0.1.0"
__copyright__ = "Copyright 2016, Jim Nasby"
__license__ = "BSD 3-clause"
__maintainer__ = "Jim Nasby"
__email__ = "Jim.Nasby@BlueTreble.com"
__status__ = "Development"

import sys
import argparse
import os
import os.path

import glob
import fnmatch
import re

VERBOSITY = 0

def walk_dir(root, includes=None, excludes=None):
    """Walk and filter a directory tree by wildcards.

    :param includes: A list of file wildcards to include.
        If `None`, then all files are (potentially) included.
    :param excludes: A list of file and directory wildcards to exclude.
        If `None`, then no files or directories are excluded.

    Original at https://www.metabrite.com/devblog/posts/mocking-and-filtering-pythons-oswalk/
    """
    # Transform glob patterns to regular expressions
    includes_re = re.compile(
        '|'.join([fnmatch.translate(x) for x in includes])
        if includes else '.*')
    excludes_re = re.compile(
        '(^|/)(' + '|'.join([fnmatch.translate(x) for x in excludes]) + ')'
        if excludes else '$.')

    v_out(3, 'includes_re = ' + includes_re.pattern)
    v_out(3, 'excludes_re = ' + excludes_re.pattern)

    for top, dirnames, filenames in os.walk(root, topdown=True):
        # exclude directories by mutating `dirnames`
        dirnames[:] = [
            d for d in dirnames
                if not excludes_re.search(os.path.join(top, d))]

        for d in dirnames:
            yield os.path.join(top, d)

        # filter filenames
        pathnames = [os.path.join(top, f) for f in filenames
                     if includes_re.match(f)]
        pathnames = [p for p in pathnames if not excludes_re.search(p)]

        for p in pathnames:
            yield p

def make_links(input_dir, output_dir, dry_run=False):
    if not os.path.isdir(input_dir):
        raise "input_dir (%s) must be a directory" % input_dir
    if not os.path.isdir(output_dir):
        raise "output_dir (%s) must be a directory" % output_dir

    # This wouldn't do what we wanted if any of the inputs weren't already directories
    common = os.path.commonprefix([input_dir, output_dir])

    v_out(1, 'common file path: ' + common)

    #dirfd = os.open(common, os.O_DIRECTORY)

    for p in walk_dir(input_dir, excludes=['/LICENSE', '.*', 'make_link*']):
        # This is p relative to input_dir
        relative = os.path.relpath(p, input_dir)

        dest = os.path.join(output_dir, relative)

        if os.path.isdir(p) and not os.path.islink(p):
            v_out(3, "p = '%s', relative = '%s'" % (p, relative))
            if dry_run:
                print 'creating directory ' + dest
            else:
                v_out(1, 'creating directory ' + dest)
                os.mkdir(dest, 0777)
        else:
            # This is the original source relative to the destination
            source_rel_to_destdir = os.path.relpath(p, os.path.dirname(dest))

            v_out(3, "p = '%s', relative = '%s', dest = '%s'" % (p, relative, dest))
            if dry_run:
                print 'creating symlink from %s to %s' % (source_rel_to_destdir, dest)
            else:
                v_out(2, 'creating symlink from %s to %s' % (source_rel_to_destdir, dest))
                os.symlink(source_rel_to_destdir, dest)

def v_out(level, str):
    if VERBOSITY >= level:
        print (' ' * level) + str

def main(argv=None):
    args = parse_args(argv)

    global VERBOSITY
    VERBOSITY = args.verbosity

    print "Creating symlinks in %(output_dir)s from %(input_dir)s" % vars(args)

    make_links(args.input_dir, args.output_dir, args.dry_run)

def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('-i', '--input_dir', default=sys.path[0])
    parser.add_argument('-d', '--dry_run', action='store_true',
            help="don't actually create links, just print what would be done")
    parser.add_argument('output_dir', nargs='?', default=os.getcwd())
    parser.add_argument('-v', '--verbosity', action='count',
            help='increase output verbosity')

    return parser.parse_args(argv)

if __name__ == "__main__":
    main()

# vi: expandtab ts=4 sw=4
