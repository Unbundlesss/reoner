# Reoner

Re-synchronize your Endlesss riffs to start on the 'one' beat.

## Usage
- Requires [ffmpeg](https://www.ffmpeg.org/download.html). 
- Install dependencies mentioned in Pipfile (virtual environment highly recommended):
- If you have pipenv, that is easiest.
```
pipenv install
pipenv shell
```

Start the interactive cli:
```
python -m reoner.cli
```


## Background
The app Endlesss exports riffs as a group of `.aiff` files. There is no natural requirement for users to always start on the first beat. So when exporting loops, you typically get a set of seemingly unsynchronized files.

In my experience, Endlesss Loops are offset in 32nd note increments. Additionally, for any riff export, all loops will be offset by the same number of 32nd notes.

This script will crudely guide you through picking the loop start point by ear, but right now you can only do one file at a time.

## How it works
You could theoretically do this all manually with ffmpeg, but no one actually knows how to use ffmpeg directly.

1 - determine the bpm of the loop. Thankfully this is dumped out right into the filename from Endlesss, so the script parses it out from that. 

2 - using the bpm and the number of frames, determine the beat length, in frames. pydub has lots of facilities for using milliseconds and time, but we can also use frames (samples) to get more precise cuts. 

3 - From the beat length, we can determine the number of frames in each 32nd beat. With that we can easily slice the audio into two pieces at the desired offset and rejoin.
