from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from nyaa_django import models

# Create your views here.


def main(request):
    page = request.GET.get('page', 1)
    torrents = models.Torrents.objects.all().order_by('-torrent_id')[:20*10]
    paginator = Paginator(torrents, 20)
    try:
        torrents = paginator.page(page)
    except PageNotAnInteger:
        torrents = paginator.page(1)
    except EmptyPage:
        torrents = paginator.page(paginator.num_pages)
    return render(request,"home.html",{"torrents":torrents})


def index(request):
    return render(request,"index.html")