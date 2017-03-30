#!/usr/bin/env python
from __future__ import absolute_import,  unicode_literals, print_function


import os
import sys
from itertools import repeat
from multiprocessing import Pool
import hashlib

PY3 = sys.version_info >= (3,0,0)

__author__ = 'Oliver Lindemann <oliver.lindemann@uni-potsdam.de>'
__version__ = '0.5'

def string_encode(s, enc='utf-8', errors='strict'):
    """unicode to bytestring"""

    if (PY3 and isinstance(s, bytes)) or \
        (not PY3 and isinstance(s, str)):
        return s
    return s.encode(enc, errors)

def string_decode(s, enc='utf-8', errors='strict'):
    """bytestring to unicode"""

    if (PY3 and isinstance(s, str)) or (not PY3 and isinstance(s, unicode)):
        return s
    if (PY3 and isinstance(s, bytes)) or (not PY3 and isinstance(s, str)):
        return s.decode(enc, errors)


def get_file_list(path, file_extensions=()):
    """ TODO
    returns relative to path
    """

    abspath = os.path.abspath(path) # ensure good path format
    rtn = []
    for root, _, files in os.walk(abspath):
        root = root.replace(abspath, ".")
        if len(root)>0 and root[0] == os.path.sep:
            root = root[1:]
        for name in files:
            ext = list(filter(lambda x: name.endswith(x), file_extensions))
            if len(file_extensions)==0 or len(ext)>0:
                rtn.append(os.path.join(root, string_decode(name)))
    return rtn


