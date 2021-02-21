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