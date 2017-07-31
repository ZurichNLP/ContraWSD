# ContraWSD
Word sense disambiguation test sets for NMT, for the language pairs German-English and German-French.

The test sets contain sentence pairs with ambiguous German words, each sentence pair has a reference translation and a set of _contrastive_ translations. 
In all _contrastive_ sentences, the original translation of the ambiguous word has been replaced with one of its other meanings.

The idea is to score all given translations for the source sentence, and if the NMT model assigns a higher probability to the reference translation than to all _contrastive_ translations, this counts as a correct decision. 
The script evaluate.py will print out statistics about the accuracy of a given model on this task, more specifically:
 - total accuracy
 - accuracy per word sense
 - accuracy per frequency class 
 - csv with accuracy, absolute and relative frequencies
 
 The frequencies given in the test sets are based on wmt data for German-English:
 - commoncrawl.de-en
 - europarl-v7.de-en
 - news-commentary-v11.de-en
 
 The frequencies in the German-French test sets are based on:
 - europarl-v7.de-fr
 - news-commentary-v11.de-fr

A snapshot of the corpora used in the test set (with document boundaries) can be found at:

http://data.statmt.org/ContraWSD

score.sh is an example of how to use the scripts in this repository with the test set.

If you use this test set, please cite:

Annette Rios, Laura Mascarell and Rico Sennrich. 2017. Improving Word Sense Disambiguation in Neural Machine Translation with Sense Embeddings. In _Proceedings of the Second Conference on Machine Translation (WMT17)_, Copenhagen, Denmark (to appear).
