import pandas as pd
from collections import defaultdict

pd.options.display.max_colwidth = 250

def find_user(user, df):
    data = []
    for i, each in enumerate(df['user']):
        if each['screen_name'] == user:
            data.append(i)
    return data

df = pd.read_json('../gg2013.json')

eonline = find_user('eonline', df)
print(eonline)

text = df['text']
eonline = text[eonline]

print(eonline)

rt = text[text.str.contains('RT')]
# rt = rt.sample(100)
print(len(rt))

usernames = {}
usernames = defaultdict(lambda: 1, usernames)
for each in rt:
    user = each.split()[1]
    usernames[user] = usernames[user] + 1

usernames = sorted(usernames.items(), key=lambda item: item[1], reverse = False)
usernames = usernames[:-1]

print(usernames)