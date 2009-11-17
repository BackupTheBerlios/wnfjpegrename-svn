#!/usr/bin/python
# -*- coding: utf-8 -*-
import time

def zeittodateiname(c):
    """
    Diese Funkton erzeugt aus c vom Typ ??? einen String YYYY_MM_DD__HH_MM_SS
    """
    s = "%4.4i_%2.2i_%2.2i" % (c.tm_year,c.tm_mon,c.tm_mday)
    s = "%s_%2.2i_%2.2i_%2.2i" % (s,c.tm_hour,c.tm_min,c.tm_sec)
    return s

if __name__ == "__main__":
    # d ist der Exif-Datum string aus einem jpeg-bild einer Kamera
    # Den Wert c ergibt sich aus der Exif-Date-Auslesefunktion
    d = "2009:11:11 19:21:49"
    c = time.strptime(d, "%Y:%m:%d %H:%M:%S")
    s = zeittodateiname(c)
    print d
    print c
    print s
