from django.http import HttpRequest, HttpResponse
from django.views.generic import TemplateView

from relatorios.forms.razao import RazaoForm
from relatorios.mixin.mixins import FormSessionMixin


class RazaoRelatorioView(FormSessionMixin, TemplateView):
    # ------------------------ Váriaveis ------------------------
    template_form = "relatorios/razao/form.html"
    template_result = "relatorios/razao/result.html"
    session_key = "razao_form_inputs"

    # ------------------------ GET ------------------------
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = RazaoForm(initial=self.get_previous_form_data(request))
        return self.render_to_response({"form": form})

    def get_template_names(self) -> str:
        """Determina qual template deve ser renderizado com base no estado da view."""

        return self.template_result if self.request.GET else self.template_form

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Processa a submissão do formulário:
        1. Valida o formulário
        2. Cria o contexto de geração do comparativo
        3. Chama o serviço de geração de relatório
        4. Trata erro, exportação para Excel ou renderização do template de resultados
        """
        form = RazaoForm(request.POST)
        if not form.is_valid():
            # Retorna o formulário com erros se inválido
            return self._render_form_with_errors(form)

        # 1. Monta o contexto do balancete com base nos dados do formulário
        self.store_form_data(request, form)  # Salva os dados do relátorio

        # 2. Chama o service para gerar o relatório
        try:
            ...

        except Exception as e:
            # Em caso de erro no service, exibe o erro no formulário
            return self._render_form_with_errors(form, str(e))

        finally:
            # Libera a conexão com o banco de dados
            self._dispose_connection()

        # 3. Se veio Excel, devolve direto
        if self._report_result.excel_response:
            return self._report_result.excel_response

        # 4. Renderiza template resultado
        return self.render_to_response()
