import numpy as np
import pandas as pd
import spacy
import random

nlp = spacy.load("en_core_web_sm")

def shortensentence(key, sentence, length):
    i = sentence.split().index(key)
    ilow = i - length
    ihigh = i + length + 1

    sent = sentence.split()[ilow:ihigh]
    sent = ' '.join(sent)

    return sent

def findkey(key, sentence):
    if key in sentence:
        return sentence
    else:
        return None

def names(num, data):
    names = {}
    randomsample = random.sample(range(len(data)), num)
    for each in data[randomsample]:
        for ent in nlp(each).ents:
            if ent.label_ == "PERSON":
                if ent.text in names:
                    names[ent.text] += 1
                else:
                    names[ent.text] = 1
    
    return names

df = pd.read_json('../gg2013.json')
textnuser = df.filter(items=['text','user'])
text = df['text']

# text = text[:10000]

bests = []
bestdressed = []
nominated = []
hosts = []
winsomething = []

keys = ["best "]

num = 0

for each in text:
    each = each.lower().replace("golden","").replace("globes","").replace("globe","").replace("#","").strip()
    eachlst = each.split()

    if 'best' in eachlst:
        num += 1

    if "best " in each:
        length = 5

        token = each.split()

        try:
            short = shortensentence('best', each, length)
            if len(short.split()) < length*2:
                bests.append(each)
            else:
                bests.append(short)

            i = token.index('best')
            if token[i+1] == 'dressed':
                bestdressed.append(each)
            

        except:
            bests.append(each)


        # if "wins " in each or "win " in each or "won " in each or "win" in each:
        #     winsomething.append(each)

    if "nominated " in each or "Nominated " in each:
        nominated.append(each)


# print(*bests, sep="\n")


# print(*bestdressed, sep='\n')
# print(len(bests))
# print(len(bestdressed))
# print(num)
# print(total)

if __name__ == "__main__":
    names = names(2000, text)
    strictlynames = []
    for n in names:
        if len(n.split()) == 2 or len(n.split()) == 3:
            if "RT" not in n.split():
                strictlynames.append(n)

    print(strictlynames)