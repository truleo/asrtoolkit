#!/usr/bin/env python
"""
Module for reading STM files

Expected file format is derived from http://www1.icsi.berkeley.edu/Speech/docs/sctk-1.2/infmts.htm#stm_fmt_name_0

This expects a Segment from class derived in convert_text
"""

from asrtoolkit.clean_formatting import clean_up

# leave in place for other imports
from asrtoolkit.data_handlers.data_handlers_common import footer, header, separator
from asrtoolkit.data_structures import Segment


def footer():
    "Returns footer with trailing line break"
    return "\n"


def format_segment(seg):
    """
    :param seg: Segment object
    :return str: text for a particular STM line (see Segment __str__ method)
      Formats a Segment assuming it's an instance of class Segment with elements
      filename, channel, speaker, start and stop times, label, and text
    """
    # clean_up used to unformat stm file text
    return " ".join(
        [
            str(getattr(seg, _))
            for _ in ("filename", "channel", "speaker", "start", "stop", "label")
        ]
        + [clean_up(seg.text)]
    )


def parse_line(line):
    """
    :param line: str; a single line of an stm file
    :return: Segment object if STM file line contains accurately formatted data; else None
    """
    data = line.strip().split()

    seg = None
    if len(data) > 6:
        filename, channel, speaker, start, stop, label = data[:6]
        text = " ".join(data[6:])
        seg = Segment(
            {
                "filename": filename,
                "channel": channel,
                "speaker": speaker,
                "start": start,
                "stop": stop,
                "label": label,
                "text": text,
            }
        )
    return seg if (seg is not None) and seg.validate() else None


def read_file(file_name):
    """
    Reads an STM file, skipping any gap lines
    :return: list of Segment objects
    """
    Segments = []
    with open(file_name, encoding="utf-8") as f:
        for line in f:
            seg = parse_line(line)
            if seg is not None:
                Segments.append(seg)
    return Segments


__all__ = [header, footer, separator]
