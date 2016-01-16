# import nltk
import logging
import string
from statistics import mean, stdev, StatisticsError
# from nltk import word_tokenize
from collections import Counter
import logging
import codecs
import string
import jsonhandler
import sys
import argparse


class Database:

    """A database contains authors of texts."""

    def __init__(self, considered_words=0, real_words=False):
        """
        Initialize a database.

        Keyword arguments:
        considered_words -- Specifies how many of the most common words
                            are used for calculating the delta scores.
                            If 0 then all are used.
                            (default 0)
        real_words -- Specifies if only real words (i.e. alphabetic words)
                      should be used for the algorithm. If False then also
                      words like '.', ';' etc. are considered.
                      (default False)
        """

        # The following list contains all authors
        # of the database.
        self.authors = []

        # The following counter object contains all
        # words of the database and their respective
        # number of occurrences.
        self.counter = Counter()

        # The following two dictionaries contain the
        # mean frequencies and standard deviations of
        # the words in the database respectively.
        # This is with respect to the set of all texts
        # in the database.
        self.mean = {}
        self.stdev = {}

        self.txt_number = 0  # the number of texts in the database

        # The following variable states the number of
        # words to be considered for the algorithm.
        # For example: a value of 30 indicates that
        # we consider the 30 most common words for
        # our calculations.
        # A value of 0 indicates that we do not limit
        # the words used for the calculations.
        self.considered_words = considered_words

        # The following boolean value decides if the
        # algorithm considers only real words (like
        # 'the', 'go', 'dog' etc.) or if the algorithm
        # should consider all words (this includes
        # also interpunctuation).
        self.real_words = real_words

    def add_author(self, *authors):
        """Add an authors to the database."""
        for author in authors:
            self.authors.append(author)

    def calc_counter(self):
        """
        Count the occurrences of every word in the database
        and how many texts there are.
        """
        logging.info("Database: Counting.")
        for author in self.authors:
            author.calc_counter()
            self.counter += author.counter
            self.txt_number += author.txt_number

        # Restrict the words to those who contain only *real* words
        if self.real_words is True:
            # The key k is a tuple of the form (word, tag).
            # We check if the first argument is a real word in the
            # sense that it contains at least one alphabetic character (a-zA-Z)
            # such that words like "middle-age" or "I'll" are accepted.
            self.counter = Counter({k: v for k, v in dict(self.counter).items()
                                    if sum(c in string.ascii_letters for c in k[0]) > 0})

        # Restrict the number of words used for the calculations
        if self.considered_words > 0:
            n = self.considered_words
            # The following code takes the n most_common words
            # in the database (this yields a list of tuples)
            # and converts it to a dictionary and then again
            # to a counter.
            self.counter = Counter(dict(self.counter.most_common(n)))

    def calc_mean_stdev(self):
        """
        Calculate the mean frequencies and standard deviation
        of every word in the database.
        calc_counter has to be executed before.
        """

        logging.info("Database: Calculating mean and stdev.")
        for word in self.counter:
            word_scores = []
            for author in self.authors:
                for text in author.texts:
                    if word in text.scores:
                        word_scores.append(text.scores[word])
                    else:  # word is *not* in text.scores,
                          # i.e. score (frequency) = 0
                        word_scores.append(0)

            self.mean[word] = mean(word_scores)
            try:
                self.stdev[word] = stdev(word_scores, self.mean[word])
            except StatisticsError:
                # could happen if a word occurs only in one text
                logging.debug(
                    "Database: Calculating mean and stdev: StatisticsError")
                self.stdev[word] = 0

    def process(self):
        """
        Process the Database, i.e. count all words and determine
        their mean frequencies and standard deviation with respect
        to all texts.
        """
        self.calc_counter()
        self.calc_mean_stdev()


