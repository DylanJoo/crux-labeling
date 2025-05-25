# Create your views here.
from io import StringIO
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import Context, loader, RequestContext
# from django.core.servers.basehttp import FileWrapper
from django.shortcuts import render, get_object_or_404
from wsgiref.util import FileWrapper

from judgementapp.models import *
import json

def examples(request, qId=None, docId=None):
    context = {'back_path': request.path.replace('examples/', '')}
    context.update({'is_doc': 'doc' in request.path})
    return render(request, 'judgementapp/examples.html', context)

def index(request):
    queries = Query.objects.order_by('qId')
    output = ', '.join([q.text for q in queries])

    # template = loader.get_template('judgementapp/index.html')
    context = {'queries': queries}
    # return HttpResponse(template.render(request, context))
    return render(request, 'judgementapp/index.html', context)

def qrels(request):
    # judgements = Judgement.objects.exclude(relevance=-1)
    judgements = Judgement.objects.exclude(judged=False)

    response = HttpResponse(judgements, content_type='application/force-download')
    # response['Content-Disposition'] = 'attachment; filename=qrels.txt'
    response['Content-Disposition'] = 'attachment; filename=qrels.jsonl'
    return response

def qlabels(request):
    # queries = Query.objects.all()
    queries = Query.objects.exclude(text="NA")

    response = HttpResponse(queries, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=qlabels.jsonl'
    #response['X-Sendfile'] = myfile
    # It's usually a good idea to set the 'Content-Length' header too.
    # You can also set any other required headers: Cache-Control, etc.
    return response

def query_list(request):
    # see if we need to add the filter (about the judged)
    queries = Query.objects.order_by('id')
    return render(request, 'judgementapp/query_list.html', {'queries': queries})

def query(request, qId):
    query = Query.objects.get(qId=qId)
    judgements = Judgement.objects.filter(query=query.id)

    if "clear" in request.POST:
        for n, question in query.questions.items():
            query.nuggets[n] = ""
        for n, label in query.question_labels.items():
            query.question_labels[n] = 0

    else:
        if "csrfmiddlewaretoken" in request.POST:
            for n, question in query.questions.items():
                query.nuggets[n] = request.POST.getlist(f'nugget-{n}')[0]
            for n, label in query.question_labels.items():
                try:
                    query.question_labels[n] = int(request.POST.getlist(f'qlabel-{n}')[0])
                except:
                    query.question_labels[n] = -2

    query.save()
    query.length = len(query.text)

    # navigation
    prev = None
    try:
        prev = Query.objects.get(id=query.id-1)
    except:
        pass

    next = None
    try:
        next = Query.objects.get(id=query.id+1)
    except:
        pass

    return render(request, 'judgementapp/query.html', 
            {'query': query, 'judgements': judgements, 
             'prev': prev, 'next': next}
    )

def document(request, qId, docId):
    document = Document.objects.get(docId=docId)
    query = Query.objects.get(qId=qId)

    judgements = Judgement.objects.filter(query=query.id)
    judgement = Judgement.objects.filter(query=query.id, document=document.id)[0]
    rank = -1
    for (count, j) in enumerate(judgements):
        if j.id == judgement.id:
            rank = count+1
            break


    prev = None
    try:
        prev = Judgement.objects.filter(query=query.id).get(id=judgement.id-1)
    except:
        pass

    next_query = None
    next = None
    try:
        next = Judgement.objects.filter(query=query.id).get(id=judgement.id+1)
    except:
        try:
            next_query = Query.objects.get(id=query.id+1)
        except:
            pass

    content = document.get_content()

    return render(request, 'judgementapp/document.html', 
            {'document': document, 'query': query, 
                'judgement': judgement, 'next': next, 'prev': prev, 
                'rank': rank, 'total_rank': judgements.count(), 
                'next_query': next_query,
                'content': content})

def judge(request, qId, docId):
    query = get_object_or_404(Query, qId=qId)
    document = get_object_or_404(Document, docId=docId)
    # relevance = request.POST['relevance']

    judgements = Judgement.objects.filter(query=query.id)
    judgement, created = Judgement.objects.get_or_create(query=query.id, document=document.id)
    # judgement.relevance = int(relevance)

    judged = [(s.split('-')[-1], request.POST.getlist(s)[0]) for s in request.POST if s.startswith('relevance-')]
    for n, rel in judged:
        judgement.relevances[n] = int(rel)

    judged = [(s.split('-')[-1], request.POST.getlist(s)[0]) for s in request.POST if s.startswith('rationale-')]
    for n, rationale in judged:
        judgement.rationales[n] = rationale

    judgement.update_judged()
    judgement.save()

    next = None
    try:
        next = Judgement.objects.filter(query=query.id).get(id=judgement.id+1)
        if 'next' in request.POST:
            document = next.document
            judgement = next
            next = Judgement.objects.filter(query=query.id).get(id=judgement.id+1)
    except:
        pass

    prev = None
    try:
        prev = Judgement.objects.filter(query=query.id).get(id=judgement.id-1)
    except:
        pass

    rank = -1
    for (count, j) in enumerate(judgements):
        if j.id == judgement.id:
            rank = count+1
            break


    content = document.get_content()

    # return render(request, 'judgementapp/upload.html', context)
    return render(request, 'judgementapp/document.html', 
            {'document': document, 'query': query, 
                'judgement': judgement, 'next': next, 'prev': prev, 
                'rank': rank, 'total_rank': judgements.count(), 
                'content': content
            }) 


def reset(request):
    # remove queries
    queries = Query.objects.all()
    n = len(queries)
    queries.delete()

    return render(request, 'judgementapp/upload.html', {
        "deleted": False, "amount": n
    })

def delete(request):
    # remove results
    judgements = Judgement.objects.filter(judged=False)
    n = len(judgements)
    judgements.delete()

    return render(request, 'judgementapp/upload.html', {
        "deleted": True, "amount": n
    })

def upload(request):
    context = {}

    if 'queryFile' in request.FILES:
        f = request.FILES['queryFile']
        qryCount = 0
        for i, query in enumerate(f):
            data = json.loads(query)
            qid = data['qid']
            text = data['topic']
            metadata = {
                'num_oracle_passages': data['type'][1],
                'type': data['type'][0],
            }
            questions = data['questions']
            reference = data['report']
            report = data['response']
            query, created = Query.objects.get_or_create(qId=qid)

            if created:
                query.text = text
                query.metadata = metadata
                for i, question in enumerate(questions):
                    query.questions[i] = question
                    if question is None:
                        query.question_labels[i] = -2
                query.reference = reference
                query.report = report
                query.save()
                qryCount += 1

        context['uploaded'] = True
        context['queries'] = qryCount
        return render(request, 'judgementapp/upload.html', context)

    if 'resultsFile' in request.FILES:
        f = request.FILES['resultsFile']
        qryCount, docCount, judCount = 0, 0, 0
        for result in f:
            qid, z, docid, rank, score, desc = result.decode().strip().split()

            # check query
            query, created = Query.objects.get_or_create(qId=qid)
            if created:
                query.text = "NA"
                query.save()
                qryCount += 1

            # check document
            document, created = Document.objects.get_or_create(docId=docid)
            if created:
                document.text = "NA"
                document.save()
                docCount += 1

            # check judgement
            judgement = Judgement.objects.filter(
                    query=query.id, document=document.id
            )
            if len(judgement) == 0:
                judgement = Judgement()
                judgement.query = query
                judgement.document = document
                # judgement.relevance = -1
                judgement.save()
                judCount += 1
                
        context['uploaded'] = True
        context['documents'] = docCount
        context['judgements'] = judCount
        context['invalid_queries'] = qryCount

    return render(request, 'judgementapp/upload.html', context)
