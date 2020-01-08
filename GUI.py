import os
os.environ['SPACY_WARNING_IGNORE'] = 'W008'

import glob
import logging
from argparse import ArgumentParser
from pprint import pprint
import bio_annotation
import neo4j_handler
import combinator
from littletools.nested_list_tools import pairwise
import basic_nlp_annotator

logging.getLogger().setLevel(logging.INFO)
annotation_kind_set = {'CONTRAST', 'SUBJECT'}


parser = ArgumentParser(description='Mixing the corpus to train/test/valid conll3s.')
parser.add_argument('dir',
                    nargs='?',
                    type=str,
                    help='directory to process conll3s together',
                    default="./test")
args = parser.parse_args()

logging.info('reading input from %s' %args.dir.upper())
annotations = []
relevant_files = list(glob.iglob(args.dir + '/*.conll3'))
for rf in relevant_files:
    print (rf)
    annotations.extend(bio_annotation.BIO_Annotation.read_annotation_from_corpus(rf))
span_sets = [bio_annotation.BIO_Annotation.compute_structured_spans(annotation) for annotation in annotations]

logging.info("number of spans to compare %d" % len(span_sets))

to_analyse = {
    'Based_on': [combinator.subordinated,
                  {
                     'layout': 'n:m',
                     'n': 10
                  }],
    'Moment_of':   [combinator.moments,
                  {
                    'layout': 'n:m',
                    'n': 50
                    }
                   ],
    'Analog_to': [combinator.analogs,
                  {
                      'layout': 'n:m',
                      'n': 10
                  }
                  ]
    }

logging.info('comparing')
all_annotations = {}
nlp_annotator = basic_nlp_annotator.BasicAnnotator(layout='structured_span')
nlp_annotated_annotations = [[[nlp_annotator.annotate(span) for span in spans] for spans in span_set] for span_set in
                             span_sets]
nlp_annotated_annotations = [sps for sps in nlp_annotated_annotations if sps and len(sps) > 1
                             and all(
    all(any(s['kind'] == kind for s in sp) for kind in annotation_kind_set) for sp in sps)]
nlp_annotated_annotations = list(
    {''.join(f['text'] for g in e for f in g): e for e in nlp_annotated_annotations}.values())
logging.info("ScienceMap has to compare %d (not unique ... %d) annotation sets!" %(len(nlp_annotated_annotations), len(span_sets)- len(nlp_annotated_annotations)))

print()

for rel_kind, (sim_mix, params) in to_analyse.items():
    logging.info('...  for ' + rel_kind)
    entailed = combinator.combine(nlp_annotated_annotations=nlp_annotated_annotations, sim=sim_mix, params=params)
    all_annotations[rel_kind] = entailed


logging.info('producing short information for for graph building')
relations = []
def defining_relations(annotation_set):
    for side in annotation_set:
        for annotation in side:
            if len(annotation)!=2:
                logging.info ('skipping annotation with more than two spans %s' % str( annotation))
                continue
            subj, contrast = annotation
            yield (subj["text"], "defines", contrast["text"])

def opposed_relations(annotation_sets, connect_on='CONTRAST'):
    to_connect = [annotation for annotation_set in annotation_sets for side in annotation_set for annotation in side if annotation['kind'] == connect_on]
    for a,b in pairwise(to_connect):
        yield (a['text'], 'opposed', b['text'])

for rel_kind, related in all_annotations.items():
    #related = [rs for rs in related if all(len(r[0])==2 for r in rs)]
    # TODO broadcast to more than two!
    for a,b in related:
        a_defs = list(defining_relations(a))
        b_defs = list(defining_relations(b))
        a_ops = list(opposed_relations(a))
        b_ops = list(opposed_relations(b))

        relations.extend(a_defs)
        relations.extend(b_defs)
        relations.extend(a_ops)
        relations.extend(b_ops)

        tups = []
        tups += [(a[i], rel_kind, b[i]) for a in a_defs for b in b_defs for i in [0,2]]
        tups += [(a[i], rel_kind, b[i]) for a in a_ops for b in b_ops for i in [0, 2]]
        tups += [(a[i], rel_kind, b[i]) for a in a_ops for b in b_defs for i in [0, 2]]
        tups += [(a[i], rel_kind, b[i]) for a in a_defs for b in b_ops for i in [0, 2]]


        relations.extend(tups)

logging.info('writing output file')
with open(args.dir + "/relations.csv", 'w+') as f:
    f.write("|n1|rel|n2\n")
    for id, rel in enumerate(relations):
        f.write("|".join([str(id), *rel]) +"\n")

logging.info("ScienceMap finished!")

#lemmatize
#link wordnet information
#link synonyms

