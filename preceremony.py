import numpy as np
import pandas as pd
import spacy
from spacy import displacy
from collections import defaultdict
import en_core_web_md
nlp = en_core_web_md.load()
from spacy.matcher import Matcher
from spacy.tokens import Span
from string import punctuation
import operator

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']

# Make DF
year = "2013" # change this from year to year
df = pd.read_json(('../gg' + year + '.json'))
df = df['text']
df = df.str.replace('#GoldenGlobes|#GoldenGlobe|Golden Globe|Golden Globes', "", case = False, regex = False)

# Make dictionaries for each field
nowords = ['think', 'thinking', 'should', 'maybe']

hosts = {}
hosts = defaultdict(lambda: 1, hosts)
host_words = ['host', 'hosts', 'hostess', 'hosted', 'hosting']

award_names = {}
award_names = defaultdict(lambda: 1, award_names)
# Uses nowords

award_winners = {}
award_winners = defaultdict(lambda: 1, award_winners)
award_winners_words = ['won best', 'wins best', 'goes to']
# Uses nowords

award_nominees = {}
award_nominees = defaultdict(lambda: 1, award_nominees)


award_presenters = {}
award_presenters = defaultdict(lambda: 1, award_presenters)
award_presenters_words = [' presents']
# Uses nowords

# Pattern for award names
award_pattern = [{"ORTH":'Best'}, {"DEP": 'compound', 'OP':'+'}, {"POS":'NOUN', 'OP':'*'}, {'IS_PUNCT': True, 'OP':'?'}, {"POS": 'PROPN', 'OP':'*'}]

award_matcher = Matcher(nlp.vocab)
award_matcher.add("Awards", None, award_pattern)

# Pattern for award winners
winner_pattern1 = [{"ENT_TYPE": "PERSON", 'OP':'+'}, {"LEMMA": "win"}, {"ORTH":'Best'}, {"DEP": 'compound', 'OP':'+'}, {"POS":'NOUN', 'OP':'*'}, {'IS_PUNCT': True, 'OP':'?'}, {"POS": 'PROPN', 'OP':'*'}]
winner_pattern2 = [{"ENT_TYPE": "WORK_OF_ART", 'OP':'+'}, {"LEMMA": "win"}, {"ORTH":'Best'}, {"DEP": 'compound', 'OP':'+'}, {"POS":'NOUN', 'OP':'*'}, {'IS_PUNCT': True, 'OP':'?'}, {"POS": 'PROPN', 'OP':'*'}]
winner_pattern3 = [{"ENT_TYPE": "PERSON", 'OP':'+'}, {"LEMMA": "win"}, {"ORTH":'Best'}, {"ENT_TYPE": "WORK_OF_ART", 'OP':'+'}]
winner_pattern4 = [{"ENT_TYPE": "WORK_OF_ART", 'OP':'+'}, {"LEMMA": "win"}, {"ORTH":'Best'}, {"ENT_TYPE": "WORK_OF_ART", 'OP':'+'}]
winner_pattern5 = [{"ORTH":'Best'}, {"ENT_TYPE": "WORK_OF_ART", 'OP':'+'},{"TEXT": "goes"}, {"TEXT": "to"}, {"ENT_TYPE": "PERSON", 'OP':'+'}] 
winner_pattern6 = [{"ORTH":'Best'}, {"DEP": 'compound', 'OP':'+'}, {"POS":'NOUN', 'OP':'*'}, {'IS_PUNCT': True, 'OP':'?'}, {"POS": 'PROPN', 'OP':'*'}, {"TEXT": "goes"}, {"TEXT": "to"}, {"ENT_TYPE": "PERSON", 'OP':'+'}]

winner_matcher = Matcher(nlp.vocab)
winner_matcher.add("Winners", [winner_pattern1, winner_pattern2, winner_pattern3, winner_pattern4, winner_pattern5, winner_pattern6])

# Pattern for award presenters
presenter_pattern1 = [{"ENT_TYPE": "PERSON", 'OP':'+'}, {"LEMMA": "present"}, {"ORTH":'Best'}, {"DEP": 'compound', 'OP':'+'}, {"POS":'NOUN', 'OP':'*'}, {'IS_PUNCT': True, 'OP':'?'}, {"POS": 'PROPN', 'OP':'*'}]
presenter_pattern2 = [{"ENT_TYPE": "WORK_OF_ART", 'OP':'+'}, {"LEMMA": "present"}, {"ORTH":'Best'}, {"DEP": 'compound', 'OP':'+'}, {"POS":'NOUN', 'OP':'*'}, {'IS_PUNCT': True, 'OP':'?'}, {"POS": 'PROPN', 'OP':'*'}]
presenter_pattern3 = [{"ENT_TYPE": "PERSON", 'OP':'+'}, {"LEMMA": "present"}, {"ORTH":'Best'}, {"ENT_TYPE": "WORK_OF_ART", 'OP':'+'}]
presenter_pattern4 = [{"ENT_TYPE": "WORK_OF_ART", 'OP':'+'}, {"LEMMA": "present"}, {"ORTH":'Best'}, {"ENT_TYPE": "WORK_OF_ART", 'OP':'+'}]

presenter_matcher = Matcher(nlp.vocab)
presenter_matcher.add("Presenters", [presenter_pattern1, presenter_pattern2, presenter_pattern3, presenter_pattern4])

# Pattern for award nominees
nominee_pattern1 = [{"ORTH":'Best'}, {"DEP": 'compound', 'OP':'+'}, {"POS":'NOUN', 'OP':'*'}, {'IS_PUNCT': True, 'OP':'?'}, {"POS": 'PROPN', 'OP':'*'}]
nominee_pattern2 = [{"ORTH":'Best'}, {"ENT_TYPE": "WORK_OF_ART", 'OP':'+'}]

nominee_matcher = Matcher(nlp.vocab)
nominee_matcher.add("Nominee", [nominee_pattern1, nominee_pattern2])

for i, text in df.iteritems():
    if any(x in a_string for x in matches)






