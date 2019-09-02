import bio_annotation
import neo4j_handler
import combinator

import os
os.environ['SPACY_WARNING_IGNORE'] = 'W008'
neo4j_db = neo4j_handler.Neo4JHandler()

annotations = bio_annotation.BIO_Annotation.read_annotation_from_corpus("./manual_corpus/dependent_differences_test.conll3")
span_sets = [bio_annotation.BIO_Annotation.compute_structured_spans(annotation) for annotation in annotations]

to_analyse = {
    'UNDERLIES': combinator.subordinated,
    'MOMENTS':   combinator.moments
}

for rel_kind, sim_mix in to_analyse.items():
    entailed = combinator.combine(span_sets=span_sets, sim=sim_mix)
    neo4j_db.add_comparison_results(entailed, D_KIND='DEF_OF', L_KIND='LEVEL', R_KIND=rel_kind)
    neo4j_db.run(f"MATCH ()-[r:{rel_kind}]-() WHERE r.value<1 DELETE r")

neo4j_db.run(f"""match ()-[r]-()
    where r.value<0.1
    delete r
    return 1""")

#lemmatize
#link wordnet information
#link synonyms!!!