class Author:

    """Represents an author with a collection of his texts."""

    def __init__(self, name):
        self.name = name           # the author's name
        self.texts = []            # a list of the author's text
        self.counter = Counter()   # a counter of all words of the author

        # The following two dictionaries contain
        # the mean frequencies and their standard
        # deviation with respect to the set of all
        # texts of this author.
        self.mean = {}
        self.stdev = {}

        self.txt_number = 0   # the number of texts of this author

        # The following dictionary contains the
        # zscores of this author's words again
        # with respect to the set of all texts of
        # this author
        self.zscores = {}

        # Has the counter already been calculated?
        self.__counter_calculated = False

    def add_text(self, *texts):
        """Add texts to this author."""
        for text in texts:
            self.texts.append(text)
            self.txt_number += 1

    def calc_counter(self):
        """Count the occurrences of every word in texts of this author."""

        if not self.__counter_calculated:
            logging.info("Author '%s': Calculating Counter.", self.name)
            for text in self.texts:
                self.counter += text.counter
            self.__counter_calculated = True
        else:
            logging.info("Author '%s': Counter has already been calculated.",
                         self.name)

    def calc_mean_stdev(self):
        """
        Calculate the mean frequencies and standard deviation of every word.
        calc_counter has to be executed before
        """
        logging.info("Author '%s': Calculating mean and stdev.", self.name)
        for word in self.counter:
            word_scores = []
            for text in self.texts:
                if word in text.scores:
                    word_scores.append(text.scores[word])
                else:
                    # word is *not* in text, i.e. score (frequency) is 0!
                    word_scores.append(0)

            self.mean[word] = mean(word_scores)
            try:
                self.stdev[word] = stdev(word_scores, self.mean[word])
            except StatisticsError:
                # This happens, for example, if the author has only one text
                logging.debug("Author '%s': Calculating mean" +
                              "and stdev: StatisticsError", self.name)
                self.stdev[word] = 0

    def calc_zscores(self, database):
        """
        Calculate the zscores of this author's words with respect
        to the specified database. These are standardized variables (i.e.
        they have an expected value of 0 and a variance of 1).
        calc_mean_stdev has to be executed before
        """
        for word in self.counter:
            # We have to check if the word is in the database's counter because
            # the database's might be restricted, e.g. most common words or
            # only real words. (see the comments of Database.calc_counter())
            if word in database.counter:
                if database.stdev[word] != 0:
                    self.zscores[word] = (self.mean[word] - database.mean[word]) \
                        / database.stdev[word]
                else:
                    self.zscores[word] = 0

    def calc_cmsz(self, database):
        """
        Calculate counter, mean, standard deviation and zscores of
        this author with respect to the specified database
        """
        self.calc_counter()
        self.calc_mean_stdev()
        self.calc_zscores(database)


class Text:

    """Represents a single text."""

    def __init__(self, raw, name, process=True, pos_tag=True):
        """
        Initialize a text object with raw text.

        Keyword arguments:
        raw -- Raw text as a string.
        name -- Name of the text.
        process -- If true then directly process the text. (default: True)
        pos_tag -- Should the raw text be POS tagged? (default: True)
        """
        self.name = name
        self.raw = raw
        self.tokens = []
        self.tags = []
        self.counter = Counter()
        self.scores = {}
        self.zscores = {}
        self.sum = 0  # number of words in self.raw

        if process:
            self.process(pos_tag=pos_tag)

    def process(self, pos_tag=True):
        """
        Process the text at hand, i.e. it is tokenized, tagged and
        counted. Moreover, we calculate the frequency/score of every word
        (relative frequency).

        Keyword arguments:
        pos_tag -- Should the raw text be POS tagged? (default: True)
        """
        if pos_tag:
            # A list of all tokens can be seen
            # with nltk.help.upenn_tagset()
            logging.info("Tokenizing '%s'", self.name)
            self.tokens = nltk.word_tokenize(self.raw)
            logging.info("Tagging '%s'", self.name)
            self.tags = nltk.pos_tag(self.tokens)
        else:
            logging.info("Preparing '%s'", self.name)
            # the following takes all alphabetic words normalized to lowercase
            # from the raw data
            self.tags = [x for x in
                        [''.join(c for c in word if c.isalpha()).lower()
                         for word in self.raw.split()]
                         if x != '']

        logging.info("Counting '%s'", self.name)
        self.counter = Counter(self.tags)
        self.sum = sum(self.counter.values())

        logging.info("Calculating the scores of '%s'", self.name)
        for x in self.counter:
            self.scores[x] = self.counter[x] / self.sum

    def calc_zscores(self, database):
        """
        Calculate the z-scores with respect to the specified database. These are
        standardized variables (i.e. they have an expected value of 0 and
        a variance of 1).
        process has to be executed before.
        """
        logging.info("Calculating the zscores of '%s'", self.name)

        # Here we have a problem if there's a word in the
        # database whose standard deviation is 0. But this
        # should only happen if there is only one text in
        # the database or the word has the same frequency
        # in every text. For the moment, this shouldn't be
        # a problem.

        for word in database.counter:
            if word in self.counter:
                self.zscores[word] = (self.scores[word]
                                      - database.mean[word]) / database.stdev[word]

    def calc_delta(self, database, author):
        """
        Calculate the delta for this text and the given author.
        Specify a database and an author from this database.
        calc_zscores has to be executed before
        """
        logging.info("Text '%s': Calculating delta for author '%s'.",
                     self.name, author.name)
        absolute_differences = {}
        absolute_differences_sum = 0
        for word in database.counter:
            if word in self.counter:
                if word in author.zscores:
                    absolute_differences[word] = abs(
                        self.zscores[word] - author.zscores[word])
                else:
                    absolute_differences[word] = abs(self.zscores[word])
                absolute_differences_sum += absolute_differences[word]
        return absolute_differences_sum  # / sum(self.counter.values())


