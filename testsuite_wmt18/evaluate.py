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

            
testwords = {
 'Absatz': ['heel' , 'paragraph' , 'sales' ],
 'Abzug': ['discount|subtraction|deduction' , 'disengagement|decampment|departure|withdrawal' , 'trigger' ],
 'Anlage|Anlagen': ['attachment|attachments|annex|annexes' , 'installation|unit|construction|facility|installations|units|constructions|facilities|plant' , 'investment|investments' ],
 'Annahme': ['adoption|approval|acceptance|acceptation|acception' , 'assumption|hypothesis|guess|conjecture|presumption' ],
 'Art': ['manner|mode|kind|style' , 'species|breed' ],
 'Aufgabe': ['abandonment|surrender' , 'task|assignment|commission|exercise' ],
 'Auflösung': ['dissolution|termination|liquidation|solution|cancellation|cancelation|disintegration|disbandment|breakup|break-up|dispersal|dismantling' , 'resolution' ],
 'Aufnahme': ['picture|photo' , 'reception|absorption|assimilation|intake|admission|inclusion' , 'record|recording' , 'start|beginning' ],
 'Decke|Decken': ['blanket|cover|quilt|blankets|covers|quilts' , 'ceiling|ceilings' ],
 'Eingang': ['entrance|entry|inlet|entranceway|entryway' , 'input|ingress' , 'receipt' ],
 'Einsatz|Einsätze': ['bet|bets' , 'commitment|commitments|engagement|engagements|effort|efforts' , 'use|usage|uses|usages|application|applications|deployment|deployments|operation|operations' ],
 'Fall': ['case|affair|event|instance|occurrence' , 'fall|plunge' ],
 'Gericht|Gerichte': ['court|tribunal|courts|tribunals|trial|trials' , 'dish|dishes|meal|meals' ],
 'Gesellschaft': ['company|association|corporation' , 'society|party|companionship' ],
 'Grund': ['bottom|base' , 'cause|reason' ],
 'Himmel': ['heaven|heavens' , 'sky|skies' ],
 'Karte|Karten': ['card|cards' , 'map|maps' , 'menu|menus' , 'ticket|tickets' ],
 'Kurs': ['course|class|line' , 'price|rate' ],
 'Lager': ['camp|camps' , 'storage|stock|store|storages|stocks|stores' ],
 'Mittel': ['instrument|tool|device|remedy|instruments|tools|devices|remedies' , 'median|medium|middle' , 'resources|funds' ],
 'Muster': ['pattern|patterns' , 'sample|example|prototype|samples|examples|prototypes' ],
 'Opfer': ['sacrifice|sacrifices|offering|offerings' , 'victim|victims|casualty|casualties' ],
 'Platz': ['place|slot|plaza' , 'seat' , 'space|room' ],
 'Preis|Preise': ['cost|costs|price|charge|fee|rate|prices|charges|fees|rates' , 'prize|award|reward|prizes|awards|rewards' ],
 'Rat': ['advice|counsel|tip' , 'council|board' ],
 'Raum': ['region|area' , 'room|space' ],
 'Schlange|Schlangen': ['line|queue|lines|queues' , 'serpent|snake|serpents|snakes' ],
 'Ton': ['clay' , 'sound|tone|chime|audio' ],
 'Tor|Tore': ['door|portal|gate|doors|portals|gates' , 'goal|goals'],
 'Wahl': ['choice|selection' , 'election']
}

