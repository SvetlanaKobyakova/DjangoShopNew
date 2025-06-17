from django.shortcuts import render
from decimal import Decimal

from shop.models import Product
from .models import CartUser, CartItem
from shopproject.settings import CART_SESSION_ID


class Cart:
    """
    Класс корзины для анонимного пользователя (не авторизованного)
    """
    def __init__(self, request):
        # получаем текущую сессию
        self.session = request.session
        # получаем текущего пользователя
        self.user = request.user
        # получаем корзину из сессии или создаем новую
        cart = self.session.get(CART_SESSION_ID)
        if not cart:
            cart = self.session[CART_SESSION_ID] = {}
        self.cart = cart

    # сохранение изменений в сессии
    def save(self):
        self.session.modified = True

    # создание копии корзины
    def copy(self):
        return self.cart.copy()


