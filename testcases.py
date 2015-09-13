import logging
import codecs
import string

from delta import Database, Author, Text

def raw_from_file(file,enc='utf_8'):
    """
    Return the raw text from a file.
    
    Keyword arguments:
    file -- A path to the file.
    enc  -- Encoding of the file (default 'utf_8') 
    """
        
    f = codecs.open(file,encoding=enc) 
    raw = f.read()
    return raw


def pan12a(training, test):
    """
    Run the Algorithm with PAN12 A data.
    
    Keyword arguments:
    train -- The path to the PAN12 training folder. 
    test -- The path to the PAN12 test folder.
    """
    # training data for PAN12 A
    database = Database(considered_words=100,real_words=True)
    
    # create the authors
    author_a = Author("Author A")
    author_b = Author("Author B")
    author_c = Author("Author C")
    
    # ... and load the texts
    train_a1 = Text(raw_from_file(
        training + "12AtrainA1.txt"), "12AtrainA1.txt")
    train_a2 = Text(raw_from_file(
        training + "12AtrainA2.txt"), "12AtrainA2.txt")
    train_b1 = Text(raw_from_file(
        training + "12AtrainB1.txt"), "12AtrainB1.txt")
    train_b2 = Text(raw_from_file(
        training + "12AtrainB2.txt"), "12AtrainB2.txt")
    train_c1 = Text(raw_from_file(
        training + "12AtrainC1.txt"), "12AtrainC1.txt")
    train_c2 = Text(raw_from_file(
        training + "12AtrainC2.txt"), "12AtrainC2.txt")
    
    author_a.add_text(train_a1, train_a2)
    author_b.add_text(train_b1, train_b2)
    author_c.add_text(train_c1, train_c2)
        
    database.add_author(author_a, author_b, author_c)
    
    database.process()
    
    # calculate the author's counter, mean, standard deviation and z-scores
    author_a.calc_cmsz(database)
    author_b.calc_cmsz(database)
    author_c.calc_cmsz(database)
      
    # now the test cases
    files = ["12Atest01.txt","12Atest02.txt","12Atest03.txt",
             "12Atest04.txt","12Atest05.txt","12Atest06.txt"]
    for file in files:
        test_text = Text(raw_from_file(test + file), file)
        test_text.calc_zscores(database) # calculate zscores for the sample
        # now calculate the delta for each author
        delta = {}
        delta['A'] = test_text.calc_delta(database,author_a)
        delta['B'] = test_text.calc_delta(database,author_b)
        delta['C'] = test_text.calc_delta(database,author_c)
        print("Delta scores for text '%s':" % file)
        print("Author A: ", delta['A'])
        print("Author B: ", delta['B'])
        print("Author C: ", delta['C'])
        print("Minimum delta has Author", min(delta, key=delta.get))


def pan12(problem, problem_training, n_authors, n_training, n_testcases, 
          considered_words, real_words, training_path, test_path):
    """
    Run the algorithm with PAN12 data. 
    This works for classification problems.
    
    Keyword arguments:
    problem -- The problem of PAN12 ('A','B' etc.)
    problem_training -- Using the trainingdata of this problem.
    n_authors -- The number of authors of this case.
    n_training -- The number of training files per author.
    n_testcases -- The number of testcases.
    considered_words -- How many of the most common words should be considered?
    real_words -- Only alphabetic words?
    training_path -- The path to the PAN12 training folder
    test_path -- The path to the PAN12 test folder
    """
    print("Problem: PAN12 " + problem)
    print("considered_words: " + str(considered_words))
    print("real_words: " + str(real_words))
    
    
    database = Database(considered_words, real_words)
    
    # Load the training data
    for author_letter in string.ascii_uppercase[0:n_authors:]:
        author = Author("Author " + author_letter)
        for testcase_number in range(1,n_training+1):
             # "12AtrainA1.txt"
            testcase = Text(raw_from_file(
                training_path + "12" + problem_training + "train" + author_letter 
                              + str(testcase_number) + ".txt"),
                "Training " + author_letter + " " + str(testcase_number))
            author.add_text(testcase)
        database.add_author(author)
    database.process()
    
    for author in database.authors:
        author.calc_cmsz(database)
        
    
    # Next, do the testcases
    for testcase_number in range(1,n_testcases+1):
        testcase = Text(raw_from_file(
            test_path + "12" + problem + "test"
                      +  str(testcase_number).zfill(2) + ".txt"),
            "Testcase " + problem + " " + str(testcase_number))
        testcase.calc_zscores(database)
        
        # now calculate the deltas
        deltas = {}
        for author in database.authors:
            deltas[author] = testcase.calc_delta(database,author)
            
        print("Deltas for Testcase " + str(testcase_number) + ":")
        for author in sorted(deltas, key=deltas.get):
            print(author.name + ": " + str(deltas[author]))
            
    print("\n\n")
  
  
def main():
    #pan12a("../pan12-training/","../pan12-test/")
    training_path = "../pan12-training/"
    test_path = "../pan12-test/"
    
    for words in [40,60,80,100,120,150,0]:
        pan12(problem="A", problem_training="A", 
              n_authors=3, n_training=2, n_testcases=6, 
              considered_words=words, real_words=True,
              training_path=training_path,test_path=test_path)
              
    for words in [40,60,80,100,120,150,0]:
        pan12(problem="B", problem_training="A", 
              n_authors=3, n_training=2, n_testcases=10, 
              considered_words=words, real_words=True,
              training_path=training_path,test_path=test_path)
    
    for words in [40,60,80,100,120,150,0]:          
        pan12(problem="C", problem_training="C", 
              n_authors=8, n_training=2, n_testcases=8, 
              considered_words=words, real_words=True,
              training_path=training_path,test_path=test_path)          
    
    for words in [40,60,80,100,120,150,0]:
        pan12(problem="D", problem_training="C", 
              n_authors=8, n_training=2, n_testcases=17, 
              considered_words=words, real_words=True,
              training_path=training_path,test_path=test_path)
    
    for words in [40,60,80,100,120,150,0]:
        pan12(problem="I", problem_training="I", 
              n_authors=14, n_training=2, n_testcases=14, 
              considered_words=words, real_words=True,
              training_path=training_path,test_path=test_path)          

    for words in [40,60,80,100,120,150,0]:
        pan12(problem="J", problem_training="I", 
              n_authors=14, n_training=2, n_testcases=16, 
              considered_words=words, real_words=True,
              training_path=training_path,test_path=test_path)      

if __name__ == "__main__":
    # execute only if run as a script
    # use level=logging.DEBUG or loggin.INFO for more output!
    logging.basicConfig(level=logging.WARNING,format='%(asctime)s %(levelname)s: %(message)s')
    main()
    
