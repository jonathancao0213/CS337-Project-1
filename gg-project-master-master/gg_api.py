'''Version 0.35'''

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']

import numpy as np
import pandas as pd
import spacy
from spacy import displacy
from collections import defaultdict
import Levenshtein
import operator

from spacy.matcher import Matcher
from spacy.tokens import Span
from string import punctuation

nlp = spacy.load('en_core_web_md')
matcher = Matcher(nlp.vocab)

if year == '2013' or year == '2015':
    new_award_names = OFFICIAL_AWARDS_1315
else:
    new_award_names = OFFICIAL_AWARDS_1819

def DistMeasure(tweet):
    awards = {}
    tweet = tweet.lower()
    tweet = tweet.replace('tv', 'television')
    tweet = tweet.replace('film', 'motion picture')
    tweet = tweet.replace('movie', 'motion picture')
    for award in new_award_names:
        split_award = award.split()
        award_dist = 0
        
        split_tweet = tweet.split()
        for word in split_tweet:
            array = []
            for word2 in split_award:
                array.append(Levenshtein.distance(word, word2))
            min_val = array[np.argmin(array)]
            award_dist += min_val
        awards[award] = award_dist
        
    val = min(awards.values())
    res = [key for key in awards if awards[key] == val]
    if len(res) > 10:
        res = []
    return res

def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    df = pd.read_json(('../gg' + year + '.json'))
    df = df['text']
    host_df = df[df.str.contains('host|hosts|hostess|hosted|hosting', case = False)]
    df = df[~df.str.contains('think|thinking|should|maybe', case = False)]
    df = df.str.replace('#GoldenGlobes|golden|globes|globe', "", case = False)
    if host_df.size > 3000:
        host_df = host_df.sample(3000)

    hosts = {}
    hosts = defaultdict(lambda: 1, hosts)
    for i, value in host_df.iteritems():
        for entity in nlp(value).ents:
            if entity.label_ == 'PERSON':
                hosts[entity.text] = hosts[entity.text] +1
                
    hosts = sorted(hosts.items(), key=lambda item: item[1], reverse = True)

    top30 = hosts[:30]
    for name in range(5):
        first_name = top30[name][0].split()[0]
        for other in range(29-name):
            curr_name = top30[other+name+1][0]
            if first_name in curr_name:
                count = top30[name][1] + top30[other+name+1][1]
                top30[name] = (top30[name][0], count)

    final30 = sorted(top30, key=lambda item: item[1], reverse = True)
    hosts = (final30[0][0], final30[1][0])

    return hosts

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    return awards

def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    # Your code here
    return nominees

