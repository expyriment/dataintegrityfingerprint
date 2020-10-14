Data Integrity Fingerprint (DIF)
================================

**A proposal for a (printable) fingerprint of scientific data sets that allows
verifying their integrity.**

*Released under the MIT License*

Oliver Lindemann (oliver@expyriment.org) & Florian Krause (florian@expyriment.org)


Available Implementations
-------------------------

* Python 3:  [dataintegrityfingerprint-python](https://github.com/expyriment/dataintegrityfingerprint-python)
* R:  [dataintegrityfingerprint-r](https://github.com/expyriment/dataintegrityfingerprint-r)


Procedure for calculating the DIF of a data directory
-----------------------------------------------------

1. Choose a (cryptographic) hash function `Hash` (e.g. SHA-256)

2. For every file `f` in the (potentially nested) data directory subtree:

    * Calculate `h` as the hexadecimal digest (lower case letters) of `Hash(f)`
      (i.e. the hashed _contents_ of `f`)
       
    * Calculate `p` as the relative path in Unix notation (i.e. U+002F slash
      character as separator) from the data directory to `f`

    * Append `h  p` (i.e., `h` followed by two U+0020 space characters followed
      by `p`) as an independent line (ending with U+000A line feed only, no
      U+000D carriage return) to a UTF-8-encoded file `checksums` (characters
      in `p` that cannot be encoded with UTF-8 shall be replaced with a U+003F
      question mark character; `checksums` shall have no empty lines)

3. Sort the lines in `checksums` in ascending Unicode code point order (i.e.,
   byte-wise sorting, NOT based on the Unicode collation algorithm)

4. Retrieve the DIF as the hexadecimal digest of `Hash(checksums)` (i.e the
   hashed _contents_ of sorted `checksums`)


### Note
On a GNU/Linux system with a UTF-8 locale, the procedure to create a DIF based
on SHA-256 is equivalent to:
```
cd <DATA_DIRECTORY>
export LC_ALL=C
find . -type f -print0 | xargs -0 shasum -a 256 | sort | sed 's/\.\///' | shasum -a 256 | cut -d' ' -f1
```
