#!/usr/bin/env python
"""
Module for reading rev.ai JSON files
"""

import json
import logging

from asrtoolkit.data_structures import Segment

LOGGER = logging.getLogger(__name__)
separator = ",\n"



def parse_segment(input_seg):
    """
    Creates an asrtoolkit Segment object from an input rev segment
    :param: input_seg: rev.ai segment-level dict
    :return: asrtoolkit Segment object
    """
    extracted_dict = {}
    extracted_dict["speaker"] = input_seg["speaker"]
    extracted_dict["start"] = min(element["ts"] for element in input_seg["elements"] if "ts" in element)
    extracted_dict["stop"] = max(element["end_ts"] for element in input_seg["elements"] if "end_ts" in element)
    extracted_dict["text"] = "".join(element["value"] for element in input_seg["elements"])

    seg = Segment(extracted_dict)

    return seg if seg and seg.validate() else None


def read_in_memory(input_data):
    """
    Reads input json objects

    :param: input_data: dict with key 'monologues'
      input_data['segments']: List[Dict];
      - Segment_dicts contain key/val pairs that map to `segment` attributes
        NB that labels of mapped key-attribute pairs may differ
          for example, Segment['startTimeSec'] -> Segment.start

    :return: list of Segment objects
      applies `parse_segment` function to each dict in input_data['segments']

    """
    segments = [_ for _ in map(parse_segment, input_data.get("monologues", []))]
    return segments


def read_file(file_name):
    """
    Reads a JSON file, skipping any bad Segments
    """
    with open(file_name, encoding="utf-8") as f:
        input_json = json.load(f)
        segments = read_in_memory(input_json)
    return segments
