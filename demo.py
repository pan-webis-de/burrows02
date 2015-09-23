import logging
import codecs
import string
import testcases

from delta import Database, Author, Text

def main():
    training_path = "../pan12-training/"
    test_path = "../pan12-test/"
    
    testcases.pan12open(problem="B", problem_training="A",
              n_authors=3, n_training=2, n_testcases=10,
              considered_words_list=[150], real_words=True,
              training_path=training_path,test_path=test_path,
              thresholds=[1.05])

if __name__ == "__main__":
    # execute only if run as a script
    # use level=logging.DEBUG or loggin.INFO for more output!
    logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s: %(message)s')
    main()