from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import RedirectView
from django.utils.text import slugify


class RedirectToGroupView(RedirectView):
    """
    View que redireciona para o primeiro grupo encontrado no usuário.
    Se o usuário não tiver grupos, faz logout e exibe mensagem de erro.
    """

    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user

        if not user.is_authenticated:
            return "/login/"

        # Verifica se o usuário tem grupos
        user_groups = user.groups.all()

        if not user_groups.exists():
            # Faz logout e exibe mensagem
            logout(self.request)
            messages.error(
                self.request, "O usuário deve ter uma área de acesso"
            )
            return "/login/"

        # Redireciona para o primeiro grupo
        first_group = user_groups.first()
        group_name = slugify(first_group.name)
        print(group_name)
        # Redireciona baseado no nome do grupo
        return f"/{group_name}/"
