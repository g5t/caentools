# CAENtools for BIFROST triplet test measurements

## Installation
This module depends only on `numpy` and `scipp`. 
It can be installed at the system level or in a virtual environment.

After optionally setting up a virtual environment, install via
```bash
python -m pip install git+https://github.com/g5t/caentools.git
```


## Use
The installation should produce a command line utility, `caen-extract`, available on your path.
You can use it to extract individual channels from a binary data file to individual text files.

The command
```bash
caen-extract filename.dat --channels 0-3 --output extracted_channels_from_filename
```
would produce files
```commandline
extracted_channels_from_filename_channel_00.txt
extracted_channels_from_filename_channel_01.txt
extracted_channels_from_filename_channel_02.txt
extracted_channels_from_filename_channel_03.txt
```

The `--channels` flag is optional, and can be a range as above or an explicit comma separated list
of channels to extract, e.g., `--channels 3,5,8,10`.
If not provided the first 15 channels will be extracted.

The `'--output` flag is optional and will be replaced by the data file stem-name if not provided.
E.g., `filename.dat` would give `filename` for output.
The specified output is used as a base-name for the extracted files(s).

