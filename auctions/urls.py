from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing/<int:pk>", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("create/", views.create, name="create"),
    path("beauty", views.beauty, name="beauty"),
    path("clothing", views.clothing, name="clothing"),
    path("education", views.education, name="education"),
    path("electronics", views.electronics, name="electronics"),
    path("furniture", views.furniture, name="furniture"),
    path("home", views.home, name="home"),
    path("sports", views.sports, name="sports"),
    path("toys", views.toys, name="toys"),
]
