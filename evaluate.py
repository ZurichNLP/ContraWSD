#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Rico Sennrich, Annette Rios

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

# usage: python evaluate.py errors.json < scores
# by default, lower scores (closer to zero for log-prob) are better

#For frequency statistics, we define several frequency bins

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
        

def count_errors(reference, scores, maximize, verbose):
    """read in scores file and count number of correct decisions"""

    reference = json.load(reference)

    results = {'by_category': defaultdict(lambda: defaultdict(int)),
	       'by_frequency': defaultdict(lambda: defaultdict(int)),
	       'category_by_freq': defaultdict(lambda: defaultdict(string))
	       }

    if maximize:
        better = gt
    else:
        better = lt

    for sentence in reference:
        score = float(scores.readline())
        all_better = True
        #category = sentence['ambig word'] + ":" + sentence['original translation']
        category = sentence['ambig word'] + ":" + sentence['sense']
        results['by_category'][category]['total'] += 1
        frequencyratio = sentence.get('frequency of sense/ambig word in wmt16', None) ## de-en
        if frequencyratio is None:
	    frequencyratio = sentence.get('frequency of sense/ambig word in europarl-v7 and nc11', None) ## de-fr
	absfrequency, total = frequencyratio.split("/")
	relfrequency = int(absfrequency)/int(total)
	#print("freq ratio is {}, absfreq {}, relfreq {}".format(frequencyratio, absfrequency, relfrequency))
	frequency = int(absfrequency)
	results['by_category'][category]['absfreq'] = frequency
	results['by_category'][category]['totalfreq'] = int(total)
        if frequency in FREQUENCY_TO_BIN:
             frequency = FREQUENCY_TO_BIN[frequency]
        elif frequency is not None:
             frequency = DEFAULT_FREQUENCY
        if frequency is not None:
           results['by_frequency'][frequency]['total'] += 1
           results['category_by_freq'][category] = frequency;
       
        for error in sentence['errors']:
            errorscore = float(scores.readline())
            if not better(score, errorscore):
                all_better = False
                #if verbose and category in ["Ton:sound|tone|chime|audio"]:
		  #print("\nwrong:")
		  #print('origin: {0}'.format(sentence["origin"]))
		  #print('original: {0}'.format(sentence["original translation"]))
		  #print('source: {0}'.format(sentence["source"]))
		  #print('reference: {0}'.format(sentence["reference"]))
		  #print('contrastive: {0}'.format(error["contrastive"]))
	      

        if all_better:
            results['by_category'][category]['correct'] += 1
            if frequency is not None:
                results['by_frequency'][frequency]['correct'] += 1
            #if verbose:    
	       #print('\ncorrect:')
	       #print('ambig. word: {0}'.format(sentence["ambig word"]))
	       #print('original translation: {0}'.format(sentence["original translation"]))
	       #print('original: {0}'.format(sentence["original translation"]))
	       #print('source: {0}'.format(sentence["source"]))
	       #print('reference: {0}'.format(sentence["reference"]))
	elif verbose:
	       print('\nwrong:')
	       print('ambig. word: {0}'.format(sentence["ambig word"]))
	       print('original translation: {0}'.format(sentence["original translation"]))
	       print('source: {0}'.format(sentence["source"]))
	       print('reference: {0}'.format(sentence["reference"]))

    return results 

def get_scores(category):
    correct = category['correct']
    total = category['total']
    if total:
        accuracy = correct/total
    else:
        accuracy = 0
    return correct, total, accuracy


def print_statistics(results):

    correct = sum([results['by_category'][category]['correct'] for category in results['by_category']])
    total = sum([results['by_category'][category]['total'] for category in results['by_category']])
    print('{0} : {1} {2} {3}'.format('total', correct, total, correct/total))


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
    
def print_statistics_by_category_csv(results):
    print('category,absfrequency,relfrequency,accuracy')
    for category in sorted(results['by_category']):
        correct, total, accuracy = get_scores(results['by_category'][category])
        freqbinclass = results['category_by_freq'][category]
	if total:
	    absfreq = results['by_category'][category]['absfreq']
	    totalfreq = results['by_category'][category]['totalfreq']
	    relfreq = absfreq/totalfreq
	    print('{0},{1},{2},{3}'.format(category, absfreq, relfreq, accuracy)) 

def main(reference, scores, maximize, verbose ):

    results = count_errors(reference, scores, maximize, verbose)

    print_statistics(results)
    print()
    print('statistics by error category')
    print_statistics_by_category(results)
    print()
    print('statistics by frequency in training data')
    print_statistics_by_frequency(results)
    print()  
    print('csv:')
    print_statistics_by_category_csv(results)
   

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument( '--verbose', '-v', action="store_true", help="verbose mode (prints out all wrong classifications)")
    parser.add_argument('--maximize', action="store_true", help="Use for model where higher means better (probability; log-likelhood). By default, script assumes lower is better (negative log-likelihood).")
    parser.add_argument('--reference', '-r', type=argparse.FileType('r'),
                        required=True, metavar='PATH',
                        help="Reference JSON file")
    parser.add_argument('--scores', '-s', type=argparse.FileType('r'),
                        default=sys.stdin, metavar='PATH',
                        help="File with scores (one per line)")

    args = parser.parse_args()

    main(args.reference, args.scores, args.maximize, args.verbose)
