# Baselines

This directory contains scores on ContraWSD for various systems, which can be used as baselines in future work.

WMT16
-----

These models are described in:
Rico Sennrich, Barry Haddow and Alexandra Birch (2016). Edinburgh Neural Machine Translation Systems for WMT 16. In: Proceedings of the First Conference on Machine Translation, Volume 2: Shared Task Papers, Berlin, Germany.

- scores.uedin-wmt16-parallel-single

    This corresponds to the baseline system in Sennrich, Haddow Birch (2016), trained on all parallel training data available.

- scores.uedin-wmt16-single

    This corresponds to the best single system in Sennrich, Haddow Birch (2016). In contrast to the baseline, back-translated monolingual data is included in the training data. The model is available at http://data.statmt.org/wmt16_systems/en-de/model-ens1.npz

- scores.uedin-wmt16-full

    The official uedin-nmt submission to the WMT16 shared news translation task. It is an ensemble of 4 independently trained left-to-right models, reranked with 4 (target-side) right-to-left models.
    We add the scores of all left-to-right models in the ensemble ( http://data.statmt.org/wmt16_systems/en-de/model-ens{1,2,3,4}.npz ), and the scores of all right-to-left models (reversing the target side of the corpus): http://data.statmt.org/rsennrich/wmt16_systems/de-en/r2l/model-ens{1,2,3,4}.npz

WMT17
-----

These models are described in:
Rico Sennrich, Alexandra Birch, Anna Currey, Ulrich Germann, Barry Haddow, Kenneth Heafield, Antonio Valerio Miceli Barone, and Philip Williams (2017). The University of Edinburgh’s Neural MT Systems for WMT17. In: Proceedings of the Second Conference on Machine Translation, Volume 2: Shared Task Papers. Copenhagen, Denmark.

- scores.uedin-wmt17-single

    This model corresponds to the best single system in Sennrich et al. (2017). Differences to last year's system include (slightly) more training data, differences in preprocessing, and better model architecture (with deep transition networks and layer normalization). This model is available at http://data.statmt.org/wmt17_systems/en-de/model.l2r.ens1.npz

- scores.uedin-wmt17-full

    The official uedin-nmt submission to the WMT17 shared news translation task. It is an ensemble of 4 independently trained left-to-right models, reranked with 4 (target-side) right-to-left models.
    We add the scores of all left-to-right models in the ensemble ( http://data.statmt.org/wmt17_systems/en-de/model.l2r.ens{1,2,3,4}.npz ), and the scores of all right-to-left models (reversing the target side of the corpus): http://data.statmt.org/wmt17_systems/en-de/model.r2l.ens{1,2,3,4}.npz


Results DE-EN
-------------

| system                      | Accuracy on ContraWSD (in %)| BLEU on newstest2016 |
|---                          |---                          |---                   |
| uedin-wmt16-parallel-single | 81.17                       | 28.5                 |
| uedin-wmt16-single          | 83.54                       | 36.2                 |
| uedin-wmt16-full            | 84.14                       | 38.6                 |
| uedin-wmt17-single          | 86.72                       | 39.6                 |
| uedin-wmt17-full            | 87.91                       | 41.0                 |
