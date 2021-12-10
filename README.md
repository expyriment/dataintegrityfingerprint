Data Integrity Fingerprint (DIF)
================================

**A proposal for a human-readable fingerprint of scientific datasets that allows verifying their integrity**

*Released under the MIT License*

Oliver Lindemann (oliver@expyriment.org) & Florian Krause (florian@expyriment.org)

Introduction
------------

**Problem:**  
How can we link a journal article unmistakably and indefinitely to a related (open) dataset, without relying on storage providers or other services that need to be maintained?

**Solution:**  
The author calculates checksums of all the files in the dataset the article relates to. From these checksums the author calculates the _Data Integrity Fingerprint (DIF)_ - a single "master checksum" that uniquly identifies the entire dataset. The author reports the DIF in the journal article. A reader of the journal article who obtained a copy of the dataset (from either the author or any other source) calculates the DIF of their copy of the dataset and compares it to the correct DIF as stated in the article. If the list of checksums of individual files in the original dataset is available, the author can furthermore investigate in detail the differences between the datasets, in case of a DIF mismatch.

![DIF_Procedure_Flowchart](https://user-images.githubusercontent.com/2971539/143914028-ea2b8570-6db4-4f82-9bec-b1770fda7df8.png)

Procedure for calculating the DIF of a dataset
----------------------------------------------

1. Choose a (cryptographic) hash function `Hash` (e.g. SHA-256)

2.  For every file `f` in the (potentially nested) subtree under the dataset root directory,

    * calculate the checksum `c` as the hexadecimal digest (lower case letters) of `Hash(f)` (i.e. the hashed _binary contents_ of the file)

    * get the file path `p` as the UTF-8 encoded relative path in Unix notation (i.e. U+002F slash character as separator) from the dataset root directory to `f`

    * create the string `cp` (i.e the concatenation of `c` and `p`)
    
    * add `cp` to a list `l`
    
3. Sort `l` in ascending Unicode code point order (i.e., byte- wise sorting, NOT based on the Unicode collation algorithm)

4. Create the string `l[0]l[1]...l[n]` (i.e. the concatenation of all elements of `l`)

5. Retrieve the DIF as the hexadecimal digest of `Hash(l[0]l[1]...l[n])`

Optionally, checksums of individual files and their file paths can be saved as a checksums file (lines of `c  p` for each `f).

### Note
On a GNU/Linux system with a UTF-8 locale, the procedure to create the SHA-256 DIF is equivalent to:
```
cd <DATASET_ROOT_DIRECTORY>
export LC_ALL=C
find . -type f -print0 | xargs -0 shasum -a 256 | cut -c-64,69- | sort | tr -d '\n' | shasum -a 256 | cut -c-64
```

Available implementations
-------------------------

* Python (reference implementation):  [dataintegrityfingerprint-python](https://github.com/expyriment/dataintegrityfingerprint-python)


Example data
------------
Custom implementations may be tested against [example data](https://github.com/expyriment/DIF/tree/master/example_data) to verify correctness.
