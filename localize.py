#!/usr/bin/env python27

"""Copy an elm-lang module with Native code, converted munged names.

Native code in elm-lang modules uses global variable names that have a prefix
that has to match the username and repo name of the module. For example, native
code in a module whose repository (in its elm-package.json file) is
"https://github.com/joeschmoe/elm-coolstuff.git" must have global variable names
that start with "_joeschmoe$elm_coolstuff$".

To use such code in another project we have to convert those global variable
names to match the user/repo name of that project. That's what this script does:
it copies a directory containing an elm-lang module, modifying native javascript
code to convert those names as needed.

"""


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
    """ Copy inroot to outroot, converting elm JS-native code on the way."""
    srcPkgFileName = os.path.join(inroot, "elm-package.json")
    srcname = getName(srcPkgFileName)
    if not srcname:
        logger.error("failed to find user/repo name in %s", srcPkgFileName)
        return

    # (assume that we are running in the root directory of project that will use
    # the converted module)
    dstPkgFileName = "elm-package.json"
    dstname = getName(dstPkgFileName)
    if not dstname:
        logger.error("failed to find user/repo name in %s", dstPkgFileName)
        return

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
            handleFile(srcname, dstname, root, file, outdir)


def handleFile(srcname, dstname, root, file, outdir):
    """ Copy a single file, converting if necesary. """
    trace("handleFile(%s, %s, %s)", root, file, outdir)
    if root.endswith("/Native") and file.endswith(".js"):
        convertFile(srcname, dstname, root, file, outdir)
    else:
        shutil.copy(os.path.join(root, file), outdir)


def convertFile(srcname, dstname, root, file, outdir):
    """ Convert a single file, changing the munged JS variable names. """
    trace("convertFile(%s, %s, %s, %s, %s)", srcname, dstname, root, file, outdir)

    user, repo = srcname.split("/")
    patternstring = r"_%s\$%s\$" % (user, repo)
    pattern = re.compile(patternstring)

    user2, repo2 = dstname.split("/")
    replacement = "_%s$%s$" % (user2, repo2)
    replacement = re.sub("-", "_", replacement)

    with open(os.path.join(outdir, file), "w+") as outfile:
        with open(os.path.join(root, file)) as infile:
            for line in infile:
                outline = pattern.sub(replacement, line)
                outfile.write(outline)
                

def getName(pkgFileName):
    """Extract the username/reponame value from the elm-package.json file."""
    try:
        with open(pkgFileName) as pkgFile:
            pattern = re.compile(r'//github\.com/(.*)\.git')
            for line in pkgFile:
                m = pattern.search(line)
                if m:
                    name = m.group(1)
                    trace("found src user/repo name = %s", name)
                    return name
    except Exception as e:
        logger.exception("failed reading %s", pkgFileName)

    return None


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
