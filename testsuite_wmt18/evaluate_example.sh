#!/bin/bash

task_dir=path-to-wsd-task
translations_dir=path-to-translations
manual_dir=path-to-manual-evaluation
automatic_dir=path-to-automatic-evaluation
final_dir=path-to-final-evaluation
moses=path-to-mosesdecoder
json=$task_dir/de-en.wsd.task.json

for system in $translations_dir/*
  do
     name=$(basename $system)
     echo "evaluating $name"
     
        # entire test set
        python evaluate.py --reference $json --translations $system --outname-automatic-results $automatic_dir/${name}.automatic.json --outname-manual-evaluation $manual_dir/${name}.manual.json  > $automatic_dir/${name}.out.automatic 
   
        # ignoring wmt sentence pairs for evaluation
        
        python evaluate.py --reference $json --translations $system --outname-automatic-results $automatic_dir/${name}.automatic.nowmt.json --outname-manual-evaluation $manual_dir/${name}.manual.nowmt.json --ignore-wmt > $automatic_dir/${name}.out.automatic.nowmt 
        
        # manually correct *.manual.json 
        # fill in number of correctly translated words in "correct"
        # NOTE: "correct" : " " == no translation found vs. "correct": "0" == wrong translation found
        # combine automatic and manual evaluation 
        python final_eval.py --automatic-eval $automatic_dir/${name}.automatic.json --manual-eval $manual_dir/${name}.manual.json > $final_dir/${name}.out
        python final_eval.py --automatic-eval $automatic_dir/${name}.automatic.nowmt.json --manual-eval $manual_dir/${name}.manual.json --ignore-wmt > $final_dir/${name}.out

 done

# BLEU
# get reference translations from json

ref=$task_dir/de-en.wsd.task.en.detok
## BLEU
for system in $translations_dir/*
 do
    name=$(basename $system)
    echo "bleu for $name"
    perl $moses/scripts/generic/multi-bleu-detok.perl $ref  < $system
 done
