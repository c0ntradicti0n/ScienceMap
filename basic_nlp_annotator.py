from types import FunctionType

from allennlp.modules import Elmo
from suffix_trees import STree
import numpy as np
import spacy
import wmd
nlp = spacy.load("en_core_web_md")
#nlp.add_pipe(wmd.WMD.SpacySimilarityHook(nlp), last=True)
options_file = "models/elmo_2x1024_128_2048cnn_1xhighway_options.json"
weight_file = "models/elmo_2x1024_128_2048cnn_1xhighway_weights.hdf5"

# Compute two different representation for each token.
# Each representation is a linear weighted combination for the
# 3 layers in ELMo (i.e., charcnn, the outputs of the two BiLSTM))
from allennlp.commands.elmo import ElmoEmbedder
elmo = ElmoEmbedder(options_file=options_file, weight_file=weight_file)



import pipetools

def next_natural_number():
    i = 0
    while True:
        yield i
        i += 1

class BasicAnnotator:
    def __init__(self, layout=None):
        if not layout:
            self.make = (
                    pipetools.pipe |
                    self.make_text |
                    self.make_spacy_doc |
                    self.make_elmo_doc |
                    self.make_lemma_text |
                    self.make_id |
                    self.make_tree
            )
            self.remake = (
                    pipetools.pipe |
                    self.remake_text
            )
        elif layout == 'structured_span':
            self.make =  (
                    pipetools.pipe |
                    self.make_from_structured_span |
                    self.make_spacy_doc |
                    self.make_spacy_doc |
                    self.make_elmo_doc |
                    self.make_lemma_text |
                    self.make_id  |
                    self.make_tree
            )
            self.remake = (
                    pipetools.pipe |
                    self.remake_from_structured_span
            )
        elif isinstance(layout, FunctionType):
            self.make = layout
        else:
            raise ValueError('wrong input layout!')

        self.id = next_natural_number()
        next(self.id)

    def make_from_structured_span(self, span):
        kind, span_i, tokens = span
        text = " ".join(x[1][0] for x in tokens)
        ex = {
            'kind': kind,
            'span_i': span_i,
            'annotation_tokens': tokens,
            'text': text
        }
        return ex
    def remake_from_structured_span (self, ex):
        try:
            return (ex['kind'], (ex['id'], ex['id'] ), ex['annotation_tokens'])
        except Exception as e:
            raise

    def annotate (self, ex):
        return self.make(ex)
    def reannotate (self, ex):
        return self.remake(ex)

    def make_tree (self,ex):
        ex['st'] = STree.STree(ex['text'].lower())
        return ex

    def make_text (self, text):
        ex = {'text': text}
        return ex
    def remake_text (self, ex):
        return ex['text']


    def make_lemma_text (self, ex):
        ex['lemma_text'] =  " ".join([t.lemma_ for t in ex['doc']])
        return ex
    def remake_lemma_text (self, ex):
        return ex['lemma_text']


    def make_id (self, ex):
        ex['id'] = next(self.id)
        return ex

    def make_spacy_doc (self, ex):
       """
       >>> annotator = BasicAnnotator()
       >>> annotator.annotate('I am here!')
       {'text': 'I am here!', 'doc': I am here!}

       :return: dict with keys defined for the annotation pipeline
       """
       if not 'text' in ex:
           raise AttributeError('expression requires \'text\' key; start of pipeline must be make_text')
       doc = nlp (ex['text'])
       ex['doc'] = doc
       return ex

    def make_elmo_doc (self, ex):
       """

       :return: dict with keys defined for the annotation pipeline
       """
       if not 'text' in ex:
           raise AttributeError('expression requires \'text\' key; start of pipeline must be make_text')
       ex['elmo'] = np.array(elmo.embed_sentence([t.text for t in ex['doc']]), dtype=np.float32)
       return ex


if __name__ == '__main__':
    import doctest
    doctest.testmod()
