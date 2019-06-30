#!/usr/bin/env python3

import os
import sys
import argparse

from .hashing import CRYPTOGRAPHIC_ALGORITHMS, NON_CRYPTOGRAPHIC_ALGORITHMS
from . import DataIntegrityFingerprint

def run_cli():

    def progress(count, total, status=''):
        bar_len = 50
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '=' * filled_len + ' ' * (bar_len - filled_len)
        sys.stdout.write('{:5.1f}% [{}] {}\r'.format(percents, bar, status))
        sys.stdout.flush()


    parser = argparse.ArgumentParser(
            description="Create a Data Integrity Fingerprint (DIF).",
            epilog="(c) O. Lindemann & F. Krause")
    parser.add_argument("PATH", nargs='?', default=None,
                        help="the path to the data folder or file")
    parser.add_argument("-f", "--from-checksums-file", dest="fromchecksumsfile",
                        action="store_true",
                        help="PATH is a checksums file",
                        default=False)
    parser.add_argument("-c", "--checksums-file", dest="checksumsfile",
                        action="store_true",
                        help="show checksums file",
                        default=False)
    parser.add_argument("-p", "--progress", dest="progressbar",
                        action="store_true",
                        help="show progressbar",
                        default=False)
    parser.add_argument("-s", "--save-checksums-file", dest="savechecksumsfile",
                        action="store_true",
                        help="save checksums file",
                        default=False)
    parser.add_argument("-n", "--no-multi-processing", dest="nomultiprocess",
                        action="store_true",
                        help="switch of multi processing",
                        default=False)
    parser.add_argument("-a", "--algorithm", metavar="ALGORITHM",
                        type= str,
                        help="the hash algorithm to be used (default=sha256)",
                        default="sha256")
    parser.add_argument("-L", "--list-available-algorithms", dest="listalgos",
                        action="store_true",
                        help="list all available-algorithms",
                        default=False)
    parser.add_argument("--non-crypthographic", dest="noncrypto",
                        action="store_true",
                        help="allow non crypthographic algorithms (Not suggested, please read documentation carefully!) ",
                        default=False)
    args = vars(parser.parse_args())

    if args['listalgos']:
        print("Crypothographic algorithms")
        print("- " + "\n- ".join(CRYPTOGRAPHIC_ALGORITHMS))
        if args['noncrypto']:
            print("Non-crypothographic algorithms")
            print("- " + "\n- ".join(NON_CRYPTOGRAPHIC_ALGORITHMS))

        sys.exit()

    if args["PATH"] is None:
        print("Use -h for help")
        sys.exit()

    if sys.version[0] == '2':
        from builtins import input
        args["PATH"] = args["PATH"].decode(sys.stdin.encoding)

    dif = DataIntegrityFingerprint(data=args["PATH"],
                                    from_checksums_file=args['fromchecksumsfile'],
                                    hash_algorithm=args["algorithm"],
                                    multiprocessing=not(args['nomultiprocess']),
                                    allow_non_cryptographic_algorithms=args['noncrypto'])

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


if __name__ == "__main__":
    run_cli()
