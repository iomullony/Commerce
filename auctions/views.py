from django.contrib import messages
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import Auction, Bid, User, Category, Comment, Watchlist


class NewListing(forms.Form):
    title = forms.CharField(label="", required=True, widget=forms.TextInput(attrs={'placeholder': 'Title'}))
    description = forms.CharField(label="", widget=forms.Textarea(attrs={"rows":"3",'placeholder': 'Description', 'max_length': 5000}))
    image = forms.CharField(label="", required=False, widget=forms.TextInput(attrs={'placeholder': 'Image link', 'autocomplete': "off"}))
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

            return redirect('index')
    else:
        form = NewListing()

    return render(request, "auctions/create_listing.html", {
        "form": form
    })


def categories(request):
    categories = Category.objects.all()
    selected_category_id = request.GET.get('category')
    
    if selected_category_id:
        auctions = Auction.objects.filter(category_id=selected_category_id)
        selected_category = Category.objects.get(id=selected_category_id)
    else:
        auctions = Auction.objects.all()
        selected_category = None
    
    return render(request, 'auctions/categories.html', {
        'categories': categories,
        'auctions': auctions,
        'selected_category': selected_category,
    })


def watchlist(request):
    saved_items = request.user.items_saved.select_related('item').all()
    auctions = [item.item for item in saved_items]  # Extracting the actual `Auction` objects

    return render(request, "auctions/watchlist.html", {
        "auctions": auctions
    })


def auction(request, auction_id):
    auction = Auction.objects.get(id=auction_id)
    comments = auction.item_comments.all()
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
        item = Auction.objects.get(id=auction_id)
        highest_bid = item.item_bids.order_by("-money").first()

        # There's no winner
        if highest_bid is None:
            item.winner = request.user # We put that the winner is the seller
            item.save()
            messages.success(request, "Closed successfully! There was no winner.")
        # Winner is the user with the highest bid
        else:
            item.winner = highest_bid.user
            item.save()
            messages.success(request, "Closed successfully! The winner is " + highest_bid.user.username)

        return redirect('auction', auction_id=auction_id)
    else:
        return redirect('index')


def reopen_auction(request, auction_id):
    if request.method == "POST":
        item = Auction.objects.get(id=auction_id)
        item.winner = None
        item.save()
        messages.success(request, "Reopened successfully!")

        return redirect('auction', auction_id=auction_id)
    else:
        return redirect('index')


def bid(request, auction_id):
    if request.method == "POST":
        item = Auction.objects.get(id=auction_id)

        try:
            # Ensure bid is a valid number
            bid = float(request.POST.get('bid'))
            if bid <= 0:
                messages.error(request, "Your bid can't be 0 or less.")
                return redirect('auction', auction_id=auction_id)
        except (TypeError, ValueError):
            messages.error(request, "Invalid bid amount. Please enter a number.")
            return redirect('auction', auction_id=auction_id)

        # Get the highest bid
        highest_bid = item.item_bids.order_by("-money").first()

        if highest_bid is None:
            # Handle the case where there are no bids
            highest_bid = item.starting_bid
        else:
            highest_bid = highest_bid.money

        # Ensure bid is higher than the current highest bid
        if bid <= highest_bid:
            messages.error(request, "Your bid must be higher than the current highest bid.")
            return redirect('auction', auction_id=auction_id)
        
        try:
            # Create bid
            Bid.objects.create(
                user=request.user,
                item=item,
                money=bid
            )

            # Save data in the Auction model too
            item.starting_bid = bid
            item.save()
        except:
            messages.error(request, "Something went wrong.")
    
        messages.success(request, "Your bid was placed successfully!")
        return redirect('auction', auction_id=auction_id)
    else:
        return redirect('index')


def add_comment(request, auction_id):
    if request.method == "POST":
        
        comment = request.POST.get('comment')
        item = Auction.objects.get(id=auction_id)
        
        Comment.objects.create(
            user=request.user,
            item=item,
            comment=comment
        )    
    
        return redirect('auction', auction_id=auction_id)
    else:
        return redirect('index')


def add_to_watchlist(request):
    if request.method == "POST":
        item = Auction.objects.get(id=request.POST.get('id'))
        if(Watchlist.objects.filter(user=request.user, item=item).count() == 0):
            Watchlist.objects.create(
                user=request.user,
                item=item
            )

        return redirect('watchlist')
    else:
        return redirect('index')


def remove_from_watchlist(request):
    if request.method == "POST":
        item = Auction.objects.get(id=request.POST.get('id'))
        Watchlist.objects.get(user=request.user, item=item).delete()

        return redirect('watchlist')
    else:
        return redirect('index')
