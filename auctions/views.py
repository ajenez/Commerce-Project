from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Max

from .models import User, Listing, ListingForm, Comment, CommentForm, Bid, BidForm, IsActiveForm, Watchlist, WatchListForm
from commerce import settings


def index(request):
    listings_unsorted = Listing.objects.filter(isactive=True)
    listings = sorted(listings_unsorted, key=lambda x: x.createtime, reverse=True)

    return render(request, "auctions/index.html",{
        "listings":listings,
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

def listing(request, pk):
    #Remove from watchlist and handle anonymous user
    title_of_watch = Listing.objects.filter(id=pk)
    nouser = str(request.user)
    if nouser == "AnonymousUser":
        forwatch = Watchlist.objects.filter(user=None)
    if nouser != "AnonymousUser":
        forwatch = Watchlist.objects.filter(user=request.user)

    forwatchlist = []
    for x in forwatch:
        forwatchlist.append((x.id_of_listing).title)

    if Listing.objects.filter(id=pk).values('title')[0].get('title') in forwatchlist:
        remove = True
    else:
        remove = False

    #display proper bid

    bidnumber = Bid.objects.filter(id_of_listing=pk).count()
    active = True
    firstbid = Listing.objects.get(id=pk).starting_bid
    if Bid.objects.filter(id_of_listing=pk).aggregate(Max('bid'))['bid__max']:
        topbid = float("%.2f" % Bid.objects.filter(id_of_listing=pk).aggregate(Max('bid'))['bid__max'])
        topbidder = Bid.objects.get(bid=topbid).user_id
        bid = 0
        if firstbid > topbid:
            bid = firstbid
            
        else:
            bid = topbid
            newbid = Listing.objects.get(id=pk)
            newbid.starting_bid = topbid
            newbid.save()
            
        overbid = "%.2f" %(bid+.01)
        bid = "%.2f" % bid

        you = ""
        if topbidder == request.user and Listing.objects.get(id=pk).isactive == True:
            you = "You are the top bidder"
            active = Listing.objects.get(id=pk).isactive
            print(active)
        if topbidder == request.user and Listing.objects.get(id=pk).isactive == False:
            you = "You won this auction!"
            active = Listing.objects.get(id=pk).isactive
            print(active)
    else:
        bid=Listing.objects.get(id=pk).starting_bid
        overbid = "%.2f" %(float(bid)+.01)
        you=""
    
# handle post requests 

    listing_fields = Listing.objects.get(id=pk)
    unsorted_comments = Comment.objects.filter(id_of_listing=pk)
    comments = sorted(unsorted_comments, key=lambda x: x.createtime, reverse=True)
    if request.method == "POST":

        if 'bid' in request.POST:
            bidform = BidForm(request.POST)
            if bidform.is_valid():
                obj = bidform.save(commit=False)
                obj.id_of_listing = Listing.objects.get(id=pk)
                obj.user_id = request.user
                obj.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


        if 'comment' in request.POST:
            commentform = CommentForm(request.POST)
            if commentform.is_valid():
                obj = commentform.save(commit=False)
                obj.username = request.user
                obj.id_of_listing = Listing.objects.get(id=pk)
                obj.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if 'changeactive' in request.POST:
            isactiveform = IsActiveForm(request.POST)
            if isactiveform.is_valid():
                obj = isactiveform.save(commit=False)
                obj.id = Listing.objects.get(id=pk).id
                obj.creator_id = request.user
                obj.starting_bid = bid
                obj.title = Listing.objects.get(id=pk).title
                obj.description = Listing.objects.get(id=pk).description
                obj.image = Listing.objects.get(id=pk).image
                obj.category = Listing.objects.get(id=pk).category
                obj.isactive = False
                obj.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if 'addtowatchlist' in request.POST:
            watchlistform = WatchListForm(request.POST)
            if watchlistform.is_valid():
                obj = watchlistform.save(commit=False)
                obj.user = request.user
                obj.id_of_listing = Listing.objects.get(id=pk)
                obj.addtime = Listing.objects.get(id=pk).createtime
                obj.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if 'removefromwatchlist' in request.POST:
            title_of_listing = Listing.objects.get(id=pk)
            Watchlist.objects.filter(id_of_listing=title_of_listing).delete()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


    else:
        commentform = CommentForm()
        bidform = BidForm()
    return render(request, "auctions/listing.html",{
        'comments':comments,
        'commentform':commentform,
        'bidform':bidform,
        "title":listing_fields.title,
        "description":listing_fields.description,
        "price":listing_fields.starting_bid,
        "creator":listing_fields.creator,
        "category":listing_fields.category,
        "image":listing_fields.image,
        "bid":bid,
        "bidnumber":bidnumber,
        "you":you,
        "remove":remove,
        "active":active,
        "overbid":overbid
    })


def categories(request):
    print(categories)
    return render(request, "auctions/categories.html",{
    })

def beauty(request):
    category = "Beauty"
    listings_unsorted = Listing.objects.filter(category="Beauty", isactive=True)
    listings = sorted(listings_unsorted, key=lambda x: x.createtime, reverse=True)
    return render(request, "auctions/category.html",{
        "listings":listings,
        "category":category,
    })
def clothing(request):
    category = "Clothing"
    listings_unsorted = Listing.objects.filter(category="Clothing", isactive=True)
    listings = sorted(listings_unsorted, key=lambda x: x.createtime, reverse=True)
    return render(request, "auctions/category.html",{
        "listings":listings,
        "category":category,
    })
def education(request):
    category = "Education"
    listings_unsorted = Listing.objects.filter(category="Education", isactive=True)
    listings = sorted(listings_unsorted, key=lambda x: x.createtime, reverse=True)
    return render(request, "auctions/category.html",{
        "listings":listings,
        "category":category,
    })
def electronics(request):
    category = "Electronics"
    listings_unsorted = Listing.objects.filter(category="Electronics", isactive=True)
    listings = sorted(listings_unsorted, key=lambda x: x.createtime, reverse=True)
    return render(request, "auctions/category.html",{
        "listings":listings,
        "category":category,
    })
def furniture(request):
    category = "Furniture"
    listings_unsorted = Listing.objects.filter(category="Furniture", isactive=True)
    listings = sorted(listings_unsorted, key=lambda x: x.createtime, reverse=True)
    return render(request, "auctions/category.html",{
        "listings":listings,
        "category":category,
    })
def home(request):
    category = "Home"
    listings_unsorted = Listing.objects.filter(category="Home", isactive=True)
    listings = sorted(listings_unsorted, key=lambda x: x.createtime, reverse=True)
    return render(request, "auctions/category.html",{
        "listings":listings,
        "category":category,
    })
def sports(request):
    category = "Sports"
    listings_unsorted = Listing.objects.filter(category="Sports", isactive=True)
    listings = sorted(listings_unsorted, key=lambda x: x.createtime, reverse=True)
    return render(request, "auctions/category.html",{
        "listings":listings,
        "category":category,
    })
def toys(request):
    category = "Toys"
    listings_unsorted = Listing.objects.filter(category="Toys", isactive=True)
    listings = sorted(listings_unsorted, key=lambda x: x.createtime, reverse=True)
    return render(request, "auctions/category.html",{
        "listings":listings,
        "category":category,
    })




def watchlist(request):
    listings_unsorted = Watchlist.objects.filter(user_id=request.user)
    print(listings_unsorted)

    l = []
    for x in listings_unsorted:
        l.append(x.id_of_listing)
        print(l)

    listings_unsorted = Listing.objects.filter(title__in = l)
    
    listings = sorted(listings_unsorted, key=lambda x: x.createtime, reverse=True)
    return render(request, "auctions/watchlist.html",{
        "listings":listings,
    })

def create(request):
    print("Here")
    if request.method == "POST":
            createform = ListingForm(request.POST, request.FILES)
            if createform.is_valid():
                obj = createform.save(commit=False)
                obj.creator = request.user
                obj.save()
                return HttpResponseRedirect('/')
    else:
        createform = ListingForm()
    return render(request, "auctions/create.html",{
        'createform':createform,
    })            