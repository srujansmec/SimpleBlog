from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponse,HttpResponseRedirect,Http404
from .models import posts
from .forms import PostForm
from django.utils import timezone
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from urllib import quote_plus
from django.db.models import Q

# Create your views here.
def post_create(request):
    #if request.user.is_authenticated():
    if not request.user.is_staff or not request.user.is_superuser:
        return Http404
    form = PostForm(request.POST or None,request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        print form.cleaned_data.get("title")
        instance.save()
        messages.success(request,"Successfully Created New Post")
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        "title" : "create",
        "form" : form
    }
    return render(request,"post_form.html",context)

def post_detail(request,slug = None):
    instance = get_object_or_404(posts,slug=slug)
    if instance.draft or instance.publish > timezone.now().date():
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404

    share_string = quote_plus(instance.content)
    context = {
        "instance" : instance,
        "sharestring" : share_string,
    }
    return render(request,"post_detail.html",context)

def post_list(request):
    today = timezone.now().date()
    queryset_list = posts.objects.active() #filter(draft=False).filter(publish__lte=timezone.now())
    if request.user.is_staff or request.user.is_superuser:
        queryset_list = posts.objects.all()

    query =  request.GET.get('q')
    if query:
        queryset_list = posts.objects.filter(
             Q(title__icontains = query)|
             Q(content__icontains = query) |
             Q(user__first_name__icontains = query) |
             Q(user__last_name__icontains = query)).distinct()
    paginator = Paginator(queryset_list, 2)  # Show 25 contacts per page
    page_request_var = 'page'
    page = request.GET.get( page_request_var )
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)
    context ={
        "object_list" : queryset,
        "title" : "All Posts",
        "page_request_var" :  page_request_var ,
        "today" : today,
        "query" : query,

    }
    return render(request,"post_list.html",context)



def post_update(request,slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404

    instance = get_object_or_404(posts,slug=slug)
    form = PostForm(request.POST or None,request.FILES or None,instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user  =  request.user
        instance.save()
        messages.success(request,"Successfully Updated")
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        "title" : instance.title,
        "instance" : instance,
        "form":form
    }
    return render(request,"post_form.html",context)

def post_delete(request,slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        return Http404
    instance = get_object_or_404(posts, slug=slug)
    instance.delete()
    messages.success(request, "Successfully Deleted")
    return redirect("blog:list")