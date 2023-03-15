# Automatic Speech Recognition (ASR) Toolkit

---

## Overview

ASRToolkit provides tools for file conversion and ASR corpora organization.
These are intended to simplify the workflow for building, customizing, and analyzing ASR models, useful for scientists, engineers, and other technologists in speech recognition.

### File formats supported

File formats have format-specific handlers in asrtoolkit/data_handlers.
The scripts `convert_transcript` and `wer` support [`stm`](http://www1.icsi.berkeley.edu/Speech/docs/sctk-1.2/infmts.htm), 
[`srt`](http://zuggy.wz.cz/), 
[`vtt`](https://w3c.github.io/webvtt/), 
`txt`, 
[GreenKey `json`](https://greenkeytech.com/) formatted transcripts, 
and [Truleo `json`](https://www.truleo.co/) transcripts.

A custom `html` format is also available, though this should not be considered a stable format for long term storage as it is subject to change without notice.

### convert_transcript 
```text
usage: convert_transcript [-h] input_file output_file

convert a single transcript from one text file format to another

positional arguments:
  input_file   input file
  output_file  output file

optional arguments:
  -h, --help   show this help message and exit
```
This tool allows for easy conversion among file formats listed above.

Note: Attributes of a `Segment` object not present in a parsed file retain their default values

- For example, a `Segment` object is created for each line of an STM line
- each is initialized with the following default values which are not encoded in STM files: `formatted_text=''`;  `confidence=1.0` 


### wer
```text
usage: wer [-h] [--char-level] [--ignore-nsns]
           reference_file transcript_file

Compares a reference and transcript file and calculates word error rate (WER)
between these two files

positional arguments:
  reference_file   reference "truth" file
  transcript_file  transcript possibly containing errors

optional arguments:
  -h, --help       show this help message and exit
  --char-level     calculate character error rate instead of word error rate
  --ignore-nsns    ignore non silence noises like um, uh, etc.

This tool allows for easy comparison of reference and hypothesis transcripts in any format listed above.
```

### clean_formatting 
```text
usage: clean_formatting.py [-h] files [files ...]

cleans input *.txt files and outputs *_cleaned.txt

positional arguments:
  files       list of input files

optional arguments:
  -h, --help  show this help message and exit

```
This script standardizes how abbreviations, numbers, and other formatted text is expressed so that ASR engines can easily use these files as training or testing data.
Standardizing the formatting of output is essential for reproducible measurements of ASR accuracy.

### split_audio_file 
```text
usage: split_audio_file [-h] [--target-dir TARGET_DIR] audio_file transcript

Split an audio file using valid segments from a transcript file.
or this
utility, transcript files must contain start/stop times.

positional arguments:
  audio_file            input audio file
  transcript            transcript

optional arguments:
  -h, --help            show this help message and exit
  --target-dir TARGET_DIR
                        Path to target directory
```

### prepare_audio_corpora
```text
usage: prepare_audio_corpora [-h] [--target-dir TARGET_DIR]
                             corpora [corpora ...]

Copy and organize specified corpora into a target directory.
Training, testing, and development sets will be created automatically if not already
defined.

positional arguments:
  corpora               Name of one or more directories in directory this
                        script is run

optional arguments:
  -h, --help            show this help message and exit
  --target-dir TARGET_DIR
                        Path to target directory
```
This script scrapes a list of directories for paired STM and SPH files.
If `train`, `test`, and `dev` folders are present, these labels are used for the output folder.
By default, a target directory of 'input-data' will be created.
Note that filenames with hyphens will be sanitized to underscores and that audio files will be forced to single channel, 16 kHz, signed PCM format.
If two channels are present, only the first will be used.

### degrade_audio_file 
```text
usage: degrade_audio_file input_file1.wav input_file2.wav

Degrade audio files to 8 kHz format similar to G711 codec
```
This script reduces audio quality of input audio files so that acoustic models can learn features from telephony with the G711 codec.

### Requirements

- Python >= 3.6.2 with `pip`

## Contributing

### Code of Conduct

Please make sure you read and observe our [Code of Conduct](https://raw.githubusercontent.com/truleo/asrtoolkit/master/CODE_OF_CONDUCT.md).

### Pull Request process

1. Fork it
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

_NOTE:_ Commits and pull requests to FINOS repositories will only be accepted from those contributors with an active, executed Individual Contributor License Agreement (ICLA) with FINOS OR who are covered under an existing and active Corporate Contribution License Agreement (CCLA) executed with FINOS.
Commits from individuals not covered under an ICLA or CCLA will be flagged and blocked by the FINOS Clabot tool.
Please note that some CCLAs require individuals/employees to be explicitly named on the CCLA.

*Need an ICLA? Unsure if you are covered under an existing CCLA? Email [help@finos.org](mailto:help@finos.org)*

## Maintainers

- [Matthew Goldey](https://github.com/mgoldey)
- [Tejas Shastry](https://github.com/tshastry)

For all other authors, please see the [list of contributors].

## License

The code in this repository is distributed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).

Copyright 2020 GreenKey Technologies

<!-- Markdown link & img defs -->
[FINOS]: https://www.finos.org
[SemVer]: http://semver.org
[list of contributors]: https://github.com/truleo/asrtoolkit/graphs/contributors
[tags on this repository]: https://github.com/truleo/asrtoolkit/tags