enhanced_patterns = {
  #Absatz  
  'heel' :  'heels?',
  'paragraph' : 'paragraphs?|sections?|subsections?',
  'sales' : 'sale|sales|sold|sells?|distribution|marketing|turnovers?',
  #Anlage
  'attachment|attachments|annex|annexes' : 'attachments?|annex|annexes|annexed|appendix|appendices',
  'investment|investments' : 'investments?|assets?',
  'installation|unit|construction|facility|installations|units|constructions|facilities|plant' : 'installations?|units?|constructions?|facility|facilities|plants?|equipment|systems?',
  #Annahme
  'adoption|approval|acceptance|acceptation|acception' : 'adoption|adopting|adopted|approval|adopts?|approving|approved|approves?|acceptance|accepting|acceptation|acception|accepted|accepts?',
  'assumption|hypothesis|guess|conjecture|presumption' : 'assumption|hypothesis|guess|conjecture|presumption|assuming|assumed|assumes?|expects?|expectation',
  #Aufgabe    
  'abandonment|surrender' : 'abandonment|surrenders?|abandons?|abandoned|surrendered' , 
  'task|assignment|commission|exercise'  : 'tasks?|assignments?|commission|exercises?|roles?|jobs?|missions?|responsibility|responsibilities|commitments?|tasked',
  #Auflösung
  'dissolution|termination|liquidation|solution|cancellation|cancelation|disintegration|disbandment|breakup|break-up|dispersal|dismantling' : 'dissolution|dissolves?|dissolved|dissolving|termination|terminates?|liquidation|solution|cancellation|cancelation|cancels?|canceled|disintegration|disintegrates?|disintegrated|disintegrating|disbandment|disbands?|disbanded|disbanding|breakup|break-up|break up|dispersal|disperses?|dispersed|dispersing|unravels?|unraveled|unraveling|closure of|resolves?|disassembly|disassembles?|dismantling|dismantles?',
  'resolution' : 'resolution',
  #Decke
  'blanket|cover|quilt|blankets|covers|quilts' : 'blankets?|covers?|quilts?',
  'ceiling|ceilings' : 'ceilings?',
  #Einsatz
  'bet|bets' : 'bets?|stakes?|wagers?', 
  'commitment|commitments|engagement|engagements|effort|efforts' : 'commitments?|commits?|committed|engagement|engaged|dedication|dedicated|efforts?|involvement|hard work|efforts?', 
  'use|usage|uses|usages|application|applications|deployment|deployments|operation|operations' : 'uses?|usages?|used|using|applications?|deployments?|deploys?|deployed|operations?',
  #Gericht
  'court|tribunal|courts|tribunals|trial|trials' : 'courts?|tribunals?|trials?|process', 
  'dish|dishes|meal|meals' : 'dish|dishes|meals?|food|menus?',
  #Himmel
  'heaven|heavens' : 'heavens?', 
  'sky|skies' : 'sky|skies|out of the blue',
  #Karte|Karten
  'card|cards' : 'cards?', 
  'map|maps' : 'maps?' , 
  'menu|menus' : 'menus?' , 
  'ticket|tickets' : 'tickets?',
  #Kurs
  'course|class|line' : 'course|class|track|line|path|agenda|road|policy|trajectory|line|lines' ,
  'price|rate' : 'prices?|rates?|values?',
  #Lager
  'camp|camps' : 'camps?' ,
  'storage|stock|store|storages|stocks|stores' : 'storages?|stocks?|stores?|warehouses?|warehousing|repository|repositories|inventory|inventories',
  #Opfer
  'sacrifice|sacrifices|offering|offerings' : 'sacrifices?|offerings?', 
  'victim|victims|casualty|casualties' : 'victims?|casualty|casualties' ,
  #Preis|Preise
  'cost|costs|price|charge|fee|rate|prices|charges|fees|rates' : 'costs?|prices?|charges?|fees?|rates?|pricing' ,
  'prize|award|reward|prizes|awards|rewards' : 'prizes?|awards?|rewards?',
  #Rat
  'advice|counsel|tip' : 'advice|counsel|tips?', 
  'council|board' : 'councils?|boards?',
  #Raum
  'region|area' : 'regions?|areas?|countryside|countries|world' , 
  'room|space' : 'rooms?|spaces?',
  #Schlange|Schlangen
  'line|queue|lines|queues' : 'lines?|queues?|queued|queue?ing', 
  'serpent|snake|serpents|snakes' : 'serpents?|snakes?',
  #Ton
  'clay' : 'clay', 
  'sound|tone|chime|audio' : 'sounds?|tones?|chimes?|audio',
  #Tor|Tore
  'door|portal|gate|doors|portals|gates' : 'doors?|portals?|gates?|gateways?|open(s|ing)? the way|floodgates?', # Tür und Tor öffnen
  'goal|goals' : 'goal|goals',
  #Wahl, choose covers both?
  'choice|selection' : 'choices?|selections?|chooses?|chosen|choosing|selects?|selected',
  'election' : 'elections?|polling|polls?|elected|elects?'
}

