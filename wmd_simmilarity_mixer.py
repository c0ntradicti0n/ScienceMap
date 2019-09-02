from Bio import pairwise2
from addict import addict

from similaritymixer import SimilarityMixer



def left_right_encircle(match_density):
    start, stop = 0, 1
    for p in range(len(match_density)):
        start = p
        stop = p + 1

        if match_density[p]<0.6 or (len(match_density[p:])>1 and (sum(match_density[p:]) / len(match_density[p:])
                < sum(match_density[p + 1:])
                / len(match_density[p + 1:]))):
            continue
        else:
            for q in range(len(match_density)-1, p, -1):
                if match_density[q]<0.6 or (sum(match_density[:q]) / len(match_density[:q])
                        > sum(match_density[:q + 1])
                        / len(match_density[:q + 1])):
                    continue
                else:
                    stop = q+1
                    break
            else:
                stop = p + 1
            break
    return start, stop


def fuzzy_search(search_key, text, strictness):
    lines = text.split("\n")
    for i, line in enumerate(lines):
        words = line.split()
        for word in words:
            similarity = SequenceMatcher(None, word, search_key)
            if similarity.ratio() > strictness:
                return " '{}' matches: '{}' in line {}".format(search_key, word, i+1)


def match (hay, needle):
    needle_length  = len(needle.split())
    max_sim_val    = 0
    max_sim_string = u""

    for ngram in ngrams(hay.split(), needle_length + int(.2*needle_length)):
        hay_ngram = u" ".join(ngram)
        similarity = SM(None, hay_ngram, needle).ratio()
        if similarity > max_sim_val:
            max_sim_val = similarity
            max_sim_string = hay_ngram
    return max_sim_string, max_sim_val


def sort(word_list):
    """
    >>> sort (['Mammals', 'eat', 'sometimes', 'fish'])
    [(1, 3, 0, 2), ('eat', 'fish', 'Mammals', 'sometimes')]

    :param word_list:
    :return:
    """
    return list(zip(*sorted(list(enumerate(word_list)), key=lambda x: x[1].lower())))


def match():
    """
    >>> text1 = ['there', 'be', 'many', 'cause', 'of', 'heart', 'failure', 'include', 'have', 'have', 'a', 'myocardial', 'infarction', ',', 'have', 'hypertension', ',', 'heart', 'valve', 'problem', ',', 'cardiomyopathy', ',', 'coronary', 'artery', 'disease', 'and', 'diabetes']
    text1 = "There are many causes of heart failure including having had a myocardial infarction, having hypertension, heart valve problems, cardiomyopathy, coronary artery disease and diabetes".split()

    >>> text2 = ['most', 'often', 'genetic', ',', 'or', 'else', 'from', 'a', 'viral', 'infection', 'or', 't', ',', 'cruzi']

    >>> match_with_biopython(text1, text2)
    False

    >>> text2 = ['cardiomyopathy', ',', 'coronary', 'artery', 'problems', ',', 'heart', 'attack', ',', 'hypertension', ',', 'valve', 'conditions']
    >>> match_with_biopython(text1, text2)
    (0, 17, 78.60000000000011, 17)

    >>> text1[0:17]

    :return:
    """




