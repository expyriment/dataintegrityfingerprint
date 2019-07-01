Data Integrity Fingerprint (DIF)
================================

*Released under the MIT License*

Oliver Lindemann (oliver@expyriment.org) & Florian Krause (florian@expyriment.org)

General Documentation: http://expyriment.github.io/dataintegrityfingerprint


DIF procedure
-------------

1. For every file `file` in a directory `data` (that is part of the dataset):

    a. Calculate the hexadecimal digest (lower case letters) of the SHA-256
       hash of the contents of `file` (hereafter referred to as `<hash>`)

    b. Calculate the relative path in Unix notation (i.e. forward slashes) to
       `file` from `data` (hereafter referred to as `<path>`)

    c. Append `<hash>  <path>` (that is, `<hash>` followed by two U+0020
       whitespace characters followed by `<path>`) as an independent line
       (U+000A line feed only, no U+000D carriage return) to a UTF-8 encoded
       file `checksums` (characters in `path` that cannot be encoded with
       UTF-8 shall be replaced with a U+003F question mark character;
       `checksums` shall have no empty lines)

2. Sort the lines in `checksums` in ascending Unicode code point order (i.e.,
   sorting capital letters first or byte-wise sorting, no sorting based on the Unicode collation algorithm)

3. Calculate the hexadecimal digest of the SHA-256 hash of the sorted
   contents of `checksums`


### Note
On a Unix(-like) system with a UTF-8 locale, the procedure is equivalent to:
```
cd <DATA_FOLDER>
export LC_ALL=C
find . -type f -print0 | xargs -0 shasum -a 256 | sort | sed 's/\.\///' | shasum -a 256 | cut -d' ' -f1
```



Available Implementations
-------------------------

* Python 2/3:  [dataintegrityfingerprint-python](https://github.com/expyriment/dataintegrityfingerprint-python)
* R:  [dataintegrityfingerprint-r](https://github.com/expyriment/dataintegrityfingerprint-r)
