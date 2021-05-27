Data Integrity Fingerprint (DIF)
================================

**A proposal for a (printable) fingerprint of scientific data sets that allows
verifying their integrity**

*Released under the MIT License*

Oliver Lindemann (oliver@expyriment.org) & Florian Krause (florian@expyriment.org)

Introduction
------------

**Problem:**  
How can we link a journal article unmistakably and indefinitely to an open data set (without relying on storage providers or other services that need to be maintained)?

**Solution:**  
We publish a unique and human-readable fingerprint of the data set in the journal article (allowing a reader with the data to calculate that fingerprint themselves and compare it to what is published in the article)!

Procedure for calculating the DIF of a data set
-----------------------------------------------

1. Choose a (cryptographic) hash function (e.g. SHA-256) as `Hash`

2.  For every file `f` in the (potentially nested) subtree under the dataset root directory,

    * calculate the hexadecimal digest (lower case letters) of `Hash(f)` (i.e. the hashed _binary contents_ of the file) as `h`

    * get the UTF-8 encoded relative path in Unix notation (i.e. U+002F slash character as separator) from the dataset root directory to `f` as `p`

    * create the string `hp` (i.e the concatenation of `h` and `p`)
    
    * add `hp` to a list `l`

3. Sort `l` in ascending Unicode code point order (i.e., byte- wise sorting, NOT based on the Unicode collation algorithm)

4. Create the string `l[0]l[1]...l[n]` (i.e. the concatenation of all elements of `l`)

5. Retrieve the DIF as the hexadecimal digest of `Hash(l[0]l[1]...l[n])`


### Note
On a GNU/Linux system with a UTF-8 locale, the procedure to create the SHA-256 DIF is equivalent to:
```
cd <DATA_SET_ROOT_DIRECTORY>
export LC_ALL=C
find . -type f -print0 | xargs -0 shasum -a 256 | cut -c-64,69- | sort | tr -d '\n' | shasum -a 256 | cut -c-64
```

Available implementations
-------------------------

* Python 3:  [dataintegrityfingerprint-python](https://github.com/expyriment/dataintegrityfingerprint-python)
* R:  [dataintegrityfingerprint-r](https://github.com/expyriment/dataintegrityfingerprint-r)
