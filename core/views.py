from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.views.decorators.http import require_POST
from .models import Servicio
from .forms import ServicioForm

def inicio(request):
    return render(request, 'core/inicio.html')

@login_required
def servicios(request):
    return render(request, 'core/servicios.html', {'servicios': Servicio.objects.filter(propietario=request.user)})

@login_required
def servicio_nuevo(request):
    form = ServicioForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.propietario = request.user
        obj.save()
        return redirect('servicios')
    return render(request, 'core/form.html', {'form': form, 'titulo': 'Nuevo servicio'})

@login_required
def servicio_editar(request, pk):
    obj = get_object_or_404(Servicio, pk=pk, propietario=request.user)
    form = ServicioForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('servicios')
    return render(request, 'core/form.html', {'form': form, 'titulo': 'Editar servicio'})

@login_required
def servicio_eliminar(request, pk):
    obj = get_object_or_404(Servicio, pk=pk, propietario=request.user)
    if request.method == 'POST':
        obj.delete()
        return redirect('servicios')
    return render(request, 'core/confirmar.html', {'obj': obj})

def registro(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.save())
        return redirect('servicios')
    return render(request, 'core/form.html', {'form': form, 'titulo': 'Registro'})

def iniciar_sesion(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('servicios')
    return render(request, 'core/form.html', {'form': form, 'titulo': 'Iniciar sesión'})

@require_POST
def cerrar_sesion(request):
    logout(request)
    return redirect('inicio')
