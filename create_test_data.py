#!/usr/bin/env python3

import os
import random
import multiprocessing

def random_file(para):
    random.seed(50)
    filename, size_mb = para
    with open(filename,'wb') as fl:
        for _ in range(size_mb):
            mb = map(lambda x: random.getrandbits(8),
                    range(1024*1024))
            fl.write(bytes(mb))
    print("created {0}".format(filename))
    return


if __name__ == "__main__":
    DIR = "test_data"
    N_FILE = 10
    SIZE_MB = 50

    try:
        os.mkdir(DIR)
    except:
        pass

    para = []
    for n in range(N_FILE):
        fl_name = os.path.join(DIR, "file_öäüß_{0}.rnd".format(n))
        para.append( (fl_name, SIZE_MB) )

    p = multiprocessing.Pool()
    list(p.imap_unordered(random_file, para))
