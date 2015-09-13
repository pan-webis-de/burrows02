# burrows02
## Literature
* Burrows, J.F. (2002). ‘Delta’: A measure of stylistic difference and a guide to likely authorship. Literary and Linguistic Computing, 17(3), 267-287.
* Bird, S., Loper, E. and Klein, E. (2009). Natural Language Processing with Python. O’Reilly Media Inc.

## How to install NLTK 
This implementation of Burrow's 'Delta' uses NLTK only to tokenize and tag the
texts at hand. Therefore, you need to [install NLTK](http://www.nltk.org/install.html). 
Then open a Python shell and run `nltk.download()` after having imported `nltk`.
Select and install `maxent_treebank_pos_tagger` in the Models tab.

## How to use this implementation
This code was written in `Python 3.4.3`.

The `pan12a` function of `testcases.py` provides an easy example of how to use
this implementation. 