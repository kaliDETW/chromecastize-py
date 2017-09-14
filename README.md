# chromecastize-py

This is a port of the original chromecastize shell script to python. The idea is to get one code base run on windows as well as unix systems as I do not want to maintain two versions of the same script.

## What is this good for
Useful if you want to make your old home video collection, gaming videos, videos recorded with your mobile phone etc compatible with chromecast or the amazon fire tv stick, so that they can be directly streamed to those devices.

## installation
clone the repo and copy the chromecastize-py.py file anywhere you want. If you do not have ffmpeg or mediainfo in the path or want to use a special version just for this script, you can also just put ffmpeg and mediainfo into the same folder as the python file.

It would look like something like this (example for windows):


```
my_folder/ 
├── mediainfo/
│   ├── MediaInfo.exe
│   ├── ...
├── ffmpeg/
│   ├── bin/
│   |   ├── ffmpeg.exe
│   |   ├── ...
│   └── ...
├── chromecastize-py.py
```

## usage
The python script accepts one mandatory parameter, which is the absolute or relative path to the to be transcoded file or directory.

e.g. <br>
```
chromecastize-py -i [path_to_file_or_directory]
```

## TODOs
- check if this runs on linux
- use proper shlex.quote to quote the absolute file paths
