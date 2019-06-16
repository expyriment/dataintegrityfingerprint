Example using DIF package
```
import dif

d = dif.DataIntegrityFingerPrint("~/Downloads")
print(d)
print(d.checksums)
print(d.master_hash)
```

DIF Command line interface
```
python3 -m dif.cli -h
```


DIF GUI
```
python3 -m dif.gui
```


