#!/usr/bin/env python3

import os
import sys
import codecs
import hashlib
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

        if not from_checksums_file:
            assert os.path.isdir(data)

        if hash_algorithm not in hashlib.algorithms_guaranteed:
            raise ValueError("Hash algorithm '{0}' not supported.".format(
                hash_algorithm))

        self._data = os.path.abspath(data)
        self._hash_algorithm = hash_algorithm
        self._files = []
        self._hash_dict = {}

        if from_checksums_file:
            length = hashlib.new(self._hash_algorithm).digest_size * 2
            with codecs.open(data, encoding="utf-8") as f:
                for line in f:
                    hash = line[:length]
                    fl = line[length:].strip()
                    self._hash_dict[hash] = fl
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
    def file_hash_dict(self):
        if len(self._hash_dict) < 1:
            self.generate()
        return self._hash_dict

    @property
    def checksums(self):
        rtn = ""
        if len(self.file_hash_dict) >= 1:
            for hash in sorted(self.file_hash_dict.keys()):
                rtn += u"{0}  {1}\n".format(hash, self.file_hash_dict[hash])
        return rtn

    @property
    def master_hash(self):
        if len(self.file_hash_dict) < 1:
            return None

        hasher = hashlib.new(self._hash_algorithm)
        hasher.update(self.checksums.encode("utf-8"))
        return hasher.hexdigest()

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

        func = partial(_hash_file, hash_algorithm = self._hash_algorithm)
        for counter, rtn in enumerate(
                multiprocessing.Pool().imap_unordered(func, self._files)):
            if progress is not None:
                progress(counter + 1, len(self._files),
                         "{0}/{1}".format(counter + 1,
                                          len(self._files)))
            print(os.path.split(self.data)[-1])
            fl = os.path.relpath(rtn[1], self._data).replace(os.path.sep, "/")
            self._hash_dict[rtn[0]] = fl

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


def _hash_file(filename, hash_algorithm):
    hasher = hashlib.new(hash_algorithm)
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(64*1024), b''):
            hasher.update(block)
    return hasher.hexdigest(), filename


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
        from builtins import input
        args["PATH"] = args["PATH"].decode(sys.stdin.encoding)

    dif = DataIntegrityFingerprint(data=args["PATH"],
                                    from_checksums_file=args['fromchecksumsfile'],
                                    hash_algorithm="sha256")
    if not args['fromchecksumsfile']:
        dif.generate(progress=progress)

    print("DIF: {0}".format(str(dif)))

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
