# corpusdir - subdir with corpus
# META_FNAME - name of the meta-file.json
# OUT_FNAME - file to write the output in (out.json)
# upath - path of the 'unknown' dir in the corpus
# candidates - list of candidate author names (from json)
# unknowns - list of unknown filenames (from json)
# trainings - dictionary wirh lists of filenames of trainingtexts for each author

# Usage:
# loadJson(corpusname), with corpusname from commandline
# OPTIONAL: loadTraining()
# OPTIONAL: getTrainingText(jsonhandler.candidate[i], jsonhandler.trainings[jsonhandler.candidates[i]][j]), gets trainingtext j from candidate i as a string
# getUnknownText(jsonhandler.unknowns[i]), gets unknown text i as a string
# storeJson(candidates, texts, scores), with list of candidates as candidates (jsonhandler.candidates can be used), list of texts as texts and list of scores as scores, last argument can be ommitted

import os, json, pprint

META_FNAME = "meta-file.json"
OUT_FNAME = "out.json"
corpusdir = ""
upath = ""
candidates = []
unknowns = []
trainings = {}

def loadJson(corpus):
	global corpusdir
	corpusdir = corpus
	mfile = open(os.path.join(corpusdir, META_FNAME), "r")
	metajson = json.load(mfile)
	mfile.close()

	global upath, candidates, unknowns
	upath = os.path.join(corpusdir, metajson["folder"])
	candidates = [author["author-name"] for author in metajson["candidate-authors"]]
	unknowns = [text["unknown-text"] for text in metajson["unknown-texts"]]

def getUnknownText(fname):
	dfile = open(os.path.join(upath, fname))
	s = dfile.read()
	dfile.close()
	return s

def loadTraining():
	for cand in candidates:
		trainings[cand] = []
		for subdir, dirs, files in os.walk(os.path.join(corpusdir, cand)):
			for doc in files:
				trainings[cand].append(doc)

def getTrainingText(cand, fname):
	dfile = open(os.path.join(corpusdir, cand, fname))
	s = dfile.read()
	dfile.close()
	return s

def storeJson(texts, cands, scores = None):
	answers = []
	if scores == None:
		scores = [1 for text in texts]
	for i in range(len(texts)):
		answers.append({"unknown_text": texts[i], "author": cands[i], "score": scores[i]})
	f = open(os.path.join(corpusdir, OUT_FNAME), "w")
	json.dump({"answers": answers}, f, indent=2)
	f.close()
