#!/usr/bin/env python
import os
import sys
import codecs
import hashlib
import collections
import multiprocessing
from functools import partial


class DataIntegrityFingerprint:
    """A class representing a DataIntegrityFingerprint (DIF).

    Example
    -------
    dif = DataIntegrityFingerPrint("~/Downloads")
    dif.generate()
    print(dif)

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

        if hash_algorithm not in hashlib.algorithms_guaranteed:
            raise ValueError("Hash algorithm '{0}' not supported.".format(
                hash_algorithm))
        self._hash_algorithm = hash_algorithm
        self._file_hashes = collections.OrderedDict()
        if from_checksums_file:
            self._file_hashes = collections.OrderedDict()
            with codecs.open(data, encoding="utf-8") as f:
                for line in f:
                    length = hashlib.new(self._hash_algorithm).digest_size * 2
                    hash_ = line[:length]
                    dir_ = line[length:].lstrip()
                    self._data = dir_.split(os.path.sep)[0]
                    root = os.path.split(self._data)[-1] + os.path.sep
                    self._file_hashes[dir_.replace(root, "")] = hash_
            self._generated = True
        else:
            self._data = os.path.abspath(data)
            if os.path.isfile(data):
                self._file_hashes[data] = None
            else:
                for dir_, _, files in os.walk(self._data):
                    for filename in files:
                        filename = os.path.join(os.path.relpath(dir_, self._data),
                                                filename)
                        if filename.startswith("./"):
                            filename = filename[2:]
                        self._file_hashes[filename] = None
            self._generated = False

    def __str__(self):
        return str(self._master_hash)

    @property
    def data(self):
        return self._data

    @property
    def file_hashes(self):
        return self._file_hashes

    @property
    def _master_hash(self):
        if not self._generated:
            return None
        file_hashes = sorted(self._file_hashes.values())
        if len(file_hashes) > 1:
            hasher = hashlib.new(self._hash_algorithm)
            for file_hash in file_hashes:
                hasher.update(file_hash.encode("ascii"))
            return hasher.hexdigest()
        else:
            return self._file_hashes[self._file_hashes.keys()[0]]

    def generate(self, progress=None):
        """Calculate the fingerprint.

        Parameters
        ----------
        progress: function, optional
            a callback function for a progress reporting that takes the
            following parameters:
                count  -- the current count
                total  -- the total count
                status -- a string describing the status

        """

        if len(self._file_hashes) > 1:
            tmp = [os.path.join(self._data, filename) for \
                   filename in self._file_hashes.keys()]
            func = partial(_hash_file, hash_algorithm = self._hash_algorithm)
            for counter, rtn in enumerate(
                    multiprocessing.Pool().imap_unordered(func, tmp)):
                if progress is not None:
                    progress(counter + 1, len(self._file_hashes),
                             "{0}/{1}".format(counter + 1,
                                              len(self._file_hashes)))
                self._file_hashes[rtn[0].replace(
                    self._data + os.path.sep, "")] = rtn[1]
        else:
            rtn = _hash_file(self._file_hashes.keys()[0])
            self._file_hashes[rtn[0]] = rtn[1]
        self._generated = True


def _hash_file(filename, hash_algorithm):
    hasher = hashlib.new(hash_algorithm)
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(64*1024), b''):
            hasher.update(block)
    return filename, hasher.hexdigest()


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(
            description="Create a Data Integrity Fingerprint (DIF).",
            epilog="(c) F. Krause & O. Lindemann")
    parser.add_argument("PATH", nargs='?', default=None,
                        help="the path to the data folder or file")
    parser.add_argument("-s", "--save-checksums-file", dest="savechecksumsfile",
                        action="store_true",
                        help="save checksums file",
                        default = False)
    parser.add_argument("-f", "--from-checksums-file", dest="fromchecksumsfile",
                        action="store_true",
                        help="PATH is a checksums file",
                        default = False)
    args = vars(parser.parse_args())

    if args["PATH"] is None:
        print("Use -h for help")
        sys.exit()

    if sys.version[0] == '2':
        input = raw_input
        args["PATH"] = args["PATH"].decode(sys.stdin.encoding)

    def progress(count, total, status=''):
        bar_len = 50
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '=' * filled_len + ' ' * (bar_len - filled_len)
        sys.stdout.write('{:5.1f}% [{}] {}\r'.format(percents, bar, status))
        sys.stdout.flush()

    if args['fromchecksumsfile']:
        dif = DataIntegrityFingerprint(args["PATH"], True, "sha256")
    else:
        dif = DataIntegrityFingerprint(args["PATH"], False, "sha256")
        dif.generate(progress=progress)
        print("")
    print("DIF: {0}".format(dif))

    if args['savechecksumsfile']:
        outfile = os.path.split(dif.data)[-1] + ".sha256"
        answer = "y"
        if os.path.exists(outfile):
            answer = input(
                    "'{0}' already exists! Overwrite? [y/N]: ".format(outfile))
        if answer == "y":
            with codecs.open(outfile, 'w', encoding="utf-8") as f:
                for filename in dif.file_hashes:
                    f.write(dif.file_hashes[filename] + "  " + os.path.join(
                        os.path.split(dif._data)[-1], filename + "\n"))
            print("Checksums have been written to '{0}'.".format(outfile))
        else:
            print("Checksums have NOT been written.".format(outfile))
