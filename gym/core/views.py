from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, DeleteView, DetailView
from django.db.models import Count
from .models import NfcCard, Usuario, Identificacion, Mensualidad, Racha, MqttConfig
from .forms import (NfcCardForm, UsuarioForm, IdentificacionForm,
                    MensualidadForm, RachaForm, MqttConfigForm)
from . import mqtt_service


class LoginRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        uid = request.session.get('usuario_id')
        if not uid:
            return redirect('login')
        self.current_usuario = Usuario.objects.filter(id=uid).first()
        if not self.current_usuario:
            request.session.flush()
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        uid = request.session.get('usuario_id')
        if not uid:
            return redirect('login')
        self.current_usuario = Usuario.objects.filter(id=uid).first()
        if not self.current_usuario:
            request.session.flush()
            return redirect('login')
        if self.current_usuario.admin != 1:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


class HomeView(LoginRequiredMixin, ListView):
    template_name = 'core/home.html'
    context_object_name = 'usuarios'

    def get_queryset(self):
        u = self.current_usuario
        if u.admin == 1:
            return Usuario.objects.all()
        return Usuario.objects.filter(id=u.id)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from .models import Racha
        ctx['mi_racha'] = Racha.objects.filter(usuario=self.current_usuario).count()
        ctx['mis_rachas'] = Racha.objects.filter(usuario=self.current_usuario).order_by('-registro')[:10]
        return ctx


# ---------- NFC ----------
class NfcListView(AdminRequiredMixin, ListView):
    model = NfcCard
    template_name = 'core/nfc_list.html'
    context_object_name = 'items'


class NfcCreateView(AdminRequiredMixin, CreateView):
    model = NfcCard
    form_class = NfcCardForm
    template_name = 'core/form.html'
    success_url = reverse_lazy('nfc_list')


class NfcDeleteView(AdminRequiredMixin, DeleteView):
    model = NfcCard
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('nfc_list')


# ---------- USUARIOS ----------
class UsuarioListView(LoginRequiredMixin, ListView):
    model = Usuario
    template_name = 'core/usuario_list.html'
    context_object_name = 'items'

    def get_queryset(self):
        u = self.current_usuario
        if u.admin == 1:
            return Usuario.objects.all()
        return Usuario.objects.filter(id=u.id)


class UsuarioCreateView(AdminRequiredMixin, CreateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'core/form.html'
    success_url = reverse_lazy('usuario_list')


class UsuarioDetailView(LoginRequiredMixin, DetailView):
    model = Usuario
    template_name = 'core/usuario_detail.html'
    context_object_name = 'item'

    def dispatch(self, request, *args, **kwargs):
        r = super().dispatch(request, *args, **kwargs)
        # check ownership after object resolved is hard; do in get
        return r

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        u = self.current_usuario
        if u.admin != 1 and obj.id != u.id:
            from django.http import Http404
            raise Http404
        return obj


class UsuarioDeleteView(AdminRequiredMixin, DeleteView):
    model = Usuario
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('usuario_list')


# ---------- IDENTIFICACIONES ----------
class IdentificacionListView(LoginRequiredMixin, ListView):
    model = Identificacion
    template_name = 'core/identificacion_list.html'
    context_object_name = 'items'

    def get_queryset(self):
        u = self.current_usuario
        if u.admin == 1:
            return Identificacion.objects.all()
        return Identificacion.objects.filter(usuario=u)


class IdentificacionCreateView(AdminRequiredMixin, CreateView):
    model = Identificacion
    form_class = IdentificacionForm
    template_name = 'core/form.html'
    success_url = reverse_lazy('identificacion_list')


class IdentificacionDeleteView(AdminRequiredMixin, DeleteView):
    model = Identificacion
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('identificacion_list')


# ---------- MENSUALIDADES ----------
class MensualidadListView(LoginRequiredMixin, ListView):
    model = Mensualidad
    template_name = 'core/mensualidad_list.html'
    context_object_name = 'items'

    def get_queryset(self):
        u = self.current_usuario
        if u.admin == 1:
            return Mensualidad.objects.all()
        return Mensualidad.objects.filter(usuario=u)


class MensualidadCreateView(AdminRequiredMixin, CreateView):
    model = Mensualidad
    form_class = MensualidadForm
    template_name = 'core/form.html'
    success_url = reverse_lazy('mensualidad_list')


class MensualidadDeleteView(AdminRequiredMixin, DeleteView):
    model = Mensualidad
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('mensualidad_list')


# ---------- RACHAS ----------
class RachaListView(LoginRequiredMixin, ListView):
    model = Racha
    template_name = 'core/racha_list.html'
    context_object_name = 'items'

    def get_queryset(self):
        u = self.current_usuario
        if u.admin == 1:
            return Racha.objects.all()
        return Racha.objects.filter(usuario=u)


class RachaCreateView(AdminRequiredMixin, CreateView):
    model = Racha
    form_class = RachaForm
    template_name = 'core/form.html'
    success_url = reverse_lazy('racha_list')


class RachaDeleteView(AdminRequiredMixin, DeleteView):
    model = Racha
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('racha_list')


# ---------- MQTT ----------
def mqtt_config_view(request):
    uid = request.session.get('usuario_id')
    if not uid:
        return redirect('login')
    from .models import Usuario
    u = Usuario.objects.filter(id=uid).first()
    if not u or u.admin != 1:
        return redirect('home')
    cfg = MqttConfig.get_config()
    if request.method == 'POST':
        form = MqttConfigForm(request.POST, instance=cfg)
        if form.is_valid():
            form.save()
            if 'start' in request.POST:
                mqtt_service.start_mqtt()
            if 'stop' in request.POST:
                mqtt_service.stop_mqtt()
            if 'toggle_racha' in request.POST:
                cfg.duplicar_racha = not cfg.duplicar_racha
                cfg.save()
            return redirect('mqtt_config')
    else:
        form = MqttConfigForm(instance=cfg)
    return render(request, 'core/mqtt_config.html', {
        'form': form,
        'status': mqtt_service.get_status(),
        'cfg': cfg,
    })


def mqtt_status_api(request):
    return JsonResponse(mqtt_service.get_status())


def login_view(request):
    error = None
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        password = request.POST.get('password', '')
        u = Usuario.objects.filter(nombre=nombre, password=password).first()
        if u:
            request.session['usuario_id'] = u.id
            request.session['usuario_nombre'] = u.nombre
            request.session['is_admin'] = (u.admin == 1)
            return redirect('home')
        error = 'Credenciales invalidas'
    return render(request, 'core/login.html', {'error': error})


def logout_view(request):
    request.session.flush()
    return redirect('login')


def top_view(request):
    from .models import Usuario, Racha
    ranking = Usuario.objects.annotate(num_rachas=Count('rachas')).order_by('-num_rachas')[:20]
    return render(request, 'core/top.html', {'ranking': ranking})


def registro_view(request):
    error = None
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        password = request.POST.get('password', '')
        if not nombre or not password:
            error = 'Nombre y password requeridos'
        elif Usuario.objects.filter(nombre=nombre).exists():
            error = 'El usuario ya existe'
        else:
            Usuario.objects.create(nombre=nombre, password=password, admin=0)
            return redirect('login')
    return render(request, 'core/registro.html', {'error': error})