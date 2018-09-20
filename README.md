# stripclub
Tools to make elf files a bit smaller..

##striptease
A simple command line python program to show you the potential savings that could be made if ELF sections (not used during execution of a program) are removed from a list of files/directories.

To run the program specify file(s) and/or directories containing ELF files that you are interested in making file size savings.

```
python striptease.py <file/directory>
```
 
for example to find the savings that could be made to a root file system for an embedded device:
```
python striptease.py buildarea/rootfs
```

If you are interested in seeing which files are being analysed try passing the `-v` flag to the program.
