import json
import string

import wn
from tqdm import tqdm

from utils import STOP_WORDS

en = wn.Wordnet('oewn:2024')


words = {}
unused_words = []


def get_definition(lemma, pos):
    definition = en.synsets(lemma, pos=pos)[0].definition()
    definition = ''.join(c for c in definition if c not in string.punctuation)
    definition = ' '.join(word for word in definition.split()
                          if word.lower() not in STOP_WORDS)
    return definition


for i, w in enumerate(tqdm(en.words(), desc='Gathering words')):
    lemma = w.lemma()
    pos = w.pos
    if ' ' in lemma:
        unused_words.append(lemma)
        continue
    try:
        definition = get_definition(lemma, pos)
        words[lemma] = definition
    except IndexError:
        try:
            definition = get_definition(lemma, 's')
            words[lemma] = definition
        except IndexError:
            print(f'Error on {lemma} for pos {pos}')
            continue


nodes = []
for i, (w, d) in enumerate(words.items()):
    nodes.append({'id': i, 'label': w, 'def': d, 'value': 0, 'connected': 0})

edges = []
for n1 in tqdm(nodes):
    for n2 in nodes:
        if n1['id'] == n2['id']:  # don't look up its own definition
            continue
        def_words = n2['def'].split(' ')

        for _w2 in list(set(def_words)):
            if n1['label'] == _w2:
                n1['value'] += 1
                n2['connected'] += 1
                edges.append(
                    {'from': n1['id'], 'to': n2['id'], 'arrows': 'middle'})


filt_nodes = []
for n in nodes:
    if n['value'] <= 0 and n['connected'] <= 0:
        continue
    n.pop('def')
    n.pop('connected')
    filt_nodes.append(n)


with open("chains.js", "w") as f:
    f.write("const NODES = ")
    json.dump(filt_nodes, f)
    f.write(";")
    f.write('\n')

    f.write("const EDGES = ")
    json.dump(edges, f)
    f.write(";")