def tira(corpusdir, outputdir):
    """
    Keyword arguments:
    corpusdir -- Path to a tira corpus
    outputdir -- Output directory
    """
    pos_tag = False

    jsonhandler.loadJson(corpusdir)
    jsonhandler.loadTraining()

    # creating training data
    logging.info("Load the training data...")
    database = Database(150, real_words=True)
    for candidate in jsonhandler.candidates:
        author = Author(candidate)
        for training in jsonhandler.trainings[candidate]:
            logging.info(
                "Author '%s': Loading training '%s'", candidate, training)
            text = Text(jsonhandler.getTrainingText(candidate, training),
                        candidate + " " + training,
                        pos_tag=pos_tag)
            author.add_text(text)
        database.add_author(author)
    database.process()

    for author in database.authors:
        author.calc_cmsz(database)

    # do some training, i.e. check which parameter is best
    logging.info("Start training...")
    results = {}
    for length in range(150, 301, 50):
        logging.info("Check for %s words.", length)
        database.considered_words = length
        database.process()
        results[length] = 0
        for correct_author in database.authors:
            for training in jsonhandler.trainings[correct_author.name]:
                trainingcase = Text(
                    jsonhandler.getTrainingText(correct_author.name, training),
                    "Trainingcase",
                    pos_tag=pos_tag)
                trainingcase.calc_zscores(database)
                deltas = {}
                for author in database.authors:
                    deltas[author] = trainingcase.calc_delta(database, author)
                if min(deltas, key=deltas.get) == correct_author:
                    results[length] += 1
    length = max(results, key=results.get)
    logging.info("Choose %s as length.", str(length))

    # reconfigure the database with length
    database.considered_words = length
    database.process()

    # run the testcases
    results = []
    for unknown in jsonhandler.unknowns:
        testcase = Text(jsonhandler.getUnknownText(unknown),
                        unknown,
                        pos_tag=pos_tag)
        testcase.calc_zscores(database)
        deltas = {}
        for author in database.authors:
            deltas[author] = testcase.calc_delta(database, author)
        results.append((unknown, min(deltas, key=deltas.get).name))

    texts = [text for (text, candidate) in results]
    cands = [candidate for (text, candidate) in results]
    jsonhandler.storeJson(path=outputdir, texts, cands)


def main():
    parser = argparse.ArgumentParser(description='Tira submission for Delta.')
    parser.add_argument('-i',
                        action='store',
                        help='Path to input directory')
    parser.add_argument('-o',
                        action='store',
                        help='Path to output directory')

    args = vars(parser.parse_args())

    corpusdir = args['i']
    outputdir = args['o']

    tira(corpusdir, outputdir)


if __name__ == "__main__":
    # execute only if run as a script
    logging.basicConfig(level=logging.ERROR,
                        format='%(asctime)s %(levelname)s: %(message)s')
    main()
