#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    routines for the ExifTool - GPL - copyleft (c) 2007 Jens Diemer

    Note:
        Used the external programm 'exiftool'! (More info in 'ExifTool.py')

   http://www.jensdiemer.de/Programmieren/Python/EXIFTool/
"""
# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="wnf"
__date__ ="$12.11.2009 09:53:54$"

import os.path

import os, sys, datetime, time, shutil, stat, subprocess, pprint

# Possible Keys
EXIF_DATE_KEYS = ("Create Date", "File Modification Date/Time",)

# Must be lower case!
EXT_WHITELIST = (".pef", ".dng", ".jpg")

class WrongPathError(Exception):
    pass

def parse_exif_out(output):
    """
    return a dict from the given exiftool >output<.
    """
    result = {}
    lines = output.split("\n")
    for line in lines:
        line = line.strip()
        if line == "":
            continue
        try:
            key, value = line.split(":", 1)
        except ValueError, e:
            print "Error: %s" % e
            print "> %s" % line
            continue

        key = key.strip()
        value = value.strip()
        result[key] = value
    return result

def get_exif_data(fn, verbose = True, debug = False):
    """
    run the exiftool for the given filename (>fn<) and returned the raw output
    """

    if debug:
        print

    cmd = ["exiftool", fn]

    if debug:
        print "> %s..." % cmd,

    try:
        process = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE)
        process.wait() # warten, bis der gestartete Prozess zu Ende ist
    except KeyboardInterrupt:
        print "\n(KeyboardInterrupt)"
        sys.exit()
    except OSError, e:
        msg = (
            "%s - (cmd: '%s')\n"
            " - Have you install the external programm 'exiftool'?"
        ) % (e, cmd)
        raise OSError(msg)

    if debug:
        print "OK (returncode: %s)" % process.returncode

    output = process.communicate()[0]
    return output

def get_pics_fn(path):
    """
    Retuns a list of all files recusive from the start >path<.
    Filter the files with EXT_WHITELIST.
    """
    for dirpath, dirnames, filenames in os.walk(path):
#        print dirpath
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if not os.path.isfile(filepath):
                continue
            for ext in EXT_WHITELIST:
                if filename.lower().endswith(ext):
                    yield dirpath, filepath, filename, ext
def get_create_date(exif_data, debug=False):
    """
    return the create date as a time object. Used the EXIF_DATE_KEYS to find the
    date.
    """
    date = None
    for key in EXIF_DATE_KEYS:
        if  key in exif_data:
            date = exif_data[key]
            break
    if date == None:
        return

    if debug:
        print date

    # FIXME: Find a better way to handle a timezone offset:
    if "+" in date:
        date = date.rsplit("+",1)[0]
    if "-" in date:
        date = date.rsplit("-",1)[0]
    if "." in date:
        date = date.rsplit(".",1)[0]

    t = time.strptime(date, "%Y:%m:%d %H:%M:%S")
    if debug:
        print t

    return t


def set_file_date(fn, create_date, simulate_only):
    """
    Set the file date to >create_date<.
    """
    #print "set file date to %s..." % time2datetime(create_date),
    create_date = time.mktime(create_date)
    atime = create_date
    mtime = create_date
    if simulate_only:
        print "(simulate only. File date not modified)\n"
    else:
        try:
            os.utime(fn, (atime, mtime))
        except OSError, e:
            print "Error:", e
        #else:
        #    print "OK"

def get_file_info(path):
    """
    The main function. Set the file date from all files to the create date from the
    exif information.
    """
    if not os.path.isdir(path):
        raise WrongPathError("Given path is not valid: '%s'." % path)

    for dirpath, filepath, filename, filetyp in get_pics_fn(path):
        output = get_exif_data(filepath, verbose=False)
        data = parse_exif_out(output)

    #    pprint.pprint(data)
    #    for k,v in data.iteritems():
    #        if "date" in k.lower():
    #            print k,v

        create_date = get_create_date(data)#, debug=True)
        if create_date == None:
            print "No date information found in exif data!"
            print "current file: %s skip." % filepath
            continue

        yield dirpath, filepath, filename, filetyp, create_date


def zeittodateiname(c):
    s = "%4.4i_%2.2i_%2.2i" % (c.tm_year,c.tm_mon,c.tm_mday)
    s = "%s_%2.2i_%2.2i_%2.2i" % (s,c.tm_hour,c.tm_min,c.tm_sec)
    return s


def jpgrename(source_path, vorsilbe, out, simulate_only):
    """
    Alle jpg-Dateien des Verzeichnisses werden umbenannt
    Der Dateiname besteht aus YYYY_MM_DD_HH_MM_SS der Exifdaten des Bildes
    Falls es Dateien mit der gleichen Zeit gibt, wird eine laufende Nummer angehaengt.
    """
    counter = 0

    def simulate():
        if simulate_only:
            msg = "(simulate only.)"
            print msg
            out.write(msg)
            return True
        return False

    for dirpath, filepath, filename, filetyp, create_date in get_file_info(source_path):
#        out.write("source file: %s" % filename)
#        out.write("source file: %s" % filepath)
#        out.write("source file: %s" % dirpath)
#        debug_file_stat(fn)
#        out.write("create date from EXIF: %r" % create_date)
        dn = zeittodateiname(create_date)
        ziel = "%s/%s_%s%s" % (dirpath,vorsilbe, dn,filetyp)
        if filepath<>ziel:
            i=0;
            while os.path.isfile(ziel):
              i += 1
              ziel = "%s/%s_%s_%2.2i%s" % (dirpath,vorsilbe, dn,i,filetyp)
#              out.write("Eine Sekunde spaeter von: %s nach %s" % (filename,ziel))

            out.write("umbenennen von: %s nach %s" % (filename,ziel))

            if not simulate_only:
                os.renames(filepath, ziel)
                set_file_date(ziel, create_date, simulate_only)
                counter += 1

    out.write("%s Datei(en) umbenannt." % counter)


if __name__ == "__main__":
    class Out(object):
        def write(self, txt):
            print txt

    source_path = "."
    dest_path = "."
#    source_path = "/tmp/2009-11-11"
#    dest_path = "/tmp/2009-11-11"
    out = Out()
    simulate_only = False
    move_files = True
    copy_files = False
    vorsilbe = "ncc"

    jpgrename(source_path,vorsilbe, out, simulate_only)
