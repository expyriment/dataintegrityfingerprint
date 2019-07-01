#!/usr/bin/env python3

"""
Data Integrity Fingerprint

This module is the Python reference implementation of the Data Integrity
Fingerprint (DIF).

"""

from __future__ import unicode_literals


__author__ = 'Oliver Lindemann <oliver@expyriment.org>, ' +\
             'Florian Krause <florian@expyriment.org>'

import os
import codecs
import multiprocessing
from . import hashing

CHECKSUMS_SEPERATOR = "  "

class DataIntegrityFingerprint:
    """A class representing a DataIntegrityFingerprint (DIF).

    Example
    -------
    dif = DataIntegrityFingerPrint("~/Downloads")
    print(dif)
    print(dif.checksums)
    """

    def __init__(self, data, from_checksums_file=False,
                 hash_algorithm="sha256", multiprocessing=True,
                 allow_non_cryptographic_algorithms=False):
        """Create a DataIntegrityFingerprint object.

        Parameters
        ----------
        data : str
            the path to the data
        from_checksums_file : bool
            data argument is a checksums file
        hash_algorithm : str
            the hash algorithm (optional, default: sha256)
        multiprocessing : bool
            using multi CPU cores (optional, default: True)
            speeds up creating of checksums for large data files
        allow_non_cryptographic_algorithms : bool
            set True only, if you need non cryptographic algorithms (see notes!)

        Note
        ----
        We do not suggest to use non-cryptographic algorithms. Non-cryptographic
        algorithms are, while much faster, not secure (e.g. can be tempered
        with). Only use these algorithms to check for technical file damage and
        in cases security is not of critical concern.

        """

        if not from_checksums_file:
            assert os.path.isdir(data)

        if allow_non_cryptographic_algorithms and \
                hash_algorithm in hashing.NON_CRYPTOGRAPHIC_ALGORITHMS:
            Warning("Non cryptographic hash function is used.")
        elif hash_algorithm not in hashing.CRYPTOGRAPHIC_ALGORITHMS:
            raise ValueError("Hash algorithm '{0}' is not supported.".format(
                hash_algorithm))

        self._data = os.path.abspath(data)
        self._hash_algorithm = hash_algorithm
        self._files = []
        self._hash_list = []
        self.multiprocessing = multiprocessing
        self.allow_non_cryptographic_algorithms = allow_non_cryptographic_algorithms

        if from_checksums_file:
            with codecs.open(data, encoding="utf-8") as f:
                for line in f:
                    h, fl = line.split(CHECKSUMS_SEPERATOR, maxsplit=1)
                    self._hash_list.append((h, fl.strip()))
                self._sort_hash_list()
        else:
            for dir_, _, files in os.walk(self._data):
                for filename in files:
                    self._files.append(os.path.join(self._data, dir_,
                                                    filename))

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
        for h, fl in self.file_hash_list:
            rtn += u"{0}{1}{2}\n".format(h, CHECKSUMS_SEPERATOR, fl)
        return rtn

    @property
    def master_hash(self):
        if len(self.file_hash_list) < 1:
            return None

        hasher = hashing.new_hash_instance(self._hash_algorithm,
                                           self.allow_non_cryptographic_algorithms)
        hasher.update(self.checksums.encode("utf-8"))
        return hasher.digest

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
        func_args = zip(self._files,
                        [self._hash_algorithm] * len(self._files),
                        [self.allow_non_cryptographic_algorithms] * len(self._files))
        if self.multiprocessing:
            imap = multiprocessing.Pool().imap_unordered
        else:
            imap = map

        for counter, rtn in enumerate(imap(_map_file_hash, func_args)):
            if progress is not None:
                progress(counter + 1, len(self._files),
                         "{0}/{1}".format(counter + 1, len(self._files)))
            fl = os.path.relpath(rtn[1], self._data).replace(os.path.sep, "/")
            self._hash_list.append((rtn[0], fl))

        self._sort_hash_list()

    def save_checksums(self, filename=None):
        """Save the checksums to a file.

        Parameters
        ----------
        filename : str, optional
            the name of the file to save checksums to

        Returns
        -------
        success : bool
            whether saving was successful

        """

        if self.master_hash is not None:
            if filename is None:
                filename = os.path.split(self._data)[-1] + ".{0}".format(
                    self._hash_algorithm)

            with codecs.open(filename, 'w', "utf-8") as f:
                f.write(self.checksums)

            return True

def _map_file_hash(x):
    # helper function for multi threading of file hashing
    hasher = hashing.new_hash_instance(hash_algorithm=x[1],
                                       allow_non_cryptographic_algorithms=x[2])
    hasher.update_file(filename=x[0])
    return hasher.digest, x[0]
