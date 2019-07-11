DIF on UNIX(-like) operating systems
-------------------------------------

On POSIX operating systems with a UTF-8 locale, the procedure to create a DIF
based on SHA-256 is equivalent to:

```
cd <DATA_FOLDER>
export LC_ALL=C
find . -type f -print0 | xargs -0 shasum -a 256 | sort | sed 's/\.\///' | shasum -a 256 | cut -d' ' -f1 | sed -e 's/^/sha256\./'
```



