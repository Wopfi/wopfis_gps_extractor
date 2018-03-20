# Wopfi's GPS Extractor
## What it does

This script recursively collects GPS information from pictures in a certain directory. It uses exiftool
for reading the EXIF tag.

Wopfi's GPS Extractor supports the following command line arguments:

```
-f file extension to search for
-o output file for the GPS coordinates
-a append to the text file instead of creating a new one
-d the root directory for the picture search
```

A typical command line looks like this:

```
./points_from_exif.py -f .cr2 -o gps_pictures.txt -d /myPictureFilePath/
```
