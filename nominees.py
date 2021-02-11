import numpy as np
import pandas as pd
import spacy
from spacy import displacy
from collections import defaultdict
from spacy.matcher import Matcher
from spacy.tokens import Span
import en_core_web_sm
nlp = spacy.load('en_core_web_sm')
from string import punctuation

award_names = ['Best Motion Picture – Drama', 'Best Motion Picture – Musical or Comedy', 'Best Motion Picture – Foreign Language',
 'Best Motion Picture – Animated', 'Best Director – Motion Picture', 'Best Actor in a Motion Picture – Drama',
 'Best Actor in a Motion Picture – Musical or Comedy', 'Best Actress in a Motion Picture – Drama',
 'Best Actress in a Motion Picture – Musical or Comedy', 'Best Supporting Actor – Motion Picture',
 'Best Supporting Actress – Motion Picture', 'Best Screenplay – Motion Picture', 'Best Original Score – Motion Picture',
 'Best Original Song – Motion Picture', 'Best Television Series – Drama', 'Best Television Series – Musical or Comedy',
 'Best Miniseries or Motion Picture – Television', 'Best Actor in a Television Series – Drama',
 'Best Actor in a Television Series – Musical or Comedy', 'Best Actor in a Miniseries or Motion Picture – Television',
 'Best Actress in a Television Series – Drama', 'Best Actress in a Television Series – Musical or Comedy',
 'Best Actress in a Miniseries or Motion Picture – Television',
 'Best Supporting Actor in a Series, Miniseries or Motion Picture – Television',
 'Best Supporting Actress in a Series, Miniseries or Motion Picture – Television']
new_award_names = [0]*len(award_names)
for i in range(len(award_names)):
    new_award_names[i] = award_names[i].lower()

winnerswithaward = {}
winnerswithaward = defaultdict(lambda: 1, winnerswithaward)

for award in award_names:
    winnerswithaward[award] = ''

df = pd.read_json('../gg2013.json')
df = df['text']
df = df.str.replace('#GoldenGlobes|golden|globes|globe', "", case = False)
nominees_df = df[df.str.contains('nominated', case = False)]

pattern1 = [{"ORTH":'Best'}, {"DEP": 'compound', 'OP':'+'}, {"POS":'NOUN', 'OP':'*'}, {'IS_PUNCT': True, 'OP':'?'}, {"POS": 'PROPN', 'OP':'*'}]
pattern2 = [{"ORTH":'Best'}, {"ENT_TYPE": "WORK_OF_ART", 'OP':'+'}]

matcher = Matcher(nlp.vocab)
matcher.add("Award", [pattern1])

bleh = {}
bleh = defaultdict(lambda: 1, bleh)
for i, text in nominees_df.iteritems():
    doc = nlp(text)
    matches = matcher(doc)
    if len(matches) != 0:
        span = doc[matches[-1][1]:matches[-1][2]]
        bleh[str(span).strip(punctuation).strip()] = bleh[str(span).strip(punctuation).strip()] +1

print(bleh)