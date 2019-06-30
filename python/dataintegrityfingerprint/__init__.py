__author__ = 'Oliver Lindemann <oliver@expyriment.org>, ' \
             'Florian Krause <florian@expyriment.org>'

__version__ = '0.2'

from .hashing import CRYPTOGRAPHIC_ALGORITHMS, NON_CRYPTOGRAPHIC_ALGORITHMS, \
                    new_hash_instance
from .dif import DataIntegrityFingerprint
