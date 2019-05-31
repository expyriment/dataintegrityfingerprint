DIF procedure
-------------

1. For every file `file` in a directory `data`:

    a. Calculate the hexadecimal digest (lower case letters) of the SHA-256
       hash of the contents of `file` (hereafter referred to as `<hash>`)

    b. Calculate the relative path in Unix notation (i.e. forward slashes) to
       `file` from (and including) `data` (hereafter referred to as `<path>`)

    c. Append `<hash>  <path>` (that is, `<hash>` followed by two U+0020
       whitespace characters followed by `<path>`) as an independent line
       (U+000A line feed only, no U+000D carriage return) to a UTF-8 encoded
       file `checksums` (characters in `path` that cannot be encoded with
       UTF-8 shall be replaced with a U+003F question mark character;
       `checksums` shall have no empty lines)

2. Sort the lines in `checksums` in ascending Unicode code point order (not Unicode collation algorithm)

3. Calculate the hexadecimal digest of the SHA-256 hash of the sorted
   contents of 'checksums'
