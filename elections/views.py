from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Candidate, Poll, Choice
from datetime import datetime
from django.db.models import Sum


def index(request):
    candidates = Candidate.objects.all()
    context = {"candidates": candidates}
    return render(request, "elections/index.html", context)


def candidates(request, name):
    candidate = get_object_or_404(Candidate, name=name)
    # try:
    #     candidate = Candidate.objects.get(name=name)
    # except Candidate.DoesNotExist:
    #     raise Http404
    return HttpResponse(candidate.name)


def areas(request, area):
    today = datetime.now()
    try:
        poll = Poll.objects.get(area=area, start_date__lte=today, end_date__gte=today)
        candidates = Candidate.objects.filter(area=area)
    except Poll.DoesNotExist:
        poll = None
        candidates = None

    context = {"candidates": candidates, "area": area, "poll": poll}
    return render(request, "elections/area.html", context)


def polls(request, poll_pk):
    poll = Poll.objects.get(pk=poll_pk)
    selection = request.POST["choice"]

    try:
        choice = Choice.objects.get(poll_id=poll_pk, candidate_id=selection)
        choice.votes += 1
        choice.save()
    except Choice.DoesNotExist:
        choice = Choice(poll_id=poll_pk, candidate_id=selection, votes=1)
        choice.save()
    return HttpResponseRedirect(f"/areas/{poll.area}/results")


def results(request, area):
    candidates = Candidate.objects.filter(area=area)
    polls = Poll.objects.filter(area=area)
    poll_results = []
    for poll in polls:
        result = {}
        result["start_date"] = poll.start_date
        result["end_date"] = poll.end_date
        total_votes = Choice.objects.filter(poll_id=poll.pk).aggregate(Sum("votes"))
        result["total_votes"] = total_votes["votes__sum"]
        rates = []
        for candidate in candidates:
            try:
                choice = Choice.objects.get(poll_id=poll.pk, candidate_id=candidate.pk)
                rates.append(round(choice.votes * 100 / result["total_votes"], 2))
            except Choice.DoesNotExist:
                rates.append(0)
        result["rates"] = rates
        poll_results.append(result)

    context = {
        "area": area,
        "candidates": candidates,
        "poll_results": poll_results,
    }
    return render(request, "elections/result.html", context)
