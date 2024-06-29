# osu! Replay Analyzer

Replay analyzer for the rhythm game [osu!](https://osu.ppy.sh/).

Currently only works for osu!mania.

## Features

- Read replay file and extract replay information
- Calculate Accuracy and MA Ratio
- Get PP and SR using [Maniera](https://github.com/NiceAesth/maniera)

## Running

Install maniera using PIP:

```
pip install maniera
```

Run using Python 3:

```
python3 main.py your_replay_file.osr
```

## References

- https://osu.ppy.sh/wiki/en/Client/File_formats/Osr_%28file_format%29
- https://github.com/ppy/osu-api/wiki
- https://github.com/NiceAesth/maniera
- https://dev.catboy.best/docs

## TODO

- [x] Standardized output format
- [x] Implement Maniera (https://github.com/NiceAesth/maniera)
- [x] Implement better error handling
- [x] Implement argparse for better argument parsing
- [x] Download beatmapset from catboy.best
- [ ] Accept multiple file paths and directory paths for processing of multiple replay files at once
- [ ] Add colors to output
- [ ] Swap maniera with aiosu for all-mode support
- [ ] Visualize miss frequency using replay data
