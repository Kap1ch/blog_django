from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
# Create your views here.
from taggit.models import Tag

from .forms import EmailPostForm, CommentForm, LoginForm, PostForm, PostPointForm, UserEditForm, UserCreateForm, \
    SearchForm
from .models import Post, PostPoint, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'blog/account/login.html', {'form': form})


@login_required
def post_list(request, tag_slug=None):
    search_form = SearchForm()
    query = None

    if 'query' in request.GET:
        search_form = SearchForm(request.GET)
        if search_form.is_valid():
            query = search_form.cleaned_data['query']
            try:
                object_list = Post.objects.filter(title__contains=query, status='published')
            except:
                object_list = None
    else:
        object_list = Post.objects.filter(status='published')
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'page': page,
                                                   'posts': posts,
                                                   'tag': tag,
                                                   'search_form': search_form})


class PostListView(ListView):
    queryset = Post.objects.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, post, post_id):
    post_object = get_object_or_404(Post, slug=post, status='published',
                                    publish__year=year,
                                    publish__month=month,
                                    publish__day=day,
                                    id=post_id)
    post_points = PostPoint.objects.filter(post=post_object)
    comments = post_object.comment.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            cd = comment_form.cleaned_data
            new_comment = Comment(post=post_object, name=cd['name'], email=cd['email'], body=cd['comment'])
            new_comment.save()
    else:
        comment_form = CommentForm()
    post_tags_ids = post_object.tags.values_list('id', flat=True)
    similar_posts = Post.objects.filter(tags__in=post_tags_ids, status='published').exclude(id=post_object.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(request, 'blog/post/detail.html', {'post': post_object,
                                                     'post_points': post_points,
                                                     'comments': comments,
                                                     'new_comment': new_comment,
                                                     'comment_form': comment_form,
                                                     'similar_posts': similar_posts
                                                     })


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments:{}'.format(post.title, post_url, cd['name'], cd['comment'])
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html',
                  {'post': post, 'form': form, 'sent': sent})


@login_required
def dashboard(request):
    return render(request, 'blog/account/dashboard.html', )


@login_required
def dashboard(request):
    user = request.user
    posts_pub = Post.objects.filter(author=user, status='published')
    posts_draft = Post.objects.filter(author=user, status='draft')
    return render(request, 'blog/account/dashboard.html', {'posts_pub': posts_pub,
                                                           'posts_draft': posts_draft})


@login_required
def post_add(request):
    user = request.user
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = user
            post.save()
            for tag in form.cleaned_data['tags']:
                post.tags.add(tag)
    else:
        form = PostForm()

    return render(request, 'blog/account/post_add.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post_edit_form = PostForm(instance=post)
    if request.method == 'POST':
        post_edit_form = PostForm(request.POST, request.FILES, instance=post)
        if post_edit_form.is_valid():
            post_edit_form.save()
    return render(request,
                  'blog/account/post_edit.html',
                  {'form': post_edit_form,
                   'post': post})


@login_required
def post_delete(request, post_id):
    try:
        post = get_object_or_404(Post,
                                 id=post_id)
        post.delete()
        return redirect('myblog:dashboard')
    except Post.DoesNotExist:
        return redirect('myblog:dashboard')


@login_required
def post_point_list(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    post_points = PostPoint.objects.filter(
        post=post)
    return render(request,
                  'blog/account/post_points.html',
                  {'post': post,
                   'post_points': post_points})


@login_required
def post_point_add(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostPointForm()

    if request.method == 'POST':
        form = PostPointForm(request.POST,
                             request.FILES)
        if form.is_valid():
            post_point = form.save(commit=False)
            post_point.post = post
            post_point.save()

    return render(request, 'blog/account/post_point_add.html', {'form': form,
                                                                'post': post})


@login_required
def post_point_edit(request, post_point_id):
    post_point = get_object_or_404(PostPoint, id=post_point_id)
    post = get_object_or_404(Post, id=post_point.post.id)
    post_point_edit_form = PostPointForm(instance=post_point)
    if request.method == 'POST':
        post_point_edit_form = PostPointForm(request.POST, request.FILES,
                                             instance=post_point)
        if post_point_edit_form.is_valid():
            post_point_edit_form.save()
    return render(request, 'blog/account/post_point_edit.html',
                  {'form': post_point_edit_form,
                   'post_point': post_point,
                   'post': post})


@login_required
def post_point_delete(request, post_point_id):
    try:
        post_point = get_object_or_404(PostPoint,
                                       id=post_point_id)
        post_point.delete()
        return redirect('myblog:post_point_list', post_id=post_point.post.id)
    except PostPoint.DoesNotExist:
        return redirect('myblog:post_list')


def sign_up(request):
    user_form = UserCreateForm()
    if request.method == 'POST':
        user_form = UserCreateForm(request.POST)
        if user_form.is_valid():
            new_user = User.objects.create_user(**user_form.cleaned_data)
            new_user.save()
            login(request, authenticate(username=user_form.cleaned_data['username'],
                                        password=user_form.cleaned_data['password']))
            return redirect('myblog:post_list')
    return render(request, 'registration/sign_up.html', {'user_form': user_form})


@login_required
def edit_profile(request):
    user_form = UserEditForm(
        instance=request.user)
    if request.method == 'POST':
        user_form = UserEditForm(
            request.POST,
            instance=request.user)
        if user_form.is_valid():
            user_form.save()
    return render(request,
                  'blog/account/profile.html',
                  {'user_form': user_form})


def add_to_favourite(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.favourite.add(request.user)
    return redirect('myblog:post_detail', year=post.publish.year,
                    month=post.publish.month,
                    day=post.publish.day,
                    post=post.slug,
                    post_id=post.id)


def delete_from_favourite(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.favourite.remove(request.user)
    return redirect('myblog:post_detail', year=post.publish.year,
                    month=post.publish.month,
                    day=post.publish.day,
                    post=post.slug,
                    post_id=post.id)


def delete_from_favourite_in_dashboard(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.favourite.remove(request.user)
    return redirect('myblog:favourite_posts')


def favourite_posts(request):
    return render(request, 'blog/account/fav_posts.html', {})
