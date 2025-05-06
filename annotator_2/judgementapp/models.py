import json
from django.conf import settings
from django.db import models

# Create your models here.
class Document(models.Model):
    docId = models.CharField(max_length=100)
    # add document

    def __str__(self):
        return self.docId

    def get_content(self):
        content = ""
        try:
            with open(settings.DATA_DIR+"/"+self.docId) as f:
                read = f.read()
                try:
                    data = json.loads(read)
                    content = json.loads(read)['contents']
                except:
                    content += read
        except Exception:
            content = "Could not read file %s" % settings.DATA_DIR+"/"+self.docId
        return content

def default_query_types():
    return {str(i): 0 for i in range(3)}
def default_query_metadata():
    return {'num_oracle_passages': -1, 'type': 'none'}

def default_query_questions():
    return {str(i): None for i in range(15)}
def default_query_question_labels():
    return {str(i): -1 for i in range(15)}
def default_query_nuggets():
    return {str(i): '' for i in range(50)}

class Query(models.Model):
    # qId = models.IntegerField()
    qId = models.CharField(max_length=100)
    text = models.CharField(max_length=300, default="NA")
    topic = models.JSONField(default={'1': 1})
    # crux
    metadata = models.JSONField(default=default_query_metadata)
    questions = models.JSONField(default=default_query_questions)
    question_labels = models.JSONField(default=default_query_question_labels)
    reference = models.TextField()
    report = models.TextField()

    # labeling
    nuggets = models.JSONField(default=default_query_nuggets)

    def __str__(self):
        answerabiliy = [self.question_labels[k] for k in self.questions]
        questions = [v if v is not None else "NA" for k, v in self.questions.items()]
        nuggets = [v for k, v in self.nuggets.items()]

        data_dict = {
                "id": self.qId,
                "question_based_nugget": {q: n for (q, n) in zip(questions, nuggets)},
                "answerability": answerabiliy,
                "coverage": sum(a==1 for a in answerabiliy) / len(answerabiliy),
        }
        to_return = json.dumps(data_dict)
        return to_return + '\n'

    def unfinished(self):
        n_total = sum([1 for v in self.question_labels.values() if v != -2])
        n_judged = sum([1 for v in self.question_labels.values() if v >= 0])

        if n_judged == 0:
            return 0 
        elif n_total != n_judged:
            return 1
        else:
            return 2

    def unclassified(self):
        return sum([int(v) for v in self.type.values()]) == 0

    def num_unjudged_docs(self):
        unjugded = [1 for judgement in self.judgements() if max(judgement.relevances.values()) == -1]
        return len(unjugded)

    def num_judgements(self):
        return len(self.judgements())

    def judgements(self):
        return Judgement.objects.filter(query=self.id)

def default_judgement_relevances():
    return {str(i): -1 for i in range(15)}
def default_judgement_rationales():
    return {str(i): "" for i in range(15)}

class Judgement(models.Model):
    labels = {-1: 'Unjudged', 0: 'Not relvant', 1: 'minimally relevant', 2:'limited relevant', 3:'partially relevant', 4:'mostly relevant', 5:'fully relevant'}
    query = models.ForeignKey(Query, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    comment = models.TextField(default="", null=True)
    # relevance = models.IntegerField()

    relevances = models.JSONField(default=default_judgement_relevances)
    rationales = models.JSONField(default=default_judgement_rationales)
    judged = models.BooleanField(default=False)


    def __str__(self):
        data_dict = {
                "id": self.query.qId,
                "document": self.document.docId,
                "relevances": self.relevances,
                "rationales": self.rationales,
        }
        to_return = json.dumps(data_dict)
        return to_return + '\n'

    def update_judged(self):
        self.judged = (max(self.relevances.values()) != -1)

    def label(self):
        return "{" + ", ".join(f"Q-{i}: {r}" for i, r in enumerate(self.relevances.values()) if r != -1) + "}"

# old document-level judgement
# class Judgement(models.Model):
#     labels = {-1: 'Unjudged', 0: 'Not relvant', 1: 'minimally relevant', 2:'limited relevant', 3:'partially relevant', 4:'mostly relevant', 5:'fully relevant'}
#     query = models.ForeignKey(Query, on_delete=models.CASCADE)
#     document = models.ForeignKey(Document, on_delete=models.CASCADE)
#     comment = models.TextField(default="", null=True)
#     relevance = models.IntegerField()
#
#     def __str__(self):
#         return '%s Q0 %s %s\n' % (self.query.qId, self.document.docId, self.relevance)
#
#     def label(self):
#         return self.labels[self.relevance<strong>e]
