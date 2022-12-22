from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Content, Collection


@login_required
def user_view(request, username):
    current_user = request.user
    if User.objects.filter(username=username).exists():
        target_user = User.objects.filter(username=username).first()
    else:
        return redirect('')

    if current_user == target_user:
        pass

    user_seen_content = Content.objects.filter(seen_by=target_user).order_by('-time_retrieved')[:20]
    user_liked_content = Content.objects.filter(liked_by=target_user).order_by('-time_retrieved')[:20]
    user_collections = Collection.objects.filter(owners=target_user).order_by('name')[:20]

    context = {
        'target_user': target_user,
        'seen_content': user_seen_content,
        'liked_content': user_liked_content,
        'collections': user_collections
    }

    return render(request, 'User/user.html', context=context)


@login_required
def user_seen_view(request, username):
    current_user = request.user
    if User.objects.filter(username=username).exists():
        target_user = User.objects.filter(username=username).first()
    else:
        return redirect('')

    if current_user == target_user:
        pass

    user_seen_content = Content.objects.filter(seen_by=target_user).order_by('-time_retrieved')

    context = {
        'target_user': target_user,
        'seen_content': user_seen_content
    }

    return render(request, 'User/user_seen.html', context=context)


@login_required
def user_liked_view(request, username):
    current_user = request.user
    if User.objects.filter(username=username).exists():
        target_user = User.objects.filter(username=username).first()
    else:
        return redirect('')

    if current_user == target_user:
        pass

    user_liked_content = Content.objects.filter(liked_by=target_user).order_by('-time_retrieved')

    context = {
        'target_user': target_user,
        'liked_content': user_liked_content
    }

    return render(request, 'User/user_liked.html', context=context)


@login_required
def user_collections_view(request, username):
    current_user = request.user
    if User.objects.filter(username=username).exists():
        target_user = User.objects.filter(username=username).first()
    else:
        return redirect('')

    if current_user == target_user:
        pass

    user_collections = Collection.objects.filter(owners=target_user).order_by('name')

    if len(user_collections) > 20:
        is_paginated = True
    else:
        is_paginated = False

    paginator = Paginator(user_collections, 20)

    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)

    context = {
        'target_user': target_user,
        'collections': user_collections,
        'page_obj': page_object,
        'is_paginated': is_paginated
    }

    return render(request, 'User/user_collections.html', context=context)