def count_errors(reference, translations, verbose=False, ignore_wmt=False,  year=18):
    """read in translations file and count number of correct decisions"""

    reference = json.load(reference)

    results = {'by_category': defaultdict(lambda: defaultdict(int)),
	       'by_frequency': defaultdict(lambda: defaultdict(int)),
	       'category_by_freq': defaultdict(lambda: defaultdict(string))
	       }
    ## keep sentence pairs that need manual evaluation in separate dictionary
    manual_evaluation_required = []
    unfound =0
    foundBoth=0
    foundother=0
    wmt_origins = re.compile(r'^dev|^newstest|^news-test|^nc-dev')
    
    for sentence in reference:
        found = False
        foundOtherSense = False
        translation = translations.readline()
        
        UNFOUND=False
        FOUND_only_correct=False
        # if FOUND_only_correct, keep track of how many correct ones were found vs. how many occur in source
        FOUND_only_correct_nbr_in_trans=1
        FOUND_only_other=False
        FOUND_both_senses=False
        category = sentence['ambig word'] + ":" + sentence['sense']
        origin = sentence['origin']
        if ignore_wmt and wmt_origins.search(origin):
            #print("{} wmt pair, ignoring for evaluation".format(origin))
            continue;

        sntnbr = sentence['sentence number']
        ## take number of occurrence in source as value here instead of just counting sentences 
        occurrence = sentence['occurrence in source']  
        results['by_category'][category]['total'] += occurrence
        
        frequencyratio = sentence.get('frequency of sense/ambig word in wmt18', None) ## de-en
        if(year == 17):
            frequencyratio = sentence.get('frequency of sense/ambig word in wmt17', None) ## de-en
        elif(year == 16):
            frequencyratio = sentence.get('frequency of sense/ambig word in wmt16', None) ## de-en
        absfrequency, total = frequencyratio.split("/")
        relfrequency = int(absfrequency)/int(total)
        
        frequency = int(absfrequency)
        results['by_category'][category]['absfreq'] = frequency
        results['by_category'][category]['totalfreq'] = int(total)
        #frequency = relfrequency
        if frequency in FREQUENCY_TO_BIN:
             frequency = FREQUENCY_TO_BIN[frequency]
        elif frequency is not None:
             frequency = DEFAULT_FREQUENCY
        if frequency is not None:
           results['by_frequency'][frequency]['total'] += occurrence
           results['category_by_freq'][category] = frequency;

	
        sense = sentence['sense']
        sensepattern = enhanced_patterns[sense]
        p = re.compile(r'\b({})\b'.format(sensepattern), re.IGNORECASE)
        matches = p.findall(translation)
        #if(sense == "investment|investments"):
            #print("sensepattern {}, translation {}".format(sensepattern, translation))
            #print("found {}".format(len(matches)))
        
        senselist = testwords[sentence['ambig word']]
        othertranslations = [othersense for othersense in senselist if not othersense == sense]
        otherpattern =""
        for othertrs in othertranslations:
            pattern = enhanced_patterns[othertrs]
            if otherpattern == "":
                otherpattern = pattern
            else:
                otherpattern += "|" + pattern
        p2 = re.compile(r'\b({})\b'.format(otherpattern), re.IGNORECASE)
        matches2 = p2.findall(translation)
        
        if (len(matches)>0 and len(matches2)>0):
            foundBoth += occurrence
            FOUND_both_senses=True
            json_ex = OrderedDict ([
                        ('category' , category),
                        ('frequency' , frequency),
                        ('origin' , origin) ,
                        ('source' , sentence['source']),
                        ('reference' , sentence['reference']),
                        ('translation' , translation),
                        ('looking for sense', sensepattern),
                        ('looking for other senses' , otherpattern),
                        ('found both' , True),
                        ('occurrence in source' , occurrence),
                        ('found list 1', matches),
                        ('found list 2' , matches2),
                        ('correct' , " ") ])
            manual_evaluation_required.append(json_ex)
            if verbose:
                print('word: {0}'.format(sentence['ambig word']))
                print('source: {0}'.format(sentence['source']))
                print('looking for sense: {0}'.format(sensepattern))
                print('looking for other senses: {0}'.format(otherpattern))
                print('found both lists: {0} and {1}'.format(matches, matches2))
                print('translation: {0}'.format(translation))
        
        elif len(matches)>0:
            FOUND_only_correct = True
            if occurrence >= len(matches):
                FOUND_only_correct_nbr_in_trans = len(matches)
        elif len(matches2)>0:
            FOUND_only_other = True    
        else:
            unfound += occurrence
            UNFOUND=True
            json_ex = OrderedDict ([
                        ('category' , category),
                        ('frequency' , frequency),
                        ('origin' , origin),
                        ('source' , sentence['source']),
                        ('reference' , sentence['reference']),
                        ('translation' , translation),
                        ('looking for sense', sensepattern),
                        ('looking for other senses' , otherpattern),
                        ('found none' , True),
                        ('occurrence in source' , occurrence),
                        ('correct' , " ") ])
            manual_evaluation_required.append(json_ex)
            if verbose:
                print('word: {0}'.format(sentence['ambig word']))
                print('source: {0}'.format(sentence['source']))
                print('looking for sense: {0}'.format(sensepattern))
                print('found list: {0}'.format(matches))
                print('looking for other senses: {0}'.format(otherpattern))
                print('found list: {0}'.format(matches2))
                print('translation: {0}'.format(translation))
                    
        
        if FOUND_only_correct:
            results['by_category'][category]['only_correct'] += FOUND_only_correct_nbr_in_trans
            results['by_category'][category]['unfound_in_correct'] += (occurrence-FOUND_only_correct_nbr_in_trans)
            unfound += occurrence-FOUND_only_correct_nbr_in_trans
            if frequency is not None:
                results['by_frequency'][frequency]['only_correct'] += FOUND_only_correct_nbr_in_trans
                results['by_frequency'][frequency]['unfound_in_correct'] +=  (occurrence-FOUND_only_correct_nbr_in_trans)
                
        elif FOUND_both_senses:        
            results['by_category'][category]['found_both'] += occurrence
            if frequency is not None:
                results['by_frequency'][frequency]['found_both'] += occurrence
                
        elif FOUND_only_other:
            results['by_category'][category]['only_other'] += occurrence
            if frequency is not None:
                results['by_frequency'][frequency]['only_other'] += occurrence
                
        elif UNFOUND:
            results['by_category'][category]['unfound'] += occurrence
            if frequency is not None:
                results['by_frequency'][frequency]['unfound'] += occurrence        
            
    print('nothing found in {0} cases'.format(unfound))
    print('both senses found in {0} cases'.format(foundBoth))
    return results, manual_evaluation_required

