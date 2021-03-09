from django.contrib import admin

from .models import Listing, User, Comment, Bid, Watchlist

# Register your models here.

class ListingAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator', 'title', 'description', 'image', 'starting_bid', 'category', 'isactive', 'createtime')

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_of_listing', 'username', 'comment', 'createtime')

class BidAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_of_listing', 'user_id', 'bid', 'timestamp')

class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'id_of_listing', 'addtime')

admin.site.register(Listing, ListingAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Watchlist, WatchlistAdmin)