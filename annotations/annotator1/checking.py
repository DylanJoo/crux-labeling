import numpy as np
import json

# qlabels
# data1 = {}
# with open('archived/qlabels_annotator1-2.jsonl', 'r') as f:
#     for line in f:
#         d = json.loads(line.strip())
#         data1[d['id']] = d
#
#
# data2 = {}
# with open('archived/qlabels_annotator1-1-revised.jsonl', 'r') as f:
#     for line in f:
#         d = json.loads(line.strip())
#         data2[d['id']] = d
#
#
# with open('qlabels_a1.jsonl', 'w') as f:
#     for key in data1:
#         if np.any(np.array(data1[key]['answerability']) == -1):
#             if np.any(np.array(data2[key]['answerability']) == -1):
#                 print(data1[key]['answerability'])
#                 print(data2[key]['answerability'])
#             else:
#                 f.write(json.dumps(data2[key]) + '\n')
#         else:
#             f.write(json.dumps(data1[key]) + '\n')

answerability = {'bm25': [], 'rankfirst': [], 'oracle': []}

a, b, c = [], [], []
bm25, rankfirst = [], []
with open('qlabels.jsonl', 'r') as f:
    for line in f:
        data = json.loads(line.strip())
        if 'bm25' in data['id']:
            all = [i for i in data['answerability'] if i != -2]
            true = [i for i in all if i == 1]
            a.append( len(true) / len(all) )
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
print('rankfirst', b)

print('Answerability =', answerability)
