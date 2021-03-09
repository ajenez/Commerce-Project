from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django import forms
from django.forms import ModelForm




class User(AbstractUser):
    pass


# auction listings, bids, comments, and auction categories

category_choices = [
    ('Beauty', 'Beauty'),
    ('Clothing', 'Clothing'),
    ('Education', 'Education'),
    ('Electronics', 'Electronics'),
    ('Furniture', 'Furniture'),
    ('Home', 'Home'),
    ('Sports', 'Sports'),
    ('Toys', 'Toys'),
]


class Listing(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=200)
    starting_bid = models.DecimalField(max_digits=7, decimal_places=2, validators = [MinValueValidator(0.01)])
    image = models.ImageField(upload_to='listing_images/', max_length=255, null=True, blank=True)
    category = models.CharField(max_length=15, choices=category_choices, default=None, null=True, blank=True)
    isactive = models.BooleanField(default=True)
    createtime = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return self.title

class ListingForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ListingForm, self).__init__(*args, **kwargs)
        self.fields['starting_bid'].widget.attrs['min'] = 0.01
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'image', 'category']
        widgets = {
          'description': forms.Textarea(attrs={'rows':5, 'cols':30, 'style':'resize:none;'}),
        }

class IsActiveForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['isactive']

class Comment(models.Model):
    id_of_listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=300)
    createtime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.comment

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']


class Bid(models.Model):
    id_of_listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User,on_delete=models.CASCADE)
    bid = models.DecimalField(max_digits=7, decimal_places=2, validators = [MinValueValidator(0.01)])
    timestamp = models.DateTimeField(auto_now=True)


class BidForm(ModelForm):

    class Meta:
        model = Bid
        fields = ['bid']


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_of_listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    addtime = models.DateTimeField()


class WatchListForm(ModelForm):
    class Meta:
        model = Watchlist
        fields = []



"""
class CreateForm(forms.Form):
    title = forms.CharField(label="title", max_length=5)
    description = forms.CharField(label="description", max_length=200)
    startingbid = forms.DecimalField(max_digits=7, decimal_places=2, validators = [MinValueValidator(0.01)])
    # image =
    category = forms.ChoiceField()
"""