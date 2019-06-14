#!/usr/bin/env python3

from __future__ import unicode_literals

import os
import sys
import codecs
import hashlib
import multiprocessing


class DataIntegrityFingerprint:
    """A class representing a DataIntegrityFingerprint (DIF).

    Example
    -------
    dif = DataIntegrityFingerPrint("~/Downloads")
    print(dif)
    print(dif.checksums)
    """

    def __init__(self, data, from_checksums_file=False, hash_algorithm="sha256"):
        """Create a DataIntegrityFingerprint object.

        Parameters
        ----------
        data : str
            the path to the data
        from_checksums_file : bool
            data argument is a checksums file
        hash_algorithm : str
            the hash algorithm (optional, default: sha256)

        """

        if not from_checksums_file:
            assert os.path.isdir(data)

        if hash_algorithm not in hashlib.algorithms_guaranteed:
            raise ValueError("Hash algorithm '{0}' not supported.".format(
                hash_algorithm))

        self._data = os.path.abspath(data)
        self._hash_algorithm = hash_algorithm
        self._files = []
        self._hash_list = []

        if from_checksums_file:
            length = hashlib.new(self._hash_algorithm).digest_size * 2
            with codecs.open(data, encoding="utf-8") as f:
                for line in f:
                    hash = line[:length]
                    fl = line[length:].strip()
                    self._hash_list.append((hash, fl))
                    self._sort_hash_list()
        else:
            for dir_, _, files in os.walk(self._data):
                for filename in files:
                    self._files.append(os.path.join(self._data, dir_, filename))

    def __str__(self):
        return str(self.master_hash)

    @property
    def data(self):
        return self._data

    @property
    def file_hash_list(self):
        if len(self._hash_list) < 1:
            self.generate()
        return self._hash_list

    @property
    def checksums(self):
        rtn = ""
        for hash, fl in self.file_hash_list:
            rtn += u"{0}  {1}\n".format(hash, fl)
        return rtn

    @property
    def master_hash(self):
        if len(self.file_hash_list) < 1:
            return None

        hasher = hashlib.new(self._hash_algorithm)
        hasher.update(self.checksums.encode("utf-8"))
        return hasher.hexdigest()

    def _sort_hash_list(self):
        self._hash_list = sorted(self._hash_list, key=lambda x: x[0] + x[1])

    def generate(self, progress=None):
        """Generate the Data Integrity Fingerprint.

        Parameters
        ----------
        progress: function, optional
            a callback function for a progress reporting that takes the
            following parameters:
                count  -- the current count
                total  -- the total count
                status -- a string describing the status

        """

        self._hash_list = []
        func_args = zip(self._files, [self._hash_algorithm]*len(self._files))
        pool = multiprocessing.Pool()
        for counter, rtn in enumerate(pool.imap_unordered(_hash_file, func_args)):
            if progress is not None:
                progress(counter + 1, len(self._files),
                         "{0}/{1}".format(counter + 1, len(self._files)))
            fl = os.path.relpath(rtn[1], self._data).replace(os.path.sep, "/")
            self._hash_list.append((rtn[0], fl))

        self._sort_hash_list()

    def save_checksums(self):
        """Save the checksums to a file.

        Returns True if successful.

        """

        if self.master_hash is not None:
            filename = os.path.split(self._data)[-1] + ".{0}".format(
                            self._hash_algorithm)
            with codecs.open(filename, 'w', "utf-8") as f:
                f.write(self.checksums)
            return True


def _hash_file(args):
    # args = (filename, hash_algorithm)
    hasher = hashlib.new(args[1])
    with open(args[0], 'rb') as f:
        for block in iter(lambda: f.read(64*1024), b''):
            hasher.update(block)
    return hasher.hexdigest(), args[0]


if __name__ == "__main__":

    import argparse

    def progress(count, total, status=''):
        bar_len = 50
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '=' * filled_len + ' ' * (bar_len - filled_len)
        sys.stdout.write('{:5.1f}% [{}] {}\r'.format(percents, bar, status))
        sys.stdout.flush()


    parser = argparse.ArgumentParser(
            description="Create a Data Integrity Fingerprint (DIF).",
            epilog="(c) F. Krause & O. Lindemann")
    parser.add_argument("PATH", nargs='?', default=None,
                        help="the path to the data folder or file")
    parser.add_argument("-s", "--save-checksums-file", dest="savechecksumsfile",
                        action="store_true",
                        help="save checksums file",
                        default=False)
    parser.add_argument("-c", "--checksums-file", dest="checksumsfile",
                        action="store_true",
                        help="show checksums file",
                        default=False)
    parser.add_argument("-p", "--progress", dest="progressbar",
                        action="store_true",
                        help="show progressbar",
                        default=False)
    parser.add_argument("-f", "--from-checksums-file", dest="fromchecksumsfile",
                        action="store_true",
                        help="PATH is a checksums file",
                        default=False)
    args = vars(parser.parse_args())

    if args["PATH"] is None:
        print("Use -h for help")
        sys.exit()

    if sys.version[0] == '2':
        from builtins import input
        args["PATH"] = args["PATH"].decode(sys.stdin.encoding)

    dif = DataIntegrityFingerprint(data=args["PATH"],
                                    from_checksums_file=args['fromchecksumsfile'],
                                    hash_algorithm="sha256")

    if not args['fromchecksumsfile'] and args['progressbar']:
        dif.generate(progress=progress)
        print("")

    if args['checksumsfile']:
        print(dif.checksums)
    else:
        print(dif)


    if args['savechecksumsfile']:
        outfile = os.path.split(dif.data)[-1] + ".{0}".format(dif._hash_algorithm)
        answer = "y"
        if os.path.exists(outfile):
            answer = input(
                    "'{0}' already exists! Overwrite? [y/N]: ".format(outfile))
        if answer == "y":
            dif.save_checksums()
            print("Checksums have been written to '{0}'.".format(outfile))
        else:
            print("Checksums have NOT been written.")


