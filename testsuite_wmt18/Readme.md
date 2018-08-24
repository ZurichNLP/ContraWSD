# Test suite WMT18

Contains the test set used in the WSD evaluation for WMT18, a reduced version of ContraWSD and evaluation scripts to deal with translations instead of scoring.

`evaluate.py` does an automatic evaluation as follows:
1. finds only instances of the correct translations -- counts as correct (If there are multiple instances of the ambiguous source word in the sentence, the script counts the number of correct translations to assign credit)
2. finds only instances of the other translations -- counts as wrong
3. finds both the correct and one of the other translations -- manual inspection (print to json file given with `--outname-manual-evaluation`)
3. finds none of the known translations -- manual inspection (print to json file given with `--outname-manual-evaluation`)

It will print the results to STDOUT and to a given location (`--outname-automatic-results`) in json format, it will also print a json file for manual inspection with the unclear cases (`--outname-manual-evaluation`).

`final_eval.py` will read the two output json files of from `evaluate.py` and add the results of the manual annotation to the automatic results. The expected annotation is as follows:

- correct: ">1" -- number of correct translations, can be >1 if source contained more than one instance of the ambiguous words. Note that this value cannot be greater than the value of `occurrence in source` of the sentence pair.
- correct: "0"  -- ambiguous word is translated with one of its other meanings
- correct: " "  -- ambiguous word has not been translated (whitespace in quotes)
- in the (rare) case that the script finds both translations and "occurrence in source" > 2 and correct is smaller than this number, the script will per default assume that the difference of "occurrence in source" - "correct" is wrong (to be treated as "0"), if one or more are not translated, add "unfound": number of untranslated instances

`evaluate_example.sh` contains a usage example for the scripts.
