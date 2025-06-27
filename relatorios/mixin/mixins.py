import json

from django.core.serializers.json import DjangoJSONEncoder


class FormSessionMixin:
    session_key = None
    form_class = None

    def get_form(self, request, **kwargs):
        """Método completo para obter o formulário com dados da sessão"""
        form_kwargs = self.get_previous_form_data(request)
        form_kwargs.update(kwargs)
        return self.form_class(**form_kwargs)

    def get_previous_form_data(self, request):
        """
        Recupera dados do formulário da sessão.
        Retorna dict vazio se:
        - session_key não está definida
        """
        return request.session.get(self.session_key, {})

    def store_form_data(self, request, form):
        """Armazena dados de um formulário válido"""
        request.session[self.session_key] = json.loads(
            json.dumps(form.cleaned_data, cls=DjangoJSONEncoder)
        )

    def clear_form_data(self, request):
        """Limpa os dados da sessão"""
        if self.session_key in request.session:
            del request.session[self.session_key]