class HashAlgorithm(object):

    def __init__(self, algorithm="sha1"):
        # TODO check type
        self.algorithm = algorithm
        suppored = {"md5" : hashlib.md5,
                 "sha1": hashlib.sha1,
                 "sha224": hashlib.sha224,
                 "sha256" : hashlib.sha256,
                 "sha384" : hashlib.sha384,
                 "sha512" : hashlib.sha512}

        if algorithm in suppored:
            self.hash_fnc = suppored[algorithm]
        else:
            raise RuntimeError("{0} is an unknown hash algorithm. Please use {1}".format(
                        algorithm, suppored.keys()))

    def file_hash(self, path_to_file):
        fl_hash = self.hash_fnc()
        with open(path_to_file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                fl_hash.update(chunk)
        return fl_hash.hexdigest()

    def hash(self, value):
        return self.hash_fnc(value).hexdigest()

def _map_file_hash(parameter):
    hash_algorithm = parameter[3]
    hash = hash_algorithm.file_hash(os.path.join(parameter[0], parameter[1]))

    if parameter[2]:
        sys.stdout.write(".")
        sys.stdout.flush()
    return (parameter[1], hash)



class HashData(object):

    def __init__(self, path=None, file_extensions = (), algorithm="sha1",
                 verbose=False, multiprocessing=False):

        """path to file of folder
        TODO"""

        self._hash_list = {}
        self.hash_algorithm = HashAlgorithm(algorithm)

        if path is not None:
            self.create_hash_list(path, file_extensions, verbose,
                                  multiprocessing)


    def create_hash_list(self, path, file_extensions = (), verbose=False,
                         multiprocessing = False):
        """
        TODO
        """

        self._hash_list = {}
        if verbose:
            sys.stdout.write("Creating hash list ")
            sys.stdout.flush()

        if os.path.isdir(path):
            map_iterator = zip(repeat(path),
                            get_file_list(path=path, file_extensions=file_extensions),
                            repeat(verbose),
                            repeat(self.hash_algorithm))

            if multiprocessing:
                tmp = Pool().map(_map_file_hash, map_iterator)
            else:
                tmp = map(_map_file_hash, map_iterator)

            self._hash_list = {k: v for k, v in tmp} # list to dict

        else: # single file
            self._hash_list = {path: self.hash_algorithm.file_hash(file_name=path)}

        if verbose:
            print(" ")
            print("    {0} files processed".format(len(self._hash_list)))
            print("    master hash: {0} (short: {1})".format(self.master_hash, \
                                                                  self.master_hash_short))

    @property
    def files(self):
        return list(self._hash_list.keys())

    @property
    def master_hash(self):
        """ TODO
        """

        if len(self._hash_list) > 1:
            return self.hash_algorithm.hash(string_encode(self.to_string(sort_by_hash=True)))
        elif len(self._hash_list) == 1:
            return self._hash_list.values()[0] # the fingerprint of the single file
        else:
            return "-" * 40


    @ property
    def hash_list(self):
        return self._hash_list

    def __str__(self):
        return self.to_string()

    def to_string(self, sort_by_hash=False):
        """Checksums as text string

        Each line of the text comprises fingerprint and file name
        separated by single space

        Note
        ----

        apply fingerprint_dict() to get a dictionary representation
        """


        hashes = map(lambda x : u"{0}  {1}".format(self._hash_list[x], x),
                        self._hash_list)
        if sort_by_hash:
            hashes = sorted(hashes)

        return "\n".join(hashes) + "\n"

    @property
    def master_hash_short(self):
        """ TODO
        """

        return self.master_hash[:7]


    def save(self, outfile):
        """
        TODO
        """

        with open(outfile, "wb+") as ofl:
            ofl.write(string_encode(self.to_string()))

    def load(self, filename):
        """returns dict"""
        self._hash_list = {}
        with open(filename, "r") as fl:
            for l in fl:
                tmp = string_decode(l).strip().split("  ")
                if len(tmp) == 2:
                    self._hash_list[tmp[1]] = tmp[0]

    def compare(self, reference, verbose=False):
        """ TODO

        reference: data_fingerprint

        returns comparison dictionary
        """

        rtn = {}

        if not isinstance(reference, HashData):
            return {}

        rtn["not_matching"] = []
        rtn["missing"] = []
        rtn["matching"] = []

        for flname in self._hash_list:
            if flname not in reference.files:
                rtn["not_matching"].append(flname)
            elif self._hash_list[flname] != reference._hash_list[flname]:
                rtn["not_matching"].append(flname)
            else:
                rtn["matching"].append(flname)

        for flname in reference.files:
            if flname not in self.files:
                rtn["missing"].append(flname)

        rtn["n_conflicts"] = len(rtn["not_matching"]) + len(rtn["missing"])
        if verbose:
            if rtn["n_conflicts"]> 0:
                print("Number of conflicts: {} ".format(rtn["n_conflicts"]))
                if len(rtn["missing"])> 0:
                    print(" missing:\n  " + "\n  ".join(rtn["missing"]))
                if len(rtn["not_matching"])> 0:
                    print(" not matching:\n  " + "\n  ".join(rtn["not_matching"]))
            else:
                print("## No conflicts!")

        return rtn


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description="usage: data_fingerprint.py [options] <PATH>",
                        epilog="(c) O. Lindemann")

    parser.add_argument("PATH", nargs='?', default=None,
                        help="The path to the data folder or file")

    parser.add_argument("-g", "--gui", dest="gui",
                        action="store_true",
                        help="start graphical user interface (GUI)",
                        default = False)

    parser.add_argument("-v", "--verbose", dest="verbose",
                  action="store_true",
                  help="verbose output",
                  default=False)

    parser.add_argument("-l", "--hashlist", dest="hashlist",
                  action="store_true",
                  help="display hash list",
                  default=False)

    parser.add_argument("-a", "--algorithm", dest="algorithm",
                        action="store",
                        help="hash algorithm. The following algorithm are supported. " +
                             "sha1 (Default), sha224, sha256, sha512, md5.",
                        metavar="ALGO",
                        default="sha1")

    parser.add_argument("-m", "--multi-process", dest="multiprocessing",
                        action="store_true",
                        help="enable multi-processing & calculate hashes in parallel",
                        default=False)

    parser.add_argument("-o", "--output", dest="outfile",
                  action="store",
                  help="output file for the hash list",
                  metavar="OUT",
                  default=None)

    parser.add_argument("-e", "--extensions", dest="extensions",
                  action="store",
                  help="list (comma-separated) of file extensions that should be considered only",
                  metavar="EXT",
                  default=())



    args = vars(parser.parse_args())

    if args['gui']:
        from gui_data_fingerprint import start_gui
        start_gui()
        exit()
    else:
        if args['PATH'] is None:
            print("Please specify path to data. (Hint: use -h for help or -g to start the GUI)")
            exit()

    if len(args['extensions'])>0:
        args['extensions'] = args['extensions'].split(",")

    d = HashData(args['PATH'],
                 file_extensions=args['extensions'],
                 algorithm=args['algorithm'],
                 verbose=args['verbose'],
                 multiprocessing=args['multiprocessing'])

    if args['hashlist']:
        txt = d.to_string()[:-1]
        if not PY3:
            txt = string_encode(txt)
        print(txt)

    if args['outfile'] is not None:
        d.save(outfile=args['outfile'])

    if not args['verbose'] and not args['hashlist']:
        print(d.master_hash)