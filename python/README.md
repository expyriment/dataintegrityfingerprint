Example using DIF package
```
from dataintegrityfingerprint import DataIntegrityFingerprint

dif = DataIntegrityFingerprint("/home/me/Downloads")
print(dif)
print(dif.checksums)
print(dif.master_hash)
```

DIF Command line interface
```
python3 -m dataintegrityfingerprint.cli -h
```


DIF GUI
```
python3 -m dataintegrityfingerprint.gui
```
