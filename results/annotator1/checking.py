import numpy as np
import json

# qlabels

data1 = {}
with open('archived/qlabels_annotator1-2.jsonl', 'r') as f:
    for line in f:
        d = json.loads(line.strip())
        data1[d['id']] = d


data2 = {}
with open('archived/qlabels_annotator1-1-revised.jsonl', 'r') as f:
    for line in f:
        d = json.loads(line.strip())
        data2[d['id']] = d


with open('qlabels_a1.jsonl', 'w') as f:
    for key in data1:
        if np.any(np.array(data1[key]['answerability']) == -1):
            if np.any(np.array(data2[key]['answerability']) == -1):
                print(data1[key]['answerability'])
                print(data2[key]['answerability'])
            else:
                f.write(json.dumps(data2[key]) + '\n')
        else:
            f.write(json.dumps(data1[key]) + '\n')


a, b, c = [], [], []
bm25, rankfirst = [], []
with open('qlabels_a1.jsonl', 'r') as f:
    for line in f:
        data = json.loads(line.strip())
        if 'bm25' in data['id']:
            all = [i for i in data['answerability'] if i != -2]
            true = [i for i in all if i == 1]
            a.append( len(true) / len(all) )
            bm25.append(data)

        elif 'rankfirst' in data['id']:
            all = [i for i in data['answerability'] if i != -2]
            true = [i for i in all if i == 1]
            b.append( len(true) / len(all) )
            rankfirst.append(data)

        else:
            all = [i for i in data['answerability'] if i != -2]
            true = [i for i in all if i == 1]
            c.append( len(true) / len(all) )

print(len(a), len(b), len(c))
print('oracle', np.mean(c), np.std(c))
print('bm25', np.mean(a), np.std(a))
print('rankfirst', np.mean(b), np.std(b))
print('bm25', a)
print('rankfirst', b)


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