def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    df = pd.read_json('../gg' + year + '.json')
    df = df['text']
    df = df[df.str.contains('won best|wins best|goes to', case = False)]
    df = df[~df.str.contains('think|thinking|should|maybe', case = False)]
    wins_df = df.str.replace('#GoldenGlobes|golden|globes|globe', "", case = False)
    if wins_df.size > 5000:
        wins_df = wins_df.sample(5000)

    pattern1 = [{"ENT_TYPE": "PERSON", 'OP':'+'}, {"LEMMA": "win"}, {"ORTH":'Best'}, {"DEP": 'compound', 'OP':'+'}, {"POS":'NOUN', 'OP':'*'}, {'IS_PUNCT': True, 'OP':'?'}, {"POS": 'PROPN', 'OP':'*'}]
    pattern2 = [{"ENT_TYPE": "WORK_OF_ART", 'OP':'+'}, {"LEMMA": "win"}, {"ORTH":'Best'}, {"DEP": 'compound', 'OP':'+'}, {"POS":'NOUN', 'OP':'*'}, {'IS_PUNCT': True, 'OP':'?'}, {"POS": 'PROPN', 'OP':'*'}]
    pattern3 = [{"ENT_TYPE": "PERSON", 'OP':'+'}, {"LEMMA": "win"}, {"ORTH":'Best'}, {"ENT_TYPE": "WORK_OF_ART", 'OP':'+'}]
    pattern4 = [{"ENT_TYPE": "WORK_OF_ART", 'OP':'+'}, {"LEMMA": "win"}, {"ORTH":'Best'}, {"ENT_TYPE": "WORK_OF_ART", 'OP':'+'}]
    pattern5 = [{"ORTH":'Best'}, {"ENT_TYPE": "WORK_OF_ART", 'OP':'+'},{"TEXT": "goes"}, {"TEXT": "to"}, {"ENT_TYPE": "PERSON", 'OP':'+'}] 
    pattern6 = [{"ORTH":'Best'}, {"DEP": 'compound', 'OP':'+'}, {"POS":'NOUN', 'OP':'*'}, {'IS_PUNCT': True, 'OP':'?'}, {"POS": 'PROPN', 'OP':'*'}, {"TEXT": "goes"}, {"TEXT": "to"}, {"ENT_TYPE": "PERSON", 'OP':'+'}] 
    
    matcher.add("Winner", [pattern1, pattern2, pattern3, pattern4, pattern5, pattern6])

    winners = {}
    winners = defaultdict(lambda: 1, winners)
    for i, text in wins_df.iteritems():
        doc = nlp(text)
        matches = matcher(doc)
        if len(matches) != 0:
            span = doc[matches[-1][1]:matches[-1][2]]
            winners[str(span).strip(punctuation).strip()] = winners[str(span).strip(punctuation).strip()] +1
    
    winners = sorted(winners.items(), key=lambda item: item[1], reverse = True)

    award_list = [dict() for x in range(len(new_award_names))]

    for tweet in winners: 
        tweet = tweet[0]
        split = tweet.lower().split()
        
        index = split.index("best")

        award_phrase = " ".join(split[index:])
        matching_awards = DistMeasure(award_phrase)
        for a in matching_awards:
            award_index = new_award_names.index(a)
            global person
            person = ''
            if "goes" in split and "to" in split:
                print("goes")
                person_index = split.index("goes")
                person = split[person_index+2:]
                print(person)
            else:
                person = split[:index-1]
            person = " ".join(person)
            if person not in award_list[award_index]:
                award_list[award_index][person] = 1
            else:
                award_list[award_index][person] = award_list[award_index][person]+1

    i = 0
    awards = [[] for x in range(len(new_award_names))]
    for award in award_list:
        if award != {}:
            max_val = max(award.items(), key=operator.itemgetter(1))[1]
            j = 0
            list_award = list(award)
            for b in award:
                if award[b] == max_val and len(awards[i]) < 1:
                    awards[i].append(list_award[j])
                j+=1
        i+=1

    for award in awards: 
    if len(award) == 0:
        award.append("NO WINNER FOUND")
    award_flat = np.array(awards).flatten()
    winners = dict(zip(award_names, award_flat)) 

    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    # Your code here
    df = pd.read_json('../gg' + year + '.json')
    df = df['text']
    df = df[df.str.contains(' present', case = False)]
    df = df[~df.str.contains('think|should|maybe', case = False)]
    present_df = df.str.replace('#GoldenGlobes|golden|globes|globe', "", case = False)
    if present_df.size > 5000:
        present_df = present_df.sample(5000)
        return presenters

    pattern1 = [{"ENT_TYPE": "PERSON", 'OP':'+'}, {"LEMMA": "present"}, {"ORTH":'Best'}, {"DEP": 'compound', 'OP':'+'}, {"POS":'NOUN', 'OP':'*'}, {'IS_PUNCT': True, 'OP':'?'}, {"POS": 'PROPN', 'OP':'*'}]
    pattern2 = [{"ENT_TYPE": "WORK_OF_ART", 'OP':'+'}, {"LEMMA": "present"}, {"ORTH":'Best'}, {"DEP": 'compound', 'OP':'+'}, {"POS":'NOUN', 'OP':'*'}, {'IS_PUNCT': True, 'OP':'?'}, {"POS": 'PROPN', 'OP':'*'}]
    pattern3 = [{"ENT_TYPE": "PERSON", 'OP':'+'}, {"LEMMA": "present"}, {"ORTH":'Best'}, {"ENT_TYPE": "WORK_OF_ART", 'OP':'+'}]
    pattern4 = [{"ENT_TYPE": "WORK_OF_ART", 'OP':'+'}, {"LEMMA": "present"}, {"ORTH":'Best'}, {"ENT_TYPE": "WORK_OF_ART", 'OP':'+'}]

    matcher.add("Presenter", [pattern1, pattern2, pattern3, pattern4])

    presenters = {}
    presenters = defaultdict(lambda: 1, presenters)
    for i, text in present_df.iteritems():
        doc = nlp(text)
        matches = matcher(doc)
        if len(matches) != 0:
            span = doc[matches[-1][1]:matches[-1][2]]
            presenters[str(span).strip(punctuation).strip()] = presenters[str(span).strip(punctuation).strip()] +1

    presenters = sorted(presenters.items(), key=lambda item: item[1], reverse = True)

    award_list = [dict() for x in range(len(new_award_names))]

    for tweet in presenters: 
        tweet = tweet[0]
        split = tweet.lower().split()
        
        index = split.index("best")

        award_phrase = " ".join(split[index:])
        matching_awards = DistMeasure(award_phrase)
        for a in matching_awards:
            award_index = new_award_names.index(a)  
            person = split[:index-1]
            person = " ".join(person)
            if person not in award_list[award_index]:
                award_list[award_index][person] = 1
            else:
                award_list[award_index][person] = award_list[award_index][person]+1

    i = 0
    awards = [[] for x in range(len(new_award_names))]
    for award in award_list:
        if award != {}:
            max_val = max(award.items(), key=operator.itemgetter(1))[1]
            j = 0
            list_award = list(award)
            for b in award:
                if award[b] == max_val and len(awards[i]) < 2:
                    awards[i].append(list_award[j])
                j+=1
        i+=1

    presenters = dict(zip(award_names, awards)) 
    return presenters


def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    print("Pre-ceremony processing complete.")
    return

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    # Your code here
    return

if __name__ == '__main__':
    main()
