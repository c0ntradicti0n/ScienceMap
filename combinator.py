from math import log
import scipy
from xnym_embeddings.xnym_embeddings import wordnet_lookup_xnyms, get_hyponyms, get_antonyms, get_cohypernyms, \
    get_cohyponyms, get_hypernyms, get_synonyms, search_sequence_numpy
import similaritymixer
import wmd_simmilarity_mixer
import neo4j_handler
from helpers.color_logger import *
import pprint
import wmd_simmilarity_mixer
from timeit import default_timer as timer

#analog = similaritymixer.SimilarityMixer(  #

#subordinated = similaritymixer.SimilarityMixer(  #
#    similarity_composition=[(1,similaritymixer.SimilarityMixer.multi_kind_tup_sim(wmd_simmilarity_mixer.wmd_similarity, assign={"SUBJECT":"CONTRAST"}),  0.0006, 1)], verbose=True)
#subordinated = similaritymixer.SimilarityMixer(  #
#    similarity_composition=[(1,similaritymixer.SimilarityMixer.multi_kind_tup_sim(wmd_simmilarity_mixer.biopython_diff_encircle, assign={"SUBJECT":"CONTRAST"}),  0.0006, 1)], verbose=True)
from littletools.nested_list_tools import flatten, flatten_list

subordinated = similaritymixer.SimilarityMixer(  #
    similarity_composition=[(1,similaritymixer.SimilarityMixer.multi_kind_tup_sim(wmd_simmilarity_mixer.sub_suffixtree, assign={"SUBJECT":"CONTRAST"}),  0.0006, 1)], verbose=True)

moments = similaritymixer.SimilarityMixer(
    similarity_composition=[(1,similaritymixer.SimilarityMixer.multi_kind_tup_sim(wmd_simmilarity_mixer.sub_suffixtree, assign={"SUBJECT":"CONTRAST"}, layout='both'),  0.0006, 1)], verbose=True)

analogs = similaritymixer.SimilarityMixer(
                            [(1,similaritymixer.SimilarityMixer.multi_kind_tup_sim(wmd_simmilarity_mixer.wmd_similarity, n=4), -3,3),
                            (-20,similaritymixer.SimilarityMixer.multi_kind_tup_sim(similaritymixer.SimilarityMixer.same_expression_sim), 0, 1)])

def combine (nlp_annotated_annotations, sim, params):
    time_test_annotations = nlp_annotated_annotations[:20]
    start = timer()
    _ = sim.choose(data=(time_test_annotations, time_test_annotations), **params)
    end = timer()
    time_needed = end - start
    estimated_time = float(time_needed) / scipy.special.comb(20,2) * scipy.special.comb(len(nlp_annotated_annotations), 2) + (float(time_needed) / 20 * len(nlp_annotated_annotations)*10) ** 1.5
    print (len(nlp_annotated_annotations))
    logging.info(f"time elapsed:                  {time_needed}")
    logging.info(f"estimated time for comparison: {estimated_time}s")

    start = timer()
    results = sim.choose(data=(nlp_annotated_annotations, nlp_annotated_annotations), **params)
    end = timer()
    time_needed = end - start
    logging.info(f"time needed for comparison:    {time_needed}s")
    return results
