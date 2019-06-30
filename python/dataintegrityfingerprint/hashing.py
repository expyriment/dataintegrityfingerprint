from __future__ import unicode_literals

"""
This module provides wrapper for hash functions from different libraries
to have a unique interface for all types of hash algorithm.

Each HashAlgorithm class has the methods 
    update() & update_file() and
the properties 
    digest & digest_size.
    
"""

import hashlib
import zlib

CRYPTOGRAPHIC_ALGORITHMS = sorted(hashlib.algorithms_guaranteed)
NON_CRYPTOGRAPHIC_ALGORITHMS = sorted(["crc32", "adler32"])

def new_hash_instance(hash_algorithm, allow_non_cryptographic_algorithms=False):
    """return a new instance of an hash object. (similar hashlib.new())

    Each HashAlgorithm object has the methods update & update_file and
    the properties checksum & digest_size.

    :param hash_algorithm:
    :param allow_non_cryptographic_algorithms:

    """

    hash_algorithm = hash_algorithm.lower()
    possible_algorithms = CRYPTOGRAPHIC_ALGORITHMS
    if allow_non_cryptographic_algorithms:
        possible_algorithms += NON_CRYPTOGRAPHIC_ALGORITHMS

    if hash_algorithm not in possible_algorithms :
        raise RuntimeError("{0} is a not support hash algorithm.".format(
                            hash_algorithm))

    if hash_algorithm == "crc32":
        return CRC32()
    if hash_algorithm == "adler32":
        return Adler32()
    else:
        return OpenSSLHashAlgorithm(hash_algorithm)


class _HashAlgorithm(object):
    # abstract super class of a hash algorithms

    def update_file(self, filename):

        with open(filename, 'rb') as f:
            for block in iter(lambda: f.read(64 * 1024), b''):
                self.update(block)

    def update(self, data):
        pass


class CRC32(_HashAlgorithm):

    digest_size = 8

    def __init__(self):
        self._current = 0

    def update(self, data):
        self._current = zlib.crc32(data, self._current)

    @property
    def digest(self):
        return hex(self._current)[2:]

class Adler32(_HashAlgorithm):

    digest_size = 8

    def __init__(self):
        self._current = None

    def update(self, data):
        try:
            self._current = zlib.adler32(data, self._current)
        except:
            self._current = zlib.adler32(data)

    @property
    def digest(self):
        return hex(self._current)[2:]


class OpenSSLHashAlgorithm(_HashAlgorithm):

    def __init__(self, hash_algorithm):
        self.hasher = hashlib.new(hash_algorithm)

    def update(self, data):
        self.hasher.update(data)

    @property
    def digest(self):
        return self.hasher.hexdigest()

    @property
    def digest_size(self):
        return self.hasher.digest_size
