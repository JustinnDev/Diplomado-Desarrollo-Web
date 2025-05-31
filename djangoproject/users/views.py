from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario registrado exitosamente. Ahora puedes iniciar sesión.')
            return redirect('users:login')
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
            return redirect('landing:index')
        else:
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('landing:index')

def profile_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Debes iniciar sesión para ver tu perfil.')
        return redirect('users:login')
    
    return render(request, 'users/profile.html', {'user': request.user})

def dashboard_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Debes iniciar sesión para acceder al panel de control.')
        return redirect('users:login')
    
    User = get_user_model()
    users = User.objects.all()
    return render(request, 'users/dashboard.html', {'user': request.user, 'users': users})


@user_passes_test(lambda u: u.is_superuser)
def manage_staff(request):
    User = get_user_model()
    users = User.objects.all()

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        is_staff = request.POST.get('is_staff') == 'on'
        user = User.objects.get(id=user_id)
        user.is_staff = is_staff
        user.save()
        messages.success(request, f'Permisos de staff actualizados para {user.username}.')

    return render(request, 'users/manage_staff.html', {'users': users})


@user_passes_test(lambda u: u.is_superuser)
def manage_staff_detail(request, user_id):
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'El usuario no existe.')
        return redirect('users:manage_staff')

    if request.method == 'POST':
        is_staff = request.POST.get('is_staff') == 'on'
        user.is_staff = is_staff
        user.save()
        messages.success(request, f'Permisos de staff actualizados para {user.username}.')
        return redirect('users:manage_staff_detail', user_id=user.id)

    return render(request, 'users/manage_staff_detail.html', {'user_obj': user})