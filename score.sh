#!/bin/bash

#######################################################
#    Example script to use test sets for evaluation   #
#######################################################

# path to moses decoder: https://github.com/moses-smt/mosesdecoder
mosesdecoder=path-to-mosesdecoder
truecasemodel_dir=path-to-your-truecase-models

# path to subword segmentation scripts: https://github.com/rsennrich/subword-nmt
subword_nmt=path-to-subword-nmt
bpemodel_dir=path-to-your-bpe-model

# path to nematus: https://www.github.com/rsennrich/nematus
nematus_dir=path-to-nematus
nmt_model_dir=path-to-directory-containing-your-model
nmt_model=path-to-your-model.npz

wsd_dir=path-to-this-repo
eval_dir=evaluation-directory
target=en ## or fr
testset=$wsd_dir/de-$target.final


## prepare NMT_testsets
python $wsd_dir/json_to_plaintext.py $testset $target

#### pre-process test sets as required by your NMT model, e.g.
cat $testset.de | $mosesdecoder/scripts/tokenizer/normalize-punctuation.perl -l de | $mosesdecoder/scripts/tokenizer/tokenizer.perl -l de | $mosesdecoder/scripts/recaser/truecase.perl -model $truecasemodel_dir/truecase-model.de | python $subword_nmt/apply_bpe.py --codes $bpemodel_dir/de$target.bpe > $testset.bpe.de
cat $testset.$target | $mosesdecoder/scripts/tokenizer/normalize-punctuation.perl -l $target | $mosesdecoder/scripts/tokenizer/tokenizer.perl -l $target | $mosesdecoder/scripts/recaser/truecase.perl -model $truecasemodel_dir/truecase-model.$target | python $subword_nmt/apply_bpe.py --codes $nmt_model_dir/de$target.bpe > $testset.bpe.$target

## score test set
(cd $nmt_model_dir && THEANO_FLAGS=floatX=float32,device=cuda0,gpuarray.preallocate=0.8,on_unused_input=warn python $nematus_dir/nematus/score.py -m $nmt_model -s $testset.bpe.de -t $testset.bpe.$target -o $eval_dir/nmt.scores.$target -n -b 20)

cat $eval_dir/nmt.scores.$target | python -c "import sys 
for line in sys.stdin:
   sys.stdout.write(' '.join(reversed(line.split())) + '\n')" | cut -f 1 -d " " >  $eval_dir/nmt.only.scores.$target
  
cat  $eval_dir/nmt.only.scores.$target | python $wsd_dir/evaluate.py -r $testset.json > $eval_dir/nmt.$target.accuracy
