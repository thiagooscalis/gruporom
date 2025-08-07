from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify


@login_required
def redirect_to_group(request):
    """
    View que redireciona para o primeiro grupo encontrado no usuário.
    Se o usuário não tiver grupos, faz logout e exibe mensagem de erro.
    """
    user = request.user

    # Verifica se o usuário tem grupos
    user_groups = user.groups.all()

    if not user_groups.exists():
        # Faz logout e exibe mensagem
        logout(request)
        messages.error(
            request, "O usuário deve ter uma área de acesso"
        )
        return redirect("/login/")

    # Redireciona para o primeiro grupo
    first_group = user_groups.first()
    group_name = slugify(first_group.name)
    
    # Redireciona baseado no nome do grupo
    return redirect(f"/{group_name}/")


def privacidade_inclusive(request):
    """
    View pública para exibir a política de privacidade da Inclusive Travel.
    """
    return render(request, 'inclusive/privacidade.html')
