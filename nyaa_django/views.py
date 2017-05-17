from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django import http
from nyaa_django import models, utils, forms
from datetime import datetime
# Create your views here.


def main(request):
    page = request.GET.get('page', 1)
    search = utils.SearchQuery(request.GET)
    sort = utils.SortQuery(request.GET)
    dbq = search.dbapply(models.Torrents.objects)
    dbs = sort.dbapply(dbq)
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
    torrent = models.Torrents.objects.get(id=int(tid))
    return render(request,"view.html",{"torrent":torrent})

def upload(request):
    if request.method == "POST":
        form = forms.UploadForm(request.POST, request.FILES)
        user = request.user
        if form.is_valid() and user.is_authenticated:
            dat = request.FILES["file"].read()
            cat, subcat = utils.parse_cats(form.category)
            pars = {
                "category_id":cat,
                "sub_category_id":subcat,
                "downloads":0,
                "stardom":0,
                "website_link":form.website,
                "description":form.description,
                "uploader_id":user.id
            }
            try:
                tinfo = utils.TorrentInfo(dat)
            except ValueError:
                return http.HttpResponseBadRequest(
                    "Not a valid torrent file!", "text/plain")
            tmod = tinfo.get_model(models.Torrents,**pars)
            tmod.save()
            return utils.HttpResponseSeeOther('/view/{}'.format(tmod.id))
        else:
            return http.HttpResponseBadRequest(
                "Invalid arguments or not logged in.", "text/plain")
    else:
        form = forms.UploadForm()
    return render(request,'upload.html',{'form':form})

def index(request):
    return redirect('/home')