#!/usr/bin/env python
"""
Module for common utils for WEBVTT files

This expects a segment from class derived in convert_text
"""

import logging
import re

from asrtoolkit.data_structures import Segment

LOGGER = logging.getLogger(__name__)
non_transcript_marks = re.compile(r"\[[A-Za-z0-9]{1,}\]")


def read_caption(caption):
    """
    Parses caption object to return a segment object
    """
    seg = None

    try:
        start = caption.start_in_seconds
        stop = caption.end_in_seconds

        text = re.sub(non_transcript_marks, lambda v: "", caption.text.strip()).strip()

        seg = Segment({"start": start, "stop": stop, "text": text})
    except Exception as exc:
        seg = None
        LOGGER.exception(exc)

    return seg if seg and seg.validate() else None
