from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

from .forms import RegistrationForm, NewRegistrationForm, CustomPasswordChangeForm
from shopproject.settings import LOGIN_REDIRECT_URL
from .models import CustomUser


def register(request):
    # когда отправляем заполненную форму на сервер
    if request.method == 'POST':
        # создаем объект формы с данными из запроса
        form = NewRegistrationForm(request.POST)
        # если форма валидна
        if form.is_valid():
            # создаем объект пользователя без записи в БД
            new_user = form.save(commit=False)
            # хэшируем пароль при помощи set_password
            new_user.set_password(form.cleaned_data['password'])
            # сохраняем пользователя в БД
            new_user.save()
            context = {'title': 'Регистрация завершена', 'new_user': new_user}
            return render(request, template_name='users/registration_done.html', context=context)

    # если метод GET (страница с пустой формой регистрации)
    form = NewRegistrationForm()
    context = {'title': 'Регистрация пользователя', 'register_form': form}
    return render(request, template_name='users/registration.html', context=context)


def log_in(request):
    # создание формы аутенфикации
    form = AuthenticationForm(request, request.POST)
    #проверка формы
    if form.is_valid():
        # полученик логина и пароля из формы
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        # аутентификация пользователя
        # проверка существования пользователя и корректности пароля
        user = authenticate(username=username, password=password)
        if user:
            #авторизация пользователя
            login(request, user)
            # получение дальнейшего маршрута после входа на сайт
            # next - путь, откуда пришел пользователь на страницу входа
            url = request.GET.get('next', LOGIN_REDIRECT_URL)
            return redirect(url)
    context = {'form': form}
    return render(request, template_name='users/login.html', context=context)

@login_required
def log_out(request):
    logout(request)
    return redirect('shop:index')

@login_required
def user_profile(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.user != user:
        raise PermissionDenied()
    context = {'user': user, 'title': 'Информация о пользователе'}
    return render(request, template_name='users/profile.html', context=context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            if not request.user.check_password(old_password):
                messages.error(request, 'Старый пароль не верный')
            else:
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Ваш пароль успешно изменен')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибку')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, template_name='users/change_password.html', context={'form': form})
