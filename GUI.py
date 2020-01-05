import glob
import logging
from argparse import ArgumentParser
from pprint import pprint
import bio_annotation
import neo4j_handler
import combinator
import os
from littletools.nested_list_tools import pairwise
os.environ['SPACY_WARNING_IGNORE'] = 'W008'
logging.getLogger().setLevel(logging.INFO)


parser = ArgumentParser(description='Mixing the corpus to train/test/valid conll3s.')
parser.add_argument('dir',
                    nargs='?',
                    type=str,
                    help='directory to process conll3s together',
                    default="./test")
args = parser.parse_args()

neo4j_db = neo4j_handler.Neo4JHandler()

logging.info('reading input')
annotations = []
relevant_files = list(glob.iglob(args.dir + '/*.conll3'))
for rf in relevant_files:
    annotations.extend(bio_annotation.BIO_Annotation.read_annotation_from_corpus("test/dependent_differences_test.conll3"))
span_sets = [bio_annotation.BIO_Annotation.compute_structured_spans(annotation) for annotation in annotations]

logging.info("number of spans to compare %d" % len(span_sets))

to_analyse = {
    'Based_on': [combinator.subordinated,
                  {
                     'layout': '1:1',
                     'n': 10
                  }],
    'Moment_of':   [combinator.moments,
                  {
                    'layout': 'n',
                    'n': 50
                    }
                   ],
    'Analog_to': [combinator.analogs,
                  {
                      'layout': 'n',
                      'n': 10
                  }
                  ]
    }

logging.info('comparing')
all_annotations = {}
for rel_kind, (sim_mix, params) in to_analyse.items():
    logging.info('... at the moment for ' + rel_kind)
    entailed = combinator.combine(span_sets=span_sets, sim=sim_mix, params=params)
    #neo4j_db.add_comparison_results(entailed, D_KIND='Def', L_KIND='Level', R_KIND=rel_kind)
    #neo4j_db.run(f"MATCH ()-[r:{rel_kind}]-() WHERE r.value<1 DELETE r")
    all_annotations[rel_kind] = entailed

#combinator.combine_wordnet(span_sets=span_sets)
#"""
#neo4j_db.run(f"""match ()-[r]-()
#    where r.value<0.1
#    delete r
#    return 1""")


#neo4j_db.run(f"""match (n)-[r]-(n)
#    delete r
#    return 1""")

#import os
#neo4j_db.run(r"call apoc.export.graphml.all('{path}/graph.graphml', {{useTypes:true, storeNodeIds:false}})".format(path=os.getcwd()))


#pprint (all_annotations)

logging.info('producing short information for for graph building')
relations = []
def defining_relations(annotation_set):
    for side in annotation_set:
        for annotation in side:
            subj, contrast = annotation
            yield (subj["text"], "defines", contrast["text"])

def opposed_relations(annotation_sets, connect_on='CONTRAST'):
    to_connect = [annotation for annotation_set in annotation_sets for side in annotation_set for annotation in side if annotation['kind'] == connect_on]
    for a,b in pairwise(to_connect):
        yield (a['text'], 'opposed', b['text'])

for rel_kind, related in all_annotations.items():
    for a,b in related:
        a_defs = list(defining_relations(a))
        b_defs = list(defining_relations(b))
        a_ops = list(opposed_relations(a))
        b_ops = list(opposed_relations(b))

        relations.extend(a_defs)
        relations.extend(b_defs)
        relations.extend(a_ops)
        relations.extend(b_ops)

        tups = [(a[0], rel_kind, b[0]) for a in a_defs for b in b_defs]
        relations.extend(tups)

logging.info('writing output file')
with open(args.dir + "/relations.csv", 'w+') as f:
    f.write(",n1,rel,n2\n")
    for id, rel in enumerate(relations):
        f.write("|".join([str(id), *rel]) +"\n")


#lemmatize
#link wordnet information
#link synonyms