def get_scores(category):
    correct = category['correct']
    total = category['total']
    if total:
        accuracy = correct/total
    else:
        accuracy = 0
    return correct, total, accuracy

def get_scores_match_all(category):
    only_correct = category['only_correct']
    found_both = category['found_both']
    total = category['total']
    if total:
        accuracycorrect = only_correct/total
        accuracyboth = found_both/total
    else:
        accuracycorrect = 0
        accuracyboth = 0
    return only_correct, found_both, total, accuracycorrect, accuracyboth

def get_scores_other(category):
    other = category['other']
    total = category['total']
    if total:
        accuracy = other/total
    else:
        accuracy = 0
    return other, total, accuracy

def get_scores_other_match_all(category):
    other = category['only_other']
    total = category['total']
    if total:
        accuracy = other/total
    else:
        accuracy = 0
    return other, total, accuracy

def print_json_for_manual_evaluation(manual_evaluation_required,name):
    with open(name, 'w') as fp:
        json.dump(manual_evaluation_required, fp, indent=4, ensure_ascii=False) 
        
def print_automatic_results(results, name):  
    with open(name, 'w') as fp:
        json.dump(results, fp, indent=4, sort_keys=True, ensure_ascii=False)   
       

def print_statistics(results):

    correct = sum([results['by_category'][category]['correct'] for category in results['by_category']])
    total = sum([results['by_category'][category]['total'] for category in results['by_category']])
    print('{0} : {1} {2} {3}'.format('total', correct, total, correct/total))
    
def print_statistics_match_all(results):
    
    only_correct = sum([results['by_category'][category]['only_correct'] for category in results['by_category']])
    found_both = sum([results['by_category'][category]['found_both'] for category in results['by_category']])
    total = sum([results['by_category'][category]['total'] for category in results['by_category']])
    print('{0} : {1} {2} {3} only correct: {4}, found both: {5}'.format('total', only_correct, found_both , total, only_correct/total, found_both/total))    
    
def print_statistics_othertranslations(results):

    other = sum([results['by_category'][category]['other'] for category in results['by_category']])
    total = sum([results['by_category'][category]['total'] for category in results['by_category']])
    print('{0} : {1} {2} {3}'.format('total', other, total, other/total))
    
def print_statistics_othertranslations_match_all(results):

    other = sum([results['by_category'][category]['only_other'] for category in results['by_category']])
    total = sum([results['by_category'][category]['total'] for category in results['by_category']])
    print('{0} : {1} {2} {3}'.format('total', other, total, other/total))    

