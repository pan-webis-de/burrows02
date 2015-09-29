import logging
import codecs
import string
import jsonhandler
import sys
import argparse

from delta import Database, Author, Text

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
            logging.info("Author '%s': Loading training '%s'", candidate,training)
            text = Text(jsonhandler.getTrainingText(candidate,training), 
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
    for length in range(150,301,50):
        logging.info("Check for %s words.", length)
        database.considered_words = length
        database.process()
        results[length] = 0
        for correct_author in database.authors:
            for training in jsonhandler.trainings[correct_author.name]:
                trainingcase = Text(jsonhandler.getTrainingText(correct_author.name,training),
                                    "Trainingcase",
                                    pos_tag=pos_tag)
                trainingcase.calc_zscores(database)
                deltas = {}
                for author in database.authors:
                    deltas[author] = trainingcase.calc_delta(database,author)
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
            deltas[author] = testcase.calc_delta(database,author)
        results.append((unknown,min(deltas, key=deltas.get).name))
        
    texts = [text for (text,candidate) in results]
    cands = [candidate for (text,candidate) in results]
    jsonhandler.storeJson(texts, cands, path=outputdir)

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
    logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s: %(message)s')
    main()
