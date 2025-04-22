import json
from django.conf import settings
from django.db import models

# Create your models here.
class Document(models.Model):
	docId = models.CharField(max_length=100)
	text = models.TextField()
	# add document

	def __str__(self):
		return self.docId

	def get_content(self):
		content = ""
		try:
			with open(settings.DATA_DIR+"/"+self.docId) as f:
			    read = f.read()
			    try:
			        metadata = json.loads(read)['metadata']
			        self.text = "{} {} {} -- #{}".format(
			                metadata['company_name'],
			                metadata['form'],
			                metadata['filing_date'],
			                metadata['order'],
			        )
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
    return {str(i): 0 for i in range(15)}
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
	comment = models.TextField(default="", null=True)
	nuggets = models.JSONField(default=default_query_nuggets)

	def __str__(self):
		data_dict = {
                "id": self.qId,
                "text": self.text,
                "highlight": self.comment,
		}
		to_return = json.dumps(data_dict)
		# return '{%s: %s}'% (self.qId, self.text)
		return to_return + '\n'

	def unfinished(self):
		return sum([1 if v == '' else 0 for v in self.nuggets.values()]) > 0

	def unclassified(self):
	    return sum([int(v) for v in self.type.values()]) == 0

	def num_unjudged_docs(self):
		unjugded = [judgement for judgement in self.judgements() if judgement.relevance < 0]
		return len(unjugded)

	def num_judgements(self):
		return len(self.judgements())

	def judgements(self):
		return Judgement.objects.filter(query=self.id)

class Judgement(models.Model):
	labels = {-1: 'Unjudged', 0: 'Not relvant', 1: 'Somewhat relevant', 2:'Highly relevant'}

	query = models.ForeignKey(Query, on_delete=models.CASCADE)
	document = models.ForeignKey(Document, on_delete=models.CASCADE)
	comment = models.TextField(default="", null=True)
	relevance = models.IntegerField()

	def __str__(self):
		return '%s Q0 %s %s\n' % (self.query.qId, self.document.docId, self.relevance)

	def label(self):
		return self.labels[self.relevance]
