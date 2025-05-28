from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib import messages

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario registrado exitosamente. Ahora puedes iniciar sesión.')
            return redirect('login')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Bienvenido, {username}!')
            return redirect('landing:home')
        else:
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('login')

def profile_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Debes iniciar sesión para ver tu perfil.')
        return redirect('users:login')
    
    return render(request, 'users/profile.html', {'user': request.user})

def dashboard_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Debes iniciar sesión para acceder al panel de control.')
        return redirect('users:login')
    
    return render(request, 'users/dashboard.html', {'user': request.user})
