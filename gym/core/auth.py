from django.shortcuts import redirect


def get_current_usuario(request):
    uid = request.session.get('usuario_id')
    if not uid:
        return None
    from .models import Usuario
    return Usuario.objects.filter(id=uid).first()


def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            return redirect('login')
        from .models import Usuario
        u = Usuario.objects.filter(id=request.session.get('usuario_id')).first()
        if not u or u.admin != 1:
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper