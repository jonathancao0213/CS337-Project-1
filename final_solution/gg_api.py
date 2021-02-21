'''Version 0.35'''

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']


import numpy as np
import pandas as pd
import spacy
from spacy import displacy
from collections import defaultdict
import Levenshtein
import json

from spacy.matcher import Matcher
from spacy.tokens import Span
from string import punctuation


nlp = spacy.load('en_core_web_md')
# award_names = [1]
def map_to_a_award(tweet):
    awards = {}
    tweet = tweet.lower()
    for award in award_names:
        split_award = award.split()
        award_dist = 0
        split_tweet = tweet.split()
        for word in tweet.split():
            min_val = float('inf')
            for word2 in award.split():
                min_val = min(min_val,Levenshtein.distance(word, word2))
            award_dist += min_val
        awards[award] = award_dist
        
    val = min(awards.values())
    res = [key for key in awards if awards[key] == val]
    return res

def find_mapping(matches, doc):
    winner_len = 0
    award_len = 0
    winner = ''
    award = ''
    for match_id, start, end in matches:
        string_id = nlp.vocab.strings[match_id]
        span = doc[start:end]
        span_len = len(span.text)
        if string_id == 'Person' and len(span)<= 2:
            if winner_len < span_len:
                winner = span.text
                winner_len = span_len
        if string_id == 'Film':
            if winner_len > span_len:
                winner = span.text
                winner_len = span_len       
        elif string_id == 'Award':
            if award_len < span_len:
                award = span.text
                award_len = span_len
    winner = str(winner).strip(punctuation).strip()
    award = str(award).strip(punctuation).strip()
    key = (winner.lower(),award)
    return key

def distance(t1,r1):
    t = t1.split()
    r = r1.split()
    if len(t) >= len(r):
        long = t
        short = r
        ret = t1
    else:
        long = r
        short = t
        ret = r1
    dist = 0
    for word in short:
        min_val = float('inf')
        for word2 in long:
            min_val = min(min_val,Levenshtein.distance(word, word2))
        dist += min_val
    return dist,ret

def commonwords(a,b):
    return len(set(a.split()).intersection(set(b.split())))

def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    df = pd.read_json('./gg%d.json' % year)
    df = df['text']
    df = df[~df.str.contains('think|thinking|should|maybe', case = False)]
    df = df[df.str.contains('host', case = False)]
    host_df = df.str.replace('#GoldenGlobes|GoldenGlobes|golden|globes|globe', "", case = False, regex = True)
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
    hosts = [final30[0][0], final30[1][0]]

    return hosts

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    df = pd.read_json('./gg%d.json' % year)
    df = df['text']
    df = df[~df.str.contains('think|should|maybe|RT @', case = False)]
    df = df[df.str.contains('best', case = False)]
    df = df.str.replace('http\S+|www.\S+', '', case=False,regex=True)
    df = df.str.replace('TV|tv', "television", case = False, regex = True)
    best_df = df.str.replace('#GoldenGlobes|#GoldenGlobe|golden|globes|globes', "", case = False, regex = True)

    if best_df.shape[0] >5000:
        best_df = best_df.sample(n=5000)
    best_df.shape[0]

    pattern = [{"LOWER":'best'}, {"DEP":{"IN":['compound','nmod','dobj','prep','det','pobj','amod','nsubj','ROOT']}, 'OP':'+'},{'ORTH': '-', 'OP':'?'}, {"POS": {"IN": ['PROPN','NOUN','CCONJ','ADJ']}, 'OP':'*'}]
    pattern2 = [{"ENT_TYPE":{"IN":['PERSON','WORK_OF_ART']},'OP':'+'}]

    matcher = Matcher(nlp.vocab)
    matcher.add('Winner', [pattern])

    matcher2 = Matcher(nlp.vocab)
    matcher2.add('Deleter',[pattern2])

    awards = {}
    awards = defaultdict(lambda: 1, awards)
    for i, text in best_df.iteritems():
        doc = nlp(text)
        matches = matcher(doc)
        if len(matches) != 0:
            span = doc[matches[-1][1]:matches[-1][2]]
            awards[str(span).strip(punctuation).strip()] = awards[str(span).strip(punctuation).strip()] + 1

    for key in list(awards):
        doc = nlp(key)
        matches = matcher2(doc)
        if len(matches) != 0:
            awards.pop(key)

    awards = sorted(awards.items(), key=lambda item: item[1], reverse = True)

    new_awards = []
    for i in awards:
        if i[1] > 2:
            new_awards.append(i[0].lower())

    final_list = []
    final_list.append(new_awards[0])

    for awrd in new_awards[1:]:
        similar = False
        for i,ans in enumerate(final_list):
            dist,long = distance(awrd,ans)
            if dist <= 1:
                similar = True
                final_list[i] = long
        if (not similar):
            final_list.append(awrd)

    awards = final_list[0:26]
    return awards

def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    # Your code here
    nominees = None
    return nominees

def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    df = pd.read_json('./gg%d.json' % year)
    df = df['text']
    df = df[df.str.contains('won|win|goes to|for best', case = False)]
    df = df[~df.str.contains('think|should|maybe|RT @', case = False)]
    df = df[df.str.contains('best', case = False)]
    df = df.str.replace('http\S+|www.\S+', '', case=False,regex=True)
    df = df.str.replace('TV|tv', "television", case = False, regex = True)
    wins_df = df.str.replace('#GoldenGlobes|#GoldenGlobe|golden|globes|globes', "", case = False, regex = True)
    if wins_df.size > 6000:
        wins_df = wins_df.sample(6000)


    person_pattern = [{"ENT_TYPE": "PERSON", 'OP':'+'}]
    film_pattern = [{"ENT_TYPE": 'ORG', 'OP':'+'}]

    award_pattern = [{"LOWER":'best'}, {"DEP":{"IN":['compound','nmod','dobj','prep','det','pobj','amod','nsubj','ROOT']}, 'OP':'+'},{'ORTH': '-', 'OP':'?'}, {"POS": {"IN": ['PROPN','NOUN','CCONJ','ADJ']}, 'OP':'*'}]

    matcher = Matcher(nlp.vocab)
    matcher.add('Person',[person_pattern])
    matcher.add('Award',[award_pattern])
    matcher.add('Film',[film_pattern])

    winners = {}
    winners = defaultdict(lambda: 0, winners)
    for i, text in wins_df.iteritems():
        doc = nlp(text)
        matches = matcher(doc)
        if len(matches) != 0:
            key = find_mapping(matches, doc)
            if (key[0] != '' and key[1] != ''):
                winners[key] = winners[key] + 1

    final_ans = {}
    for award in award_names:
        sub_dict = {}
        sub_dict = defaultdict(lambda: 0, sub_dict)
        final_ans[award] = sub_dict
    for pair,count in winners.items():
        award = pair[1]
        person = pair[0]
        possible_awards = map_to_a_award(award)
        for ard in possible_awards:
            final_ans[ard][person] = final_ans[ard][person] + count
    for ans in final_ans:
        if len(final_ans[ans].items()) > 0:
            final_ans[ans] = max(final_ans[ans], key=final_ans[ans].get)
        else:
            final_ans[ans] = ''

    winners = final_ans
    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    # Your code here
    df = pd.read_json('./gg%d.json' % year)
    df = df['text']
    df = df[df.str.contains(' present|announc|introduc', case = False)]
    df = df[~df.str.contains('think|should|maybe|RT @', case = False)]
    df = df.str.replace('http\S+|www.\S+', '', case=False,regex=True)
    df = df.str.replace('TV|tv', "television", case = False, regex = True)
    present_df = df.str.replace('#GoldenGlobes|golden|globes|globe', "", case = False, regex =True)
    if present_df.size > 6000:
        present_df = present_df.sample(6000)

    person_pattern = [{"ENT_TYPE": "PERSON", 'OP':'+'}]
    award_pattern = [{"LOWER":'best'}, {"DEP":{"IN":['compound','nmod','dobj','prep','det','pobj','amod','nsubj','ROOT']}, 'OP':'+'},{'ORTH': '-', 'OP':'?'}, {"POS": {"IN": ['PROPN','NOUN','CCONJ','ADJ']}, 'OP':'*'}]

    matcher = Matcher(nlp.vocab)
    matcher.add('Person',[person_pattern])
    matcher.add('Award',[award_pattern])

    presenters = {}
    presenters = defaultdict(lambda: 0, presenters)
    for i, text in present_df.iteritems():
        doc = nlp(text)
        matches = matcher(doc)
        if len(matches) != 0:
            key = find_mapping(matches, doc)
            if (key[0] != '' and key[1] != ''):
                presenters[key] = presenters[key] +1


    presenters = dict(presenters)

    final_ans = {}
    for award in award_names:
        sub_dict = {}
        sub_dict = defaultdict(lambda: 0, sub_dict)
        final_ans[award] = sub_dict
    for pair,count in presenters.items():
        award = pair[1]
        person = pair[0]
        possible_awards = map_to_a_award(award)
        for ard in possible_awards:
            final_ans[ard][person] = final_ans[ard][person] + count
    for ans in final_ans:
        if len(final_ans[ans].items()) > 0:
            m = max(final_ans[ans], key=final_ans[ans].get)
            final_ans[ans].pop(m)
            m2 = max(final_ans[ans], key=final_ans[ans].get)
            
            while commonwords(m, m2) != 0:
                final_ans[ans].pop(m2)
                try:
                    m2 = max(final_ans[ans], key=final_ans[ans].get)
                except:
                    m2 = ''
            
            final_ans[ans] = [m,m2]
        else:
            final_ans[ans] = []

    presenters = final_ans
    return presenters

def winner_presenter_nominees_helper(year): # This function is to help the nominees be more accurate, see main for how it's run
    winners = get_winner(year)
    presenters = get_presenters(year)

    new_award_names = [0]*len(award_names)
    for i in range(len(award_names)):
        new_award_names[i] = award_names[i].replace(" in ", " ").replace(" a ", " ").replace(" or ", " ").replace(" – ", " ").replace(" - ", " ").lower()

    awardnominees = {}
    awardnominees = defaultdict(lambda: 1, awardnominees)

    for award in award_names:
        awardnominees[award] = []

    df = pd.read_json('./gg%d.json' % year)
    df = df['text']
    df = df[~df.str.contains('RT @', case = False)]
    df = df[df.str.contains('Best', case = True)]
    nominees_df = df.str.replace('#GoldenGlobes|golden|globes|globe', "", case = False, regex =True)
    # nominees_df = df[df.str.contains('nominated', case = False)]
    if nominees_df.size > 6500:
        nominees_df = nominees_df.sample(6500)

    for i, text in nominees_df.iteritems():
        for j, award in enumerate(new_award_names):
            awardlst = award.split()
            awardlst2 = award.replace("television ", "").split()
            if all(x in text.lower() for x in awardlst) or all(x in text.lower() for x in awardlst2):
                for ent in nlp(text).ents:
                    if (ent.label_ == "PERSON" or ent.label == "WORK_OF_ART") and '#' not in ent.text and '@' not in ent.text:
                        awardnominees[list(awardnominees)[j]].append(ent.text)

    for lst in awardnominees:
        dd = defaultdict( int )
        for word in awardnominees[lst]:
            dd[word] += 1
        
        awardnominees[lst] = dd

    nominees_final = {}
    for i, each in enumerate(awardnominees):
        nominees_final[each] = [winners[each]]
        
        noms = sorted(awardnominees[each].items(), key=lambda item: item[1], reverse = True)
        
        if noms == []:
            continue
            
        for j, (name, num) in enumerate(noms):
            name = name.lower()
            # if j == 0:
            #     nominees_final[each].append(name)
            # else:
            common = 1
            for inlst in nominees_final[each]:
                if commonwords(inlst, name) != 0:
                    common = 0

            if common == 1 and len(nominees_final[each]) < 5 and name not in presenters[each] and '/' not in name and 'rt' not in name:
                nominees_final[each].append(name)

    return winners, presenters, nominees_final

def get_best_dressed(year):
    df = pd.read_json('./gg%d.json' % year)
    df = df['text']
    df = df[df.str.contains('best dressed|glamorous|jealous|dress|stunning|fav|gorgeous|red carpet', case = False)]
    dressed_df = df.str.replace('#GoldenGlobes|golden|globes|globe', "", case = False, regex = True)
    

    if dressed_df.size > 6000:
        dressed_df = dressed_df.sample(6000)

    dressed = {}

    dressed = defaultdict(lambda: 1, dressed)
    for i, value in dressed_df.iteritems():
        for entity in nlp(value).ents:
            if entity.label_ == 'PERSON':
                dressed[entity.text] = dressed[entity.text] +1
                
    dressed = sorted(dressed.items(), key=lambda item: item[1], reverse = True)

    best_dressed = []
    for d in dressed:
        word = d[0].replace("'s", "")
        if len(best_dressed) == 5:
            break
        if len(best_dressed) == 0:
            best_dressed.append(word)
        else:
            common = 1
            for c in best_dressed:
                if commonwords(c, word) != 0:
                    common = 0

            if common == 1:
                best_dressed.append(word)

    # best_dressed = [d[0] for d in dressed[:5]]
    return best_dressed

def get_worst_dressed(year):
    df = pd.read_json('./gg%d.json' % year)
    df = df['text']
    df = df[df.str.contains('worst dressed|ugly|gross|weird|worst', case = False)]
    dressed_df = df.str.replace('#GoldenGlobes|golden|globes|globe', "", case = False, regex = True)

    if dressed_df.size > 6000:
        dressed_df = dressed_df.sample(6000)

    dressed = {}

    dressed = defaultdict(lambda: 1, dressed)
    for i, value in dressed_df.iteritems():
        for entity in nlp(value).ents:
            if entity.label_ == 'PERSON':
                dressed[entity.text] = dressed[entity.text] +1
                
    dressed = sorted(dressed.items(), key=lambda item: item[1], reverse = True)

    worst_dressed = []
    for d in dressed:
        word = d[0].replace("'s", "")
        if len(worst_dressed) == 5:
            break
        if len(worst_dressed) == 0:
            worst_dressed.append(word)
        else:
            common = 1
            for c in worst_dressed:
                if commonwords(c, word) != 0:
                    common = 0

            if common == 1:
                worst_dressed.append(word)

    return worst_dressed

def get_best_jokes(year):
    df = pd.read_json('./gg%d.json' % year)
    df = df['text']
    df = df[df.str.contains('funny|funniest|joke|haha|hilarious', case = False)]
    jokes_df = df.str.replace('#GoldenGlobes|golden|globes|globe', "", case = False, regex = True)

    if jokes_df.size > 6000:
        jokes_df = jokes_df.sample(6000)

    jokes = {}
    jokes = defaultdict(lambda: 1, jokes)
    for i, text in jokes_df.iteritems():
        for entity in nlp(text).ents:
            if entity.label_ == 'PERSON':
                jokes[entity.text] = jokes[entity.text] +1
                
    jokes = sorted(jokes.items(), key=lambda item: item[1], reverse = True)

    best_jokes = []
    for d in jokes:
        word = d[0].replace("'s", "")
        if len(best_jokes) == 5:
            break
        if len(best_jokes) == 0:
            best_jokes.append(word)
        else:
            common = 1
            for c in best_jokes:
                if commonwords(c, word) != 0:
                    common = 0

            if common == 1:
                best_jokes.append(word)

    return best_jokes

def get_best_parties(year):
    df = pd.read_json('./gg%d.json' % year)
    df = df['text']
    parties_df = df[df.str.contains('party|parties|lit', case = False)]
    parties_df = parties_df.str.replace('#GoldenGlobes|golden|globes|globe', "", case = False, regex = True)
    if parties_df.size > 6000:
        parties_df = parties_df.sample(6000)


    parties = {}
    parties = defaultdict(lambda: 1, parties)
    for i, text in parties_df.iteritems():
        for entity in nlp(text).ents:
            if entity.label_ == 'GPE':
                parties[entity.text] = parties[entity.text] +1
                
    parties = sorted(parties.items(), key=lambda item: item[1], reverse = True)

    return parties[:5]

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
    json_2013 = {}
    json_2015 = {}

    year = [2013,2015]
    for each in year:
        global award_names
        if each == 2013:
            award_names= OFFICIAL_AWARDS_1315
        elif each == 2015:
            award_names= OFFICIAL_AWARDS_1819

        [winners, presenters, nominees] = winner_presenter_nominees_helper(each)
        print('Winner, presenters,nominees done')
        awards = get_awards(each)
        print('awards done')
        hosts = get_hosts(each)
        print('host done')
        best_dressed = get_best_dressed(each)
        print('best dress done')
        worst_dressed = get_worst_dressed(each)
        print('worst dress done')
        best_jokes = get_best_jokes(each)
        print('best jokes done')
        best_parties = get_best_parties(each)
        print('best parties done')

        print("Year = %d" % each)
        print("Hosts: %s, %s" % (hosts[0], hosts[1]))
        for award in award_names:
            print("Award: ", award)
            print("Presenters:", *presenters[award], sep=", ")
            print("Nominees: ", *nominees[award], sep=", ")
            print("Winner: %s" % winners[award])
            print("\n")
            if each == 2013:
                json_2013[award] = {}
                json_2013[award]["Presenters"] = presenters
                json_2013[award]["Nominees"] = nominees
                json_2013[award]["Winner"] = winners
            elif each == 2015:
                json_2015[award] = {}
                json_2015[award]["Presenters"] = presenters
                json_2015[award]["Nominees"] = nominees
                json_2015[award]["Winner"] = winners


        print("Overall Awards:-------------")
        print("Best Dressed: ", *best_dressed, sep=", ")
        print("Worst Dressed: ", *worst_dressed, sep=", ")
        print("Best Jokes: ", *best_jokes, sep=", ")
        print("Best Parties: ", *best_parties, sep=", ")
        print("\n")

        if each == 2013:
            json_2013["Host"] = hosts
            answers_2013 = open("answers_2013.json", "w")
            json.dump(json_2013, answers_2013)
            answers_2013.close()
        elif each == 2015:
            json_2015["Host"] = hosts
            answers_2015 = open("answers_2015.json", "w")
            json.dump(json_2015, answers_2015)
            answers_2015.close()
    return

if __name__ == '__main__':
    main()
