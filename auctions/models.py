from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


# Category for an object
class Category(models.Model):
    name = models.CharField(max_length=60)


# Seller
# Item's name
# Description
# Image
# Starting Bid
# Category
class Auction(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=5000)
    image = models.CharField(max_length=20000, blank=True, null=True)
    starting_bid = models.DecimalField(decimal_places=2, max_digits=12)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.title} from {self.seller.username}"


# User
# Bidding item
# Bid money
class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Auction, on_delete=models.CASCADE)
    money = models.DecimalField(decimal_places=2, max_digits=12)

    def __str__(self):
        return f"{self.user.username} bid {self.money}€ on {self.item.title}"

 
# User
# Item
# Comment
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Auction, on_delete=models.CASCADE)
    comment = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.item.title} {self.user.username}: {self.comment}"
    
 
# User
# Item
class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Auction, on_delete=models.CASCADE)
