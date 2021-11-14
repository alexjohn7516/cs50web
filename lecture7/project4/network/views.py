from typing import OrderedDict
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

import json
import datetime

from .models import User, Profile, Posts, LikedPosts

#! For Future Reference Read Below
# When sending context into a django template from a view insert it into
# a Dictionary with key value pairs so if someone else sees the code or
# you need to go back and reference it you know how the model looks
# ? This would make my functions larger Write a doc type note above each
# ? Function explaining the model being used?


def order_posts(posts):
    ordered_posts = []
    for post in posts:
        ordered_posts.append(post)
    length_ = len(ordered_posts)
    for i in range(length_):
        for j in range(length_-i-1):
            if (ordered_posts[j].timestamp < ordered_posts[j+1].timestamp):
                temp = ordered_posts[j]
                ordered_posts[j] = ordered_posts[j+1]
                ordered_posts[j+1] = temp

    return ordered_posts


def index(request):
    # load all the posts here and send it to the template
    all_posts = Posts.objects.all()
    ordered_posts = order_posts(all_posts)
    # TODO create an ordering algorithm to order posts newests to oldests

    return render(request, "network/index.html",
                  {
                      "posts": ordered_posts
                  })


@ensure_csrf_cookie
@login_required
def edit_post(request, id):
    try:
        post = Posts.objects.get(post_id=id)
        if request.user != post.user:
            return JsonResponse({"error": "Not Post Creator"})
    except:
        return JsonResponse({"error": "Post not found"}, status=404)

    if request.method == "GET":
        return JsonResponse(post.serialize())

    elif request.method == "PUT":
        # data = request.body
        # post.content = data['content']
        # this could also be this ^ becuase the content was JSON.stringified upon request
        data = json.loads(request.body)
        post.content = data.get('content')
        post.timestamp = datetime.datetime.now()
        post.save()
        return HttpResponse(status=202)
    else:
        return JsonResponse({
            "error": "GET or PUT response Required"
        })


@ensure_csrf_cookie
@login_required
def new_post(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status="400")
    content = request.POST.get("content")
    user = request.user

    # # create post in data base to be fetched
    post = Posts.objects.create(content=content, user=user)
    post.save()
    posts = Posts.objects.all()
    return render(request, "network/index.html", {
        "posts": posts
    })


@ensure_csrf_cookie
@login_required
def like_post(request, id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status="400")

    try:
        post = Posts.objects.get(post_id=id)
    except:
        return JsonResponse({"error": "Post Not Found"})

    try:
        liked = LikedPosts.objects.get(user=request.user, post=post)
        liked.delete()
        post.likes -= 1
        post.liked.remove(request.user)
        post.save()
        return HttpResponse(status=204)
    except:
        new_like = LikedPosts.objects.create(
            user=request.user, post=post)
        new_like.save()
        post.likes += 1
        post.liked.add(request.user)
        post.save()
        return HttpResponse(status=202)


def profile(request, username):
    user = User.objects.filter(username=username).get()
    profile = Profile.objects.filter(name=username).get()
    # new accounts will have no posts
    try:
        posts = Posts.objects.filter(user=user)
        ordered_posts = order_posts(posts)
    except:
        posts = None
    return render(request, "network/profile.html", {
        "profile": profile,
        "posts": ordered_posts,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"].lower()
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user and profile
        try:
            user = User.objects.create_user(username, email, password)
            user.save()

            # create a profile upon creation of user
            profile = Profile.objects.create(
                name=user.username,
                user=user)
            profile.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
