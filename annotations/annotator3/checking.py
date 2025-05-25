import numpy as np
import json

# qlabels

bm25, rankfirst = [], []

# coverage
a, b, c = [], [], []

# answerability
answerability = {'bm25': [], 'rankfirst': [], 'oracle': []}
with open('qlabels.jsonl', 'r') as f:
    for line in f:
        data = json.loads(line.strip())
        if 'bm25' in data['id']:
            all = [i for i in data['answerability'] if i != -2]
            true = [i for i in all if i == 1]
            a.append( len(true) / len(all) )
            bm25.append(data)
            answerability['bm25'] += data['answerability']

        elif 'rankfirst' in data['id']:
            all = [i for i in data['answerability'] if i != -2]
            true = [i for i in all if i == 1]
            b.append( len(true) / len(all) )
            rankfirst.append(data)
            answerability['rankfirst'] += data['answerability']

        else:
            all = [i for i in data['answerability'] if i != -2]
            true = [i for i in all if i == 1]
            c.append( len(true) / len(all) )
            answerability['oracle'] += data['answerability']


print(len(a), len(b), len(c))
print('oracle', np.mean(c), np.std(c))
print('bm25', np.mean(a), np.std(a))
print('rankfirst', np.mean(b), np.std(b))
print('oracle', c)
print('bm25', a)
print('dr_rankfirst', b)

print('Answerability = ', answerability)


# print([i for i, v in enumerate(a) if v > b[i]])
# print([i for i, v in enumerate(a) if v < b[i]])
# print([d['id'] for d in bm25])
# print([d['id'] for d in rankfirst])
# for i in [0, 2, 5, 6, 7]:
#     print(bm25[i]['id'])
#     print(rankfirst[i]['id'])
#     for j, lbl in enumerate(bm25[i]['answerability']):
#         if lbl > rankfirst[i]['answerability'][j]:
#             print('1', j, list(bm25[i]['question_based_nugget'].items())[j])
#             print('2', j, list(rankfirst[i]['question_based_nugget'].items())[j])
#     print('---')
