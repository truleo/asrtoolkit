#!/usr/bin/env python
"""
Module for organizing SPH/MP3/WAV & STM files from a Corpus
"""

import glob
import os
import random
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from tqdm import tqdm

from asrtoolkit.file_utils.name_cleaners import basename, strip_extension

from .audio_file import AudioFile
from .exemplar import Exemplar
from .time_aligned_text import Transcript


def get_files(data_dir, extension):
    """
    Gets all files in a data directory with given extension
    """
    files = []
    if data_dir and os.path.exists(data_dir):
        files = glob.glob(data_dir + "/*." + extension)
    return files


class Corpus:
    """
    Create a Corpus object for storing information about
    the location and count of files in a Corpus
    """

    location = None
    exemplars = []
    n_words = 0

    def __init__(self, *args, **kwargs):
        """
        Initialize from location and populate list of
        SPH, WAV, or MP3 audio files
        and STM files into segments
        """
        for dictionary in args:
            if isinstance(dictionary, dict):
                for key, value in dictionary.items():
                    setattr(self, key, value)
        for key, value in kwargs.items():
            setattr(self, key, value)

        # only if not defined above should we search for exemplars
        # based on location
        if not self.exemplars:
            # instantiate exemplars for this object to override
            # static class variable
            self.exemplars = []

            audio_extensions_to_try = ["sph", "wav", "mp3"][::-1]
            self.exemplars += [
                Exemplar(
                    {
                        "audio_file": AudioFile(fl),
                        "transcript_file": Transcript(strip_extension(fl) + ".stm"),
                    }
                )
                for audio_extension in audio_extensions_to_try
                for fl in (
                    get_files(self.location, audio_extension) if self.location else []
                )
                if (os.path.exists(strip_extension(fl) + ".stm"))
            ]

            # gather all exemplars from /stm and /sph subdirectories if present
            self.exemplars += [
                Exemplar(
                    {
                        "audio_file": AudioFile(fl),
                        "transcript_file": Transcript(
                            self.location
                            + "/stm/"
                            + basename(strip_extension(fl))
                            + ".stm"
                        ),
                    }
                )
                for audio_extension in audio_extensions_to_try
                for fl in (
                    get_files(self.location + "/sph/", audio_extension)
                    if self.location
                    else []
                )
                if (
                    os.path.exists(
                        self.location + "/stm/" + basename(strip_extension(fl)) + ".stm"
                    )
                )
            ]

    def validate(self):
        """
        Check and validate each example after sorting by audio file hash
        since stm hash may change
        """
        dict_of_examples = {_.audio_file.hash(): _ for _ in self.exemplars}
        self.exemplars = [dict_of_examples[_] for _ in set(dict_of_examples)]
        return sum(_.validate() for _ in self.exemplars)

    def count_exemplar_words(self):
        """
        Count the number of words in valid Corpus exemplars
        adds attribute n_words to exemplars
        """
        valid_exemplars = [_ for _ in self.exemplars if _.validate()]

        total_words = 0
        for eg in valid_exemplars:
            eg.n_words = eg.count_words()
            total_words += eg.n_words
        return valid_exemplars, total_words

    def split(self, split_words, min_segments=10):
        """
        Select exemplars to create data split with specified number of words and minimum number of segments
        Returns the new splits as separate corpora
        """
        valid_exemplars, total_words = self.count_exemplar_words()

        # Raise error if we inputs are invalid to avoid infinite loop
        if split_words < 0 or split_words > total_words:
            raise ValueError(
                "cannot split Corpus with {} words into split with {} words".format(
                    total_words, split_words
                )
            )

        exemplars_in_split = []
        word_counter, seg_counter = 0, 0
        while word_counter <= split_words or seg_counter <= min_segments:
            exemplars_in_split += [
                valid_exemplars.pop(random.randrange(len(valid_exemplars)))
            ]
            word_counter += exemplars_in_split[-1].n_words
            seg_counter += len(exemplars_in_split[-1].transcript_file.segments)

        new_corpus = Corpus(
            {"location": self.location, "exemplars": exemplars_in_split,}
        )

        remaining_corpus = self - new_corpus
        remaining_corpus.location = self.location

        return remaining_corpus, new_corpus

    def log(self):
        """
        Log what each hashed example contains
        """
        return {
            _.hash(): {
                "audio_file": _.audio_file.location,
                "audio_file_hash": _.audio_file.hash(),
                "transcript_file": _.transcript_file.location,
                "transcript_file_hash": _.transcript_file.hash(),
            }
            for _ in self.exemplars
        }

    def calculate_number_of_segments(self):
        """
        Calculate how many segments are in this Corpus
        """
        return sum(len(eg.transcript_file.segments) for eg in self.exemplars)

    def prepare_for_training(self, target=None, nested=False, sample_rate=16000):
        """
        Run validation and audio file preparation steps
        """

        # write Corpus back in place if no target
        target = self.location if target is None else target

        executor = ThreadPoolExecutor()

        # process audio files concurrently for speed
        futures = [
            executor.submit(
                partial(
                    _.prepare_for_training,
                    target=target,
                    sample_rate=sample_rate,
                    nested=nested,
                )
            )
            for _ in self.exemplars
        ]

        # trigger conversion and gather results
        new_exemplars = [future.result() for future in tqdm(futures)]

        new_corpus = Corpus(
            {
                "location": target,
                "exemplars": [eg for eg in new_exemplars if eg is not None],
            }
        )
        new_corpus.validate()
        return new_corpus.log()

    def __add__(self, other):
        """Allow addition of corpora via + operator"""
        return Corpus({"location": None, "exemplars": self.exemplars + other.exemplars})

    def __iadd__(self, other):
        """Allow addition of corpora via += operator"""
        self.exemplars = self.exemplars + other.exemplars
        return self

    def __sub__(self, other):
        """Allow addition of corpora via - operator"""
        return Corpus(
            {
                "location": None,
                "exemplars": [_ for _ in self.exemplars if _ not in other.exemplars],
            }
        )

    def __isub__(self, other):
        """Allow subtraction of corpora via -= operator"""
        self.exemplars = [_ for _ in self.exemplars if _ not in other.exemplars]

    def __getitem__(self, given):
        """Allow slicing of corpora via []"""
        return Corpus(
            {
                "location": self.location,
                "exemplars": [self.exemplars[given]]
                if not isinstance(given, slice)
                else self.exemplars[given],
            }
        )