def print_statistics_by_category(results):

    for category in sorted(results['by_category']):
        correct, total, accuracy = get_scores_match_all(results['by_category'][category])
	if total:
            print('{0} : {1} {2} {3}'.format(category, correct, total, accuracy))
            
def print_statistics_by_category_match_all(results):

    for category in sorted(results['by_category']):
        only_correct, found_both, total, accuracycorrect, accuracyboth = get_scores_match_all(results['by_category'][category])
	if total:
            print('{0} : {1} {2} {3} | {4} + {5} '.format(category, only_correct, found_both, total, accuracycorrect, accuracyboth))            

def print_statistics_by_frequency(results):

    for frequency in FREQUENCY_BINS:
        correct, total, accuracy = get_scores_match_all(results['by_frequency'][frequency])
        if total:
	    print('{0} : {1} {2} {3} '.format(frequency, correct, total, accuracy))

def print_statistics_by_frequency_match_all(results):
    print('frequency, only_correct, found_both, total | accuracycorrect + accuracyboth')
    for frequency in FREQUENCY_BINS:
        only_correct, found_both, total, accuracycorrect, accuracyboth = get_scores_match_all(results['by_frequency'][frequency])
        if total:
            print('{0} : {1} {2} {3} | {4} + {5} '.format(frequency, only_correct, found_both, total, accuracycorrect, accuracyboth)) 


def print_statistics_by_frequency_other(results):

    for frequency in FREQUENCY_BINS:
        other, total, accuracy = get_scores_other(results['by_frequency'][frequency])
        if total:
            print('{0} : {1} {2} {3} '.format(frequency, other, total, accuracy))    
	    

def print_statistics_by_frequency_other_match_all(results):

    for frequency in FREQUENCY_BINS:
        other, total, accuracy = get_scores_other_match_all(results['by_frequency'][frequency])
        if total:
            print('{0} : {1} {2} {3} '.format(frequency, other, total, accuracy))  	    


def print_statistics_by_category_csv(results):
    print('category,absfrequency,relfrequency,accuracy')
    for category in sorted(results['by_category']):
        correct, total, accuracy = get_scores(results['by_category'][category])
        freqbinclass = results['category_by_freq'][category]
        #print(freqbinclass)
	if total:   
	    absfreq = results['by_category'][category]['absfreq']
	    totalfreq = results['by_category'][category]['totalfreq']
	    relfreq = absfreq/totalfreq
	    print('{0},{1},{2},{3}'.format(category, absfreq, relfreq, accuracy)) 


def main(reference, translations, verbose, outname_automatic_results, outname_manual_evaluation, ignore_wmt, year):

    results, manual_evaluation_required = count_errors(reference, translations,  verbose, ignore_wmt, year)

    print_statistics_match_all(results)
    print()
    print('statistics by error category')
    print_statistics_by_category_match_all(results)
    print()
    print('statistics by frequency in training data')
    print_statistics_by_frequency_match_all(results)
    print()  
    print('print_statistics_othertranslations')
    print_statistics_othertranslations_match_all(results)
    print()  
    print_statistics_by_frequency_other_match_all(results)
    print()
    print_automatic_results(results,outname_automatic_results)
    print_json_for_manual_evaluation(manual_evaluation_required, outname_manual_evaluation)
   

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action="store_true", help="verbose mode (prints out all wrong classifications)")
    parser.add_argument('--reference', '-r', type=argparse.FileType('r'),
                        required=True, metavar='PATH',
                        help="Reference JSON file")
    parser.add_argument('--translations', '-t', type=argparse.FileType('r'),
                        default=sys.stdin, metavar='PATH',
                        help="File with translations (one per line)")
    parser.add_argument('--outname-automatic-results', type=str, metavar='PATH',
                        help="json to print results of automatic evaluation")
    parser.add_argument('--outname-manual-evaluation', type=str, metavar='PATH',
                        help="json to print sentence pairs that need manual evaluation")
    parser.add_argument('--ignore-wmt', action="store_true", help="ignore all sentence pairs from wmt dev and test sets for the evaluation")
    parser.add_argument('--year', type=int, required=False,
                        help="year to get training data frequencies")

    args = parser.parse_args()

    #load_outputs(args.outputs)
    #enc = sys.getdefaultencoding()
    #print('enc:', enc)
    main(args.reference, args.translations, args.verbose, args.outname_automatic_results, args.outname_manual_evaluation, args.ignore_wmt, args.year)
