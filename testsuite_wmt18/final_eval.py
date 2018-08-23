#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals
import sys
reload(sys);
sys.setdefaultencoding("utf8")
import json
import argparse
from collections import defaultdict, OrderedDict
from operator import gt, lt
import scipy
import scipy.stats
import re

FREQUENCY_BINS = OrderedDict()
# value for higher frequencies
FREQUENCY_BINS[">10k"] = []
DEFAULT_FREQUENCY = ">10k"
FREQUENCY_BINS[">5k"] = range(5001, 10001)
FREQUENCY_BINS[">2k"] = range(2001, 5001)
FREQUENCY_BINS[">1k"] = range(1001, 2001)
FREQUENCY_BINS[">500"] = range(501,1001)
FREQUENCY_BINS[">200"] = range(201,501)
FREQUENCY_BINS[">100"] = range(101,201)
FREQUENCY_BINS[">50"] = range(51,101)
FREQUENCY_BINS[">20"] = range(21,51)
FREQUENCY_BINS["0-20"] = range(0,21)


FREQUENCY_TO_BIN = {}
for key in FREQUENCY_BINS:
    for freq in FREQUENCY_BINS[key]:
        FREQUENCY_TO_BIN[freq] = key

def finalize(automatic_eval, manual_eval, verbose=False, ignore_wmt=False):
    results = json.load(automatic_eval)
    manual_results = json.load(manual_eval)

    
    ## correct number of only_correct from automatic evaluation + correct==1 from manual evalutation
    automatic_correct =0
    automatic_other = 0
    automatic_both = 0
    automatic_none = 0
    automatic_unfound_in_correct =0
    
    for category in results['by_category']:
        
        only_correct_found = results['by_category'][category]['only_correct']
        only_other = results['by_category'][category]['only_other']
        found_both = results['by_category'][category]['found_both']
        results['by_category'][category]['correct'] = only_correct_found
        ## set unfound for all categories and frequencies
        if 'unfound' not in results['by_category'][category]:
            results['by_category'][category]['unfound'] =0
        if 'unfound_in_correct' not in results['by_category'][category]:
            results['by_category'][category]['unfound_in_correct'] =0    
            
        unfound = results['by_category'][category]['unfound']
        unfound_in_correct = results['by_category'][category]['unfound_in_correct']
        automatic_correct += only_correct_found
        automatic_other += only_other
        automatic_both += found_both
        automatic_none += unfound
        automatic_unfound_in_correct += unfound_in_correct
        

    for category in results['by_frequency']:
            only_correct_found = results['by_frequency'][category]['only_correct']
            results['by_frequency'][category]['correct'] = only_correct_found   
            ## set unfound for all categories and frequencies
            if 'unfound' not in results['by_frequency'][category]: 
                results['by_frequency'][category]['unfound'] = 0

    wmt_origins = re.compile(r'^dev|^newstest|^news-test|^nc-dev')
    
    manual_only_other =0
    manual_only_correct=0
    manual_found_none=0
    manual_occurrence=0
    
    for sentence_pair in manual_results:
        # check if this is sentence pair from wmt data and ignore_wmt was given
        if ignore_wmt and wmt_origins.search(sentence_pair['origin']):
            continue;
        
        # >1=number of correct, 0=false " "= no translation found/undecided
        correct = sentence_pair['correct']
        frequency = sentence_pair['frequency']
        category = sentence_pair['category']
        occurrence = sentence_pair['occurrence in source']
        manual_occurrence += occurrence
        
            
        correct = sentence_pair['correct']
        if correct == " ":
            # not found
            manual_found_none += occurrence
        else:
            # already included in total, only need to be added to correct
            # make sure that correct <= occurence in reference (we do not want to adapt total number of cases!)
            if int(correct) > occurrence:
                print("number of correct words {} is higher than number of occurrence in source {} in example with source {}".format(correct, sentence_pair['occurrence in source'],  sentence_pair['source']))
                exit(1)
            else:
               if correct == "0":
                   manual_only_other += occurrence
                    
               elif int(correct) <= occurrence:
                    manual_only_correct += int(correct)
                    diff = occurrence - int(correct)
                    results['by_category'][category]['correct'] += int(correct)
                    if 'found none' in sentence_pair:
                        manual_found_none += diff
                    elif 'found both' in sentence_pair: # if there were >2 ambiguous words in source, some might have been translated wrong and others might not be translated at all
                        if 'unfound' in sentence_pair:
                            #print("nbr unfound: {}".format(sentence_pair['unfound']))
                            manual_found_none += int(sentence_pair['unfound'])
                            manual_only_other += diff - int(sentence_pair['unfound'])
                    
                        else:
                            manual_only_other += diff
                    
               
    total_unfound = manual_found_none + automatic_unfound_in_correct
    total_only_correct = automatic_correct + manual_only_correct
    total_other = automatic_other + manual_only_other
  
    return results, total_unfound, total_other 

def get_scores(category):
    correct = category['correct']
    total = category['total']
    if total:
        accuracy = correct/total
    else:
        accuracy = 0
    return correct, total, accuracy

def print_statistics(results, total_unfound, total_other):

    correct = sum([results['by_category'][category]['correct'] for category in results['by_category']])
    total = sum([results['by_category'][category]['total'] for category in results['by_category']])

    print('{0} : {1} {2} {3}'.format('total', correct, total, correct/total))
    print('other translation found : {} {}'.format(total_other, total_other/total))
    print('no translation found : {} {}'.format(total_unfound,total_unfound/total))
    
def print_statistics_by_category(results):

    for category in sorted(results['by_category']):
        correct, total, accuracy = get_scores(results['by_category'][category])
	if total:
            print('{0} : {1} {2} {3}'.format(category, correct, total, accuracy))
            
            
def print_statistics_by_frequency(results):

    for frequency in FREQUENCY_BINS:
        correct, total, accuracy = get_scores(results['by_frequency'][frequency])
        if total:
	    print('{0} : {1} {2} {3} '.format(frequency, correct, total, accuracy))
            

def main(automatic_eval, manual_eval, verbose, ignore_wmt):

    results, total_unfound, total_other = finalize(automatic_eval, manual_eval,  verbose, ignore_wmt)
    
    print_statistics(results, total_unfound, total_other)
    print()
    print('statistics by error category')
    print_statistics_by_category(results)
    print()
    print('statistics by frequency in training data')
    print_statistics_by_frequency(results)
    print() 


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action="store_true", help="verbose mode (prints out all wrong classifications)")
    parser.add_argument('--ignore-wmt', action="store_true", help="ignore all sentence pairs from wmt dev and test sets for the evaluation")
    parser.add_argument('--automatic-eval', '-a', type=argparse.FileType('r'),
                        required=True, metavar='PATH',
                        help="JSON file containing the (preliminary) results of the automatic evaluation")
    parser.add_argument('--manual-eval', '-m', type=argparse.FileType('r'),
                        required=True, metavar='PATH',
                        help="JSON file containing the annotated results of the manual evaluation")

    args = parser.parse_args()

    #load_outputs(args.outputs)
    #enc = sys.getdefaultencoding()
    #print('enc:', enc)
    main(args.automatic_eval, args.manual_eval, args.verbose, args.ignore_wmt)
