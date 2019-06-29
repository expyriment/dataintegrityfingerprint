#!/usr/bin/env python3

import os
import multiprocessing
import numpy as np

def random_file(para):
    np.random.seed(50)
    filename, size_mb = para
    with open(filename,'wb') as fl:
        for _ in range(size_mb):
            mb = np.random.bytes(1024*1024)
            fl.write(mb)
    print("created {0}".format(filename))
    return

if __name__ == "__main__":
    DIR = "test_data"
    N_FILE = 10
    SIZE_MB = 100

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

