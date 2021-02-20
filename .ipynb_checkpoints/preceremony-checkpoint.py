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
import time

start_time = time.time()

# Function to see if two strings are close enough (essentially levenstein)
def closeenough(a,b): 
  a = a.split() 
  b = b.split() 
  k = set(a).symmetric_difference(set(b)) 
  return True if len(k) <= 2 else False


OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']


new_award_names = [0]*len(OFFICIAL_AWARDS_1315) # Or the other one
for i in range(len(OFFICIAL_AWARDS_1315)):
    new_award_names[i] = OFFICIAL_AWARDS_1315[i].lower()
    new_award_names[i] = OFFICIAL_AWARDS_1315[i].replace(" in ", " ").replace(" a ", " ").replace(" or ", " ").replace(" – ", " ").replace(" - ", " ").lower()
#     if "television" in new_award_names[i]:
#         new_award_names[i].append("tv")


# Make DF -------------------------------------------------------------------------------------------------------------
year = "2013" # change this from year to year
df = pd.read_json(('../gg' + year + '.json'))
df = df['text']
df = df.str.replace('#GoldenGlobes|#GoldenGlobe|Golden Globe|Golden Globes', "", case = False, regex = False)


# Make dictionaries for each field ------------------------------------------------------------------------------------
nowords = ['think', 'thinking', 'should', 'maybe']

hosts = {}
hosts = defaultdict(lambda: 1, hosts)
host_words = ['host', 'hosts', 'hostess', 'hosted', 'hosting']
# Uses nowords

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
# Uses nowords


# Instantiate some dictionaries ---------------------------------------------------------------------------------------
for award in OFFICIAL_AWARDS_1315:
    award_winners[award] = ''
    award_presenters[award] = []
    award_nominees[award] = []


# Patterns ------------------------------------------------------------------------------------------------------------
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


# Loop through df -----------------------------------------------------------------------------------------------------
for i, text in df.iteritems():
    doc = nlp(text)

    # Nominees pattern matcher
    if 'Best' in text:
        nominee_matches = nominee_matcher(doc)
        if len(nominee_matches) != 0:
            span = doc[nominee_matches[-1][1]:nominee_matches[-1][2]]
            sent = str(span).strip(punctuation).strip().replace('- ','').lower()
            if "tv" in sent:
                sent.replace("tv",'television')
                
            # awarded = 0
            for i, award in enumerate(new_award_names):
                if sent == award or sent in award or closeenough(sent, award):
                    for ent in nlp(text.replace("sent","")).ents:
                        if ent.label_ == "PERSON" or ent.label_ == "WORK_OF_ART":
                            award_nominees[list(award_nominees)[i]].append(ent.text)
                            # awarded = 1

    if not any(x in text.lower() for x in nowords):

        # Award names pattern matcher
        if 'Best' in text:
            award_matches = award_matcher(doc)
            if len(award_matches) != 0:
                span = doc[award_matches[-1][1]:award_matches[-1][2]]
                award_names[str(span).strip(punctuation).strip()] += 1

        # Award presenters pattern matcher
        if ' presents' in text.lower() or ' present' in text.lower():
            presenter_matches = presenter_matcher(doc)
            if len(presenter_matches) != 0:
                span = doc[presenter_matches[-1][1]:presenter_matches[-1][2]]
                award_presenters[str(span).strip(punctuation).strip()] += 1
        
        # Hosts pattern matcher
        if any(x in text.lower() for x in host_words):
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    hosts[ent.text] += 1

        # Award winner pattern matcher
        if any(x in text.lower() for x in award_winners_words):
            winner_matches = winner_matcher(doc)
            if len(winner_matches) != 0:
                span = doc[winner_matches[-1][1]:winner_matches[-1][2]]
                award_winners[str(span).strip(punctuation).strip()] += 1


print(award_names)
print(award_winners)
print(award_presenters)
print(award_nominees)
print(print("--- %s seconds ---" % (time.time() - start_time)))

