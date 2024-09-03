from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create"),
    path("categories", views.categories, name="categories"),
    path("watchlist", views.watchlist, name="watchlist"),
    path('auction/<int:auction_id>/', views.auction, name='auction'),
    path("close_auction/<int:auction_id>/", views.close_auction, name="close_auction"),
    path("bid/<int:auction_id>/", views.bid, name="bid"),
    path("add_to_watchlist", views.add_to_watchlist, name="add_to_watchlist"),
    path("remove_from_watchlist", views.remove_from_watchlist, name="remove_from_watchlist"),
    path("add_comment/<int:auction_id>/", views.add_comment, name="add_comment")
]
