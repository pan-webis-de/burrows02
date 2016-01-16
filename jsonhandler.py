# META_FNAME - name of the meta-file.json
# GT_FNAME - name of the ground-truth.json
# OUT_FNAME - file to write the output in (answers.json)
# encoding - encoding of the texts (from json)
# language - language of the texts (from json)
# upath - path of the 'unknown' dir in the corpus (from json)
# candidates - list of candidate author names (from json)
# unknowns - list of unknown filenames (from json)
# trainings - dictionary with lists of filenames of trainingtexts for each author
# 	{"candidate2":["file1.txt", "file2.txt", ...], "candidate2":["file1.txt", ...] ...}
# trueAuthors - list of true authors of the texts (from GT_FNAME json)
# correstponding to 'unknowns'

'''
EXAMPLE:

import jsonhandler

candidates = jsonhandler.candidates
unknowns = jsonhandler.unknowns
jsonhandler.loadJson("testcorpus")

# If you want to do training:
jsonhandler.loadTraining()
for cand in candidates:
	for file in jsonhandler.trainings[cand]:
		# Get content of training file 'file' of candidate 'cand' as a string with:
		# jsonhandler.getTrainingText(cand, file)

# Create lists for your answers (and scores)
authors = []
scores = []

# Get Parameters from json-file:
l = jsonhandler.language
e = jsonhandler.encoding

for file in unknowns:
	# Get content of unknown file 'file' as a string with:
	# jsonhandler.getUnknownText(file)
	# Determine author of the file, and score (optional)
	author = "oneAuthor"
	score = 0.5
	authors.append(author)
	scores.append(score)

# Save results to json-file out.json (passing 'scores' is optional)
jsonhandler.storeJson(unknowns, authors, scores)

# If you want to evaluate the ground-truth file
loadGroundTruth()
# find out true author of document unknowns[i]:
# trueAuthors[i]
'''

import os
import json
import codecs

META_FNAME = "meta-file.json"
OUT_FNAME = "answers.json"
GT_FNAME = "ground-truth.json"

# always run this method first to evaluate the meta json file. Pass the
# directory of the corpus (where meta-file.json is situated)


def loadJson(corpus):
    global corpusdir, upath, candidates, unknowns, encoding, language
    corpusdir += corpus
    mfile = open(os.path.join(corpusdir, META_FNAME), "r")
    metajson = json.load(mfile)
    mfile.close()

    upath += os.path.join(corpusdir, metajson["folder"])
    encoding += metajson["encoding"]
    language += metajson["language"]
    candidates += [author["author-name"]
                   for author in metajson["candidate-authors"]]
    unknowns += [text["unknown-text"] for text in metajson["unknown-texts"]]

# run this method next, if you want to do training (read training files etc)


def loadTraining():
    for cand in candidates:
        trainings[cand] = []
        for subdir, dirs, files in os.walk(os.path.join(corpusdir, cand)):
            for doc in files:
                trainings[cand].append(doc)

# get training text 'fname' from candidate 'cand' (obtain values from
# 'trainings', see example above)


def getTrainingText(cand, fname):
    dfile = codecs.open(os.path.join(corpusdir, cand, fname), "r", "utf-8")
    s = dfile.read()
    dfile.close()
    return s

# get training file as bytearray


def getTrainingBytes(cand, fname):
    dfile = open(os.path.join(corpusdir, cand, fname), "rb")
    b = bytearray(dfile.read())
    dfile.close()
    return b

# get unknown text 'fname' (obtain values from 'unknowns', see example above)


def getUnknownText(fname):
    dfile = codecs.open(os.path.join(upath, fname), "r", "utf-8")
    s = dfile.read()
    dfile.close()
    return s

# get unknown file as bytearray


def getUnknownBytes(fname):
    dfile = open(os.path.join(upath, fname), "rb")
    b = bytearray(dfile.read())
    dfile.close()
    return b

# run this method in the end to store the output in the 'path' directory as OUT_FNAME
# pass a list of filenames (you can use 'unknowns'), a list of your
# predicted authors and optionally a list of the scores (both must of
# course be in the same order as the 'texts' list)


def storeJson(path, texts, cands, scores=None):
    answers = []
    if scores == None:
        scores = [1 for text in texts]
    for i in range(len(texts)):
        answers.append(
            {"unknown_text": texts[i], "author": cands[i], "score": scores[i]})
    f = open(os.path.join(path, OUT_FNAME), "w")
    json.dump({"answers": answers}, f, indent=2)
    f.close()

# if you want to evaluate your answers using the ground-truth.json, load
# the true authors in 'trueAuthors' using this function


def loadGroundTruth():
    tfile = open(os.path.join(corpusdir, GT_FNAME), "r")
    tjson = json.load(tfile)
    tfile.close()

    global trueauthors
    for i in range(len(tjson["ground-truth"])):
        trueAuthors.append(tjson["ground-truth"][i]["true-author"])

# initialization of global variables
encoding = ""
language = ""
corpusdir = ""
upath = ""
candidates = []
unknowns = []
trainings = {}
trueAuthors = []
