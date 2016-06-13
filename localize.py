#!/usr/bin/env python27

import argparse
import logging
import os
import re
import shutil
import sys


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('localize')

trace = logger.debug


def convertDir(inroot, outroot):
    os.makedirs(outroot)

    for root, dirs, files in os.walk(inroot):
        trace("root, dirs, files = %s, %s, %s", root, dirs, files)
        for excludedir in [".git", "elm-stuff"]:
            if excludedir in dirs:
                dirs.remove(excludedir)

        reldir = root[len(inroot):]
        if reldir.startswith("/"):
            reldir = reldir[1:]

        outdir = outroot
        if reldir != "":
            outdir = os.path.join(outroot, reldir)
            os.mkdir(outdir)

        for file in files:
            handleFile(root, file, outdir)


def handleFile(root, file, outdir):
    trace("handleFile(%s, %s, %s)", root, file, outdir)
    if root.endswith("/Native") and file.endswith(".js"):
        convertFile(root, file, outdir)
    else:
        shutil.copy(os.path.join(root, file), outdir)


def convertFile(root, file, outdir):
    trace("convertFile(%s, %s, %s)", root, file, outdir)

    pattern = re.compile(r"_fredcy\$storage\$")

    with open(os.path.join(outdir, file), "w+") as outfile:
        with open(os.path.join(root, file)) as infile:
            for line in infile:
                outline = pattern.sub("_fredcy$elm_tangram_svg$", line)
                outfile.write(outline)
                

def main():
    parser = argparse.ArgumentParser(description='Convert native module')
    parser.add_argument('indir', help='directory name of module to convert')
    parser.add_argument('outdir', help='new directory for converted code')
    parser.add_argument('--debug', '-d', action='store_true')
    args = parser.parse_args()
    
    if args.debug:
        logger.setLevel(level=logging.DEBUG)

    if not os.path.isdir(args.indir):
        logger.error("%s is not a directory", args.indir)
        sys.exit(1)

    if os.path.isdir(args.outdir):
        logger.error("output directory %s already exists", args.outdir)
        sys.exit(2)

    sys.stdout.write("Reading %s, creating %s\n" % (args.indir, args.outdir))

    convertDir(args.indir, args.outdir)


if __name__ == "__main__":
    main()
