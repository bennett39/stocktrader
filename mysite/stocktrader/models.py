from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Profile(models.Model):
    """ Extend built-in Django User model with cash value """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    cash = models.DecimalField(
        default=10000,
        max_digits=7,
        decimal_places=2,
    )

    def __str__(self):
        return f'{self.user.username}'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """ When a new user is created, also create a new Profile """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """ Save the OneToOne linked Profile on the User instance """
    instance.profile.save()


class Stock(models.Model):
    symbol = models.CharField(
        max_length=10,
        unique=True,
    )
    name = models.CharField(
        max_length=80,
    )

    def __str__(self):
        return f'{self.symbol} - {self.name[:10]}'


class Transaction(models.Model):
    """ Stores an append-only list of transactions. """
    user = models.ForeignKey(
        'Profile',
        on_delete=models.CASCADE,
        related_name='transactions',
    )
    stock = models.ForeignKey(
        'Stock',
        on_delete=models.CASCADE,
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
    )
    time = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        buy_sell = 'BUY' if self.quantity > 0 else 'SELL'
        return f'{self.user} - {buy_sell} {self.stock}'

