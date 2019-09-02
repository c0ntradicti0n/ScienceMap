from math import log

import scipy

import basic_nlp_annotator
import similaritymixer
import wmd_simmilarity_mixer
import neo4j_handler
from helpers.color_logger import *

#analog = similaritymixer.SimilarityMixer(  #
#    similarity_composition=[(1,similaritymixer.SimilarityMixer.multi_kind_tup_sim(wmd_simmilarity_mixer.wmd_similarity, n=4), -3,3),
#                            (-20,similaritymixer.SimilarityMixer.multi_kind_tup_sim(similaritymixer.SimilarityMixer.same_expression_sim), 0, 1)])

#subordinated = similaritymixer.SimilarityMixer(  #
#    similarity_composition=[(1,similaritymixer.SimilarityMixer.multi_kind_tup_sim(wmd_simmilarity_mixer.wmd_similarity, assign={"SUBJECT":"CONTRAST"}),  0.0006, 1)], verbose=True)
#subordinated = similaritymixer.SimilarityMixer(  #
#    similarity_composition=[(1,similaritymixer.SimilarityMixer.multi_kind_tup_sim(wmd_simmilarity_mixer.biopython_diff_encircle, assign={"SUBJECT":"CONTRAST"}),  0.0006, 1)], verbose=True)
subordinated = similaritymixer.SimilarityMixer(  #
    similarity_composition=[(1,similaritymixer.SimilarityMixer.multi_kind_tup_sim(wmd_simmilarity_mixer.sub_suffixtree, assign={"SUBJECT":"CONTRAST"}),  0.0006, 1)], verbose=True)

moments = similaritymixer.SimilarityMixer(
    similarity_composition=[(1,similaritymixer.SimilarityMixer.multi_kind_tup_sim(wmd_simmilarity_mixer.sub_suffixtree, assign={"SUBJECT":"CONTRAST"}, layout='both'),  0.0006, 1)], verbose=True)


def combine (span_sets, sim):
    span_sets = span_sets
    nlp_annotator = basic_nlp_annotator.BasicAnnotator(layout='structured_span')
    nlp_annotated_annotations = [[[nlp_annotator.annotate(span) for span in spans] for spans in span_set] for span_set in span_sets]
    nlp_annotated_annotations = [sp for sp in nlp_annotated_annotations if sp and len(sp)>1]
    params = {
     'layout': '1:1',
     'n': 10
    }
    from timeit import default_timer as timer
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

def combine_wordnet(span_sets):
    subjects = [s for s in span_sets if s['kind'] == 'SUBJECT']
    to_pair = []
    for s in subjects:
        xnyms_of_s = xnym_embedder(s)
        common = set(xnyms) & set(synjects)
        if common:
            to_pair.append([(s, c) for c in common])

    return to_pair
