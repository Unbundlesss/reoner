# Reoner

Re-synchronize your Endlesss rifffs to start on the 'one' beat.

## Usage
- Requires [ffmpeg](https://www.ffmpeg.org/download.html). 
- Install dependencies mentioned in Pipfile (virtual environment highly recommended):
  - python 3.9
  - pydub
  - pyinquirer

```shell
python run.py
```
- or run script with offset and optional filename:
```shell
python run.py <filename> --offset <offset>
```

If filename is not provided, then an interactive chooser will be started. All options are optional.

Full options:
```shell
python run.py [-h] [--outpath OUTPATH] [--bpm BPM] --offset OFFSET [file]
```
OUTPATH is a directory, not a file. It will default to the same folder as the source file. It will use the same file name but with `.wav` instead. Does not hesitate to overwrite the same `wav` file over and over.

BPM is in case the bpm is not in the file name, such as the case for older riffff exports. Filenames with bpm in them look like this: `2 - jgusta - Audio In - 135.1234BPM - 2022-03-16-09-55.aiff`

OFFSET is specified in number of 32nd notes. If not specified you can preview the offset in the interactive thing. It's extremely clunky right now but works.


## Background
The app Endlesss exports rifffs as a group of `.aiff` files. There is no natural requirement for users to always start on the first beat. So when exporting loops, you typically get a set of seemingly unsynchronized files.

In my experience, Endlesss Loops ware offset in 32nd note increments. Additionally, for any rifff export, all loops will be offset by the same number of 32nd notes.

This script will crudely guide you through picking the loop start point by ear, then applying the change to all files in the rifff. But right now you can only do one file at a time.

## How it works
You could theoretically do this all manually with ffmpeg, but no one actually knows how to use ffmpeg directly.

1 - determine the bpm of the loop. Thankfully this is dumped out right into the filename from Endlesss, so the script parses it out from that. 

2 - using the bpm and the number of frames, determine the beat length, in frames. pydub has lots of facilities for using milliseconds and time, but we can also use frames (samples) to get more precise cuts. 

3 - From the beat length, we can determine the number of frames in each 32nd beat. With that we can easily slice the audio into two pieces at the desired offset and rejoin.
