from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import Auction, User, Category, Comment, Watchlist


class NewListing(forms.Form):
    title = forms.CharField(label="", required=True, widget=forms.TextInput(attrs={'placeholder': 'Title'}))
    description = forms.CharField(label="", widget=forms.Textarea(attrs={"rows":"3",'placeholder': 'Description', 'max_length': 5000}))
    image = forms.CharField(label="", required=False, widget=forms.TextInput(attrs={'placeholder': 'Image link'}))
    starting_bid = forms.DecimalField(label="", required=True, min_value=0, decimal_places=2, widget=forms.NumberInput(attrs={'placeholder': 'Starting Bid'}))
    category = forms.ChoiceField(label="", required=True, choices=[])

    def __init__(self, *args, **kwargs):
        super(NewListing, self).__init__(*args, **kwargs)
        self.fields['category'].choices = [(category.id, category.name) for category in Category.objects.all()]


def index(request):
    return render(request, "auctions/index.html", {
        "auctions": Auction.objects.all()
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    

# put for auction a new item
def create_listing(request):

    if request.method == "POST":
        form = NewListing(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            image = form.cleaned_data["image"]
            starting_bid = form.cleaned_data["starting_bid"]
            category_id = form.cleaned_data["category"]

            category = Category.objects.get(id=category_id)

            Auction.objects.create(
                seller=request.user,
                title=title,
                description=description,
                image=image,
                starting_bid=starting_bid,
                category=category
            )

            return render(request, "auctions/index.html", {
                "auctions": Auction.objects.all()
            })
    else:
        form = NewListing()

    return render(request, "auctions/create_listing.html", {
        "form": form
    })


def categories(request):
    categories = Category.objects.prefetch_related('auction_set').all()
    return render(request, "auctions/categories.html", {
            "categories": categories
    })


def watchlist(request):
    return render(request, "auctions/watchlist.html", {
        "auctions": Watchlist.objects.filter(user=request.user)
    })


def auction(request, auction_id):
    auction = Auction.objects.get(id=auction_id)
    comments = Comment.objects.filter(item=auction)
    is_seller = auction.seller == request.user
    in_watchlist = Watchlist.objects.filter(item=auction)
    return render(request, 'auctions/auction.html', {
        'auction': auction,
        'comments': comments,
        'is_seller': is_seller,
        'in_watchlist': in_watchlist
    })


def close_auction(request, auction_id):
    if request.method == "POST":
        return HttpResponse("close auction")
    else:
        return render(request, "auctions/index.html", {
            "auctions": Auction.objects.all()
        })



def bid(request, auction_id):
    if request.method == "POST":
        return HttpResponse("bid")
    else:
        return render(request, "auctions/index.html", {
            "auctions": Auction.objects.all()
        })


def add_comment(request, auction_id):
    if request.method == "POST":
        return HttpResponse("add comment")
    else:
        return render(request, "auctions/index.html", {
            "auctions": Auction.objects.all()
        })


def add_to_watchlist(request):
    if request.method == "POST":
        item = Auction.objects.get(id=request.POST.get('id'))
        if(Watchlist.objects.filter(user=request.user, item=item).count() == 0):
            Watchlist.objects.create(
                user=request.user,
                item=item
            )

        return render(request, "auctions/watchlist.html", {
            "auctions": Watchlist.objects.filter(user=request.user)
        })
    else:
        return render(request, "auctions/index.html", {
            "auctions": Auction.objects.all()
        })


def remove_from_watchlist(request):
    if request.method == "POST":
        item = Auction.objects.get(id=request.POST.get('id'))
        Watchlist.objects.get(user=request.user, item=item).delete()

        return render(request, "auctions/watchlist.html", {
            "auctions": Watchlist.objects.filter(user=request.user)
        })
    else:
        return render(request, "auctions/index.html", {
            "auctions": Auction.objects.all()
        })
