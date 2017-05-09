from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from nyaa_django import models, utils, forms
# Create your views here.


def main(request):
    page = request.GET.get('page', 1)
    search = utils.SearchQuery(request.GET)
    sort = utils.SortQuery(request.GET)
    sec = search.construct()
    src = sort.construct()
    if sec:
        dbq = models.Torrent.objects.filter(sec)
    else:
        dbq = models.Torrent.objects.all()
    if src:
        dbs = dbq.order_by(src)
    else:
        dbs = dbq.order_by('-id')
    paginator = Paginator(dbs, search.max)
    try:
        torrents = paginator.page(page)
    except PageNotAnInteger:
        torrents = paginator.page(1)
    except EmptyPage:
        torrents = paginator.page(paginator.num_pages)
    return render(request,"home.html",{
                            "torrents":torrents,
                            "search":search,
                            "sort":sort})

def view(request, tid):
    torrent = models.Torrent.objects.get(id=int(tid))
    return render(request,"view.html",{"torrent":torrent})

def upload(request):
    if request.method == "POST":
        form = forms.UploadForm(request.POST, request.FILES)
        if form.is_valid():
            # PROCESSING CODE #
            return HttpResponseRedirect('/home')
    else:
        form = forms.UploadForm()
    return render_to_response('upload.html',{'form':form})

def index(request):
    return HttpResponseRedirect('/home')