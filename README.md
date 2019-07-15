Data Integrity Fingerprint (DIF)
================================

*Released under the MIT License*

Oliver Lindemann (oliver@expyriment.org) & Florian Krause (florian@expyriment.org)


Available Implementations
-------------------------

* Python 3:  [dataintegrityfingerprint-python](https://github.com/expyriment/dataintegrityfingerprint-python)
* R:  [dataintegrityfingerprint-r](https://github.com/expyriment/dataintegrityfingerprint-r)


DIF procedure
-------------

1. Choose a (cryptographic) hash function `Hash` (e.g. "SHA-256") and let
   `PREFIX` be it's official name, converted to lower case letters with
   nonalphanumeric symbols removed (e.g. "sha256")

2. For every file `f` in the parent directory of the data:

    a. Calculate `h` as the hexadecimal digest (lower case letters) of
       `Hash(f)` (i.e. the hashed _contents_ of `f`)
       
    b. Calculate `p` as the relative path in Unix notation (i.e. U+002F
       forward slash character as separator) to `f` from the parent directory

    c. Append `h  p` (i.e., `h` followed by two U+0020
       whitespace characters followed by `p`) as an independent line
       (U+000A line feed only, no U+000D carriage return) to a UTF-8-encoded
       file `checksums` (characters in `p` that cannot be encoded with
       UTF-8 shall be replaced with a U+003F question mark character;
       `checksums` shall have no empty lines)

3. Sort the lines in `checksums` in ascending Unicode code point order (i.e.,
   byte-wise sorting, NOT based on the Unicode collation algorithm)

4. Calculate `POSTFIX` as the hexadecimal digest of `Hash(checksums)` (i.e the
   hashed _contents_ of sorted `checksums`)

6. Retrieve the DIF of the dataset as `PREFIX.POSTFIX` (i.e. `PREFIX` followed
   by a U+002E dot character followed by `POSTFIX`)


### Note
On a Unix(-like) system with a UTF-8 locale, the procedure to create a DIF
based on SHA-256 is equivalent to:
```
cd <DATA_DIRECTORY>
export LC_ALL=C
find . -type f -print0 | xargs -0 shasum -a 256 | sort | sed 's/\.\///' | \
shasum -a 256 | cut -d' ' -f1 | sed -e 's/^/sha256\./'
```