def match_with_biopython (text1, text2, ignore_order=False):
    ''' Let's match a string with biopython. It's not the fastest choice. But it solves a problem.

    It's hard, because one can normally either match strings against each other, or words, treating them as characters,
    but not a list of words fitting to another list of words. This here operates on fitting the string and then it
    searches a local optimum, where the word-borders fitting chars may belong.

    Python difflib can operate either on strings or on dilimited lists.

    :param text1: list of words
    :param text2: list of words
    :return: tuple of left pos, right pos, confidence score and length

    >>> match_with_biopython(['bid', 'be', 'make', 'by', 'buyer'], ['buyer'])
    (4, 5, 10.0, 1)

    >>> match_with_biopython(['heart', 'failure', 'can', 'be', 'treat', 'with', 'the', 'same', 'medication', 'as', 'cardiomyopathy', 'but', 'also', 'nitrate', 'and', 'diuretic', ',', 'and', 'sometimes', 'a', 'cardioverter', '-', 'defibrillator', 'or', 'a', 'transplanted', 'heart', 'may', 'be', 'necessary', 'for', 'survival'],
    ...                      ['cardiomyopathy'])
    (10, 11, 28.0, 1)

    >>> match_with_biopython(['a', 'positive', 'tb', 'skin', 'test', 'be', 'when', 'the', 'mantoux', 'tuberculin', 'skin', 'test', 'indicate', 'that', 'a', 'person', 'have', 'the', 'bacteria', 'or', 'have', 'be', 'expose', 'to', 'm.', 'tuberculosis'],
    ...                      ['negative', 'tb', 'skin', 'test'])
    (0, 5, 35.1, 5)

    >>> match_with_biopython(['cardiomyopathy', 'be', 'a', 'problem', 'in', 'the', 'heart', 'muscle'],
    ...                      ['this', 'condition', 'occur', 'when', 'there', 'be', 'a', 'problem', 'with', 'the', 'heart', 'muscle', ',', 'the', 'myocardium'])
    (1, 8, 70.2, 7)

    >>> match_with_biopython(['cardiomyopathy', 'can', 'be', 'treat', 'with', 'medication', 'such', 'as', 'beta', 'blocker', ',', 'digoxin', ',', 'and', 'calcium', 'channel', 'blocker'],
    ...                      ['treatment'])
    (3, 4, 14.400000000000007, 1)

    # handle empty token
    >>> match_with_biopython(['cardiomyopathy', 'but', 'also', 'nitrate', 'and', 'diuretic', ',', 'and', 'sometimes', 'a', 'cardioverter', '', 'defibrillator', 'or', 'a', 'transplanted', 'heart', 'may', 'be', 'necessary', 'for', 'survival'],
    ...                      ['cardiomyopathy'])
    (0, 1, 28.0, 1)

    >>> match_with_biopython(['cardiomyopathy', 'can', 'be', 'treat', 'with', 'medication', 'such', 'as', 'beta', 'blocker', ',', 'digoxin', ',', 'and', 'calcium', 'channel', 'blocker'],
    ...                      ['medication'])
    (5, 6, 20.0, 1)

    >>> match_with_biopython(['heart', 'failure', 'be', 'not', 'a', 'common', 'condition', 'find', 'in', 'child'],
    ...                      ['definition'])
    False

    >>> match_with_biopython('if they were normal Python strings, for example getting the length, or iterating over'.split(),
    ...                      'iterating over'.split())
    (12, 14, 28.0, 2)

    >>> match_with_biopython('if'.split(),
    ...                      'if'.split())
    (0, 1, 4.0, 1)

    >>> match_with_biopython('if'.split(),
    ...                      'then'.split())
    False

    >>> match_with_biopython('if they were normal Python strings, for example getting the length, or iterating over'.split(),
    ...                      'if they'.split())
    (0, 2, 14.0, 2)

    >>> match_with_biopython('if they were normal Python strings, for example getting the length, or iterating over'
    ...                          'the elements'.split(),
    ...                          'they are normal Python schrings, so example get th len'.split())
    (1, 8, 95.00000000000001, 7)

    >>> match_with_biopython(['We', 'bought', 'more', 'milk'], ['more'])
    (2, 3, 8.0, 1)

    '''
    if ignore_order:
        translation_list1, text1 = sort(text1)
        translation_list2, text2 = sort(text2)

    alignments = pairwise2.align.localms(
        list(" ".join(text1).lower()),
        list(" ".join(text2).lower()),
        2, -1, -.5, -.1, gap_char=['-'],
        one_alignment_only=True)

    if not alignments:
        return False

    dashed2 = alignments[0][0]
    dashed1 = alignments[0][1]
    alignment_score = alignments[0][2]

    # translate to dashed
    match_text = []
    match_density = []
    i_glob = 0

    # compute for each matched word a density, how well it fits based on the biopython alignment

    # go through the single words in the text, to match on
    for i, w in enumerate(text1):
        lw = list(w)

        # go through the single word
        for j, c in enumerate(w):
            try:
                # if its not matching, marked by a '-' dash, then shift the position in the dashed biopython result
                while j + i_glob < len(dashed2)-3 and dashed2[j + i_glob] == '-':
                    i_glob += 1

                if dashed1[j + i_glob] == '-':
                    lw[j] = dashed1[j + i_glob]
            except:
                # Todo, find out, why this gets to big, but it's not soo important
                pass

        if len(w) != 0:
            match_density.append((len(lw) - lw.count('-')) / len(lw))
        else:
            match_density.append(0.0)

        match_text.append("".join(lw))

        i_glob += len(w) + 1


    assert (len(text1) == len(match_text))
    assert (len(text1) == len(match_density))

    if max(match_density)<1:
        return False

    start, stop = left_right_encircle(match_density)

    if ignore_order:
        start = translation_list1[start]
        stop = translation_list1[stop]
    return start, stop, alignment_score

@SimilarityMixer.standard_range(-1, 8000)
def biopython_diff_encircle(exs1, exs2):

    text1 = exs1['text']
    text2 = exs2['text']
    start, stop, sim = match_with_biopython(text1=text1, text2=text2)
    beam = {exs1['id']:{
        exs2['id']:sim
    }}
    return sim, beam


from fuzzywuzzy import fuzz

@SimilarityMixer.standard_range(0, 100)
def sub_suffixtree(exs1, exs2):
    st = exs1['st']
    text1 = exs1['text'].lower()

    text2 = exs2['text'].lower()
    match = text2.find(text1)
    l = len (text1)

    if text1 in text2:
        print ('contained')

    print (text1, text2)

    if match != -1:
        if match+l >=  len(text2):
            x=1
        sim = fuzz.ratio (text2[match:match+l], text1)
    else:
        sim = 0
    beam = {exs1['id']:{
        exs2['id']:sim
    }}
    return sim, beam

@SimilarityMixer.standard_range(-1, 1)
def wmd_similarity(span1, span2):
    beam = {span1['id']:{
        span2['id']:'x'
    }}

    if not span1 or not span1:
        return 0, beam
    doc1 = span1['doc']
    doc2 = span2['doc']
    #if not doc1.vector_norm or not doc2.vector_norm:
    #    logging.error('Spacy tries to compute similarity on non vectorized word in %s' % str((span1, span2)))
    #    return 0, beam

    if not doc1 or not doc2:
        return 0, beam
    try:
        sim = doc1.similarity(doc2)
        beam = {span1['id']: {
            span2['id']: sim
        }}
        return sim, beam
    except ZeroDivisionError:
        #logging.error('Fallback with fuzzy text comparison, because spacy has incorrectshell')
        #span1.similarity(span2)
        return SimilarityMixer.fuzzytext_sim(text1, text2)
