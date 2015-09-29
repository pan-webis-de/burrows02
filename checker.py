import os
import json
import sys

def main():
    corpusdir = sys.argv[1]
    truthfile = open(os.path.join(corpusdir, "ground-truth.json"))
    truthjson = json.load(truthfile)
    
    outfile = open(os.path.join(corpusdir, "out.json"))
    outjson = json.load(outfile)
    
    ground_truth = {truth["unknown-text"]:truth["true-author"] for truth in truthjson["ground-truth"]}

    #print([answer for answer in outjson["answers"]])
    count = 0
    correct = 0
    for answer in outjson["answers"]:
        count += 1
        if answer["author"] == ground_truth[answer["unknown_text"]]:
            correct += 1
    
    print("Total answers: " + str(count))
    print("Correct answers: " + str(correct))
    print("Accuracy: " + str(correct/count * 100))
            
    
if __name__ == "__main__":
    # execute only if run as a script
    main()
