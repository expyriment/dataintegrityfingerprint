DIF procedure
-------------

1. For every file 'file' in a directory 'data':

    a. Calculate the hexadecimal digest (lower case letters) of the $FUNCTION
       hash of the contents of 'file' (hereafter referred to as <hash>)

    b. Calculate the relative path in Unix notation (i.e. forward slashes) to
       'file' from (and including) 'data' (hereafter referred to as <path>)

    c. Append "<hash>  <path>" (note the two whitespaces) as an independent
       line (line feed only, no carriage return) to a UTF-8 encoded file
       'checksums' (characters that cannot be encoded with UTF-8 shall be
       replaced with a question mark)

2. Sort the lines in 'checksums' in ascending ASCII-code order

3. Calculate the hexadecimal digest of the $FUNCTION hash of the contents of
   'checksums'
