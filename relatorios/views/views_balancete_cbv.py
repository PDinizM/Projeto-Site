from typing import Any

from django.http import HttpRequest, HttpResponse
from django.views.generic import TemplateView

from relatorios.forms.formularios import BalanceteForm
from relatorios.mixin.mixins import FormSessionMixin
from relatorios.utils.balancete import Balancete, BalanceteContext
from relatorios.utils.conexao import conectar_dominio
from relatorios.utils.export_utils import dataframe_para_excel_response


class BalanceteRelatorioView(FormSessionMixin, TemplateView):
    """
    View para geração do relatório balancete com as seguintes opções:
    - Balancete comum (Normal e Plano ECF)
    - Relatório Consolidado (Apenas ECF)
    - Cruzamento com ECF

    Attributes:
        template_form (str): Caminho do template do formulário
        template_result (str): Caminho do template de resultados
        session_key (str): Chave para armazenamento dos dados do formulário na sessão
    """

    # 1. Constantes/Configurações da View
    template_form = "relatorios/balancete/form.html"
    template_result = "relatorios/balancete/result.html"
    session_key = "balancete_form_inputs"

    # 2. Métodos do ciclo de vida da View (HTTP methods)
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Handle GET requests: exibe o formulário, pré-preenchido se houver dados na sessão."""

        form = BalanceteForm(self.get_previous_form_data(request))
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Handle POST requests: valida o formulário e processa os dados ou retorna erros."""

        form = BalanceteForm(request.POST)
        if not form.is_valid():
            return self._handle_error(form=form)

        return self._process_form_valid(request, form)

    # 3. Métodos auxiliares principais
    def get_template_names(self) -> str:
        """Determina qual template deve ser renderizado com base no estado da view."""

        if hasattr(self, "balancete_context") and not hasattr(self, "form_has_errors"):
            return self.template_result
        return self.template_form

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        if hasattr(self, "balancete_context"):
            context.update(
                {
                    "form_title": self.balancete_context.form.titulo,
                    "data_inicial": self.balancete_context.data_inicial,
                    "data_final": self.balancete_context.data_final,
                    "mostrar_resumo": self.balancete_context.mostrar_resumo,
                    "mostrar_conferencia": self.balancete_context.mostrar_conferencia,
                    "cnpj": self.balancete_context.df_empresas.loc[0, "CNPJ"],
                    "nome_empresa": self.balancete_context.df_empresas.loc[
                        0, "nome_emp"
                    ],
                    "dados_relatorio_balancete": kwargs["balancete"].to_dict(
                        orient="records"
                    ),
                }
            )

        if "form" in kwargs:
            context["form"] = kwargs["form"]
            context["form_title"] = kwargs["form"].titulo

        return context

    # 4. Métodos de processamento do formulário
    def _process_form_valid(
        self, request: HttpRequest, form: BalanceteForm
    ) -> HttpResponse:
        """
        Processa o formulário válido: salva na sessão, gera o relatório,
        renderiza o resultado ou exporta para Excel. Em caso de erro, exibe no formulário.
        """
        self.store_form_data(request, form)

        try:
            self.balancete_context = self._create_balancete_context(form)
            balancete = Balancete.gerar(self.balancete_context)
            if (
                len(self.balancete_context.empresas) > 1
                and not self.balancete_context.consolidado
            ) or self.balancete_context.cruzamento_ecf:
                return dataframe_para_excel_response(balancete)

            else:
                return self.render_to_response(
                    self.get_context_data(form=form, balancete=balancete)
                )

        except Exception as e:
            return self._handle_error(form=form, message=str(e))

        finally:
            if hasattr(self, "balancete_dados"):
                self.balancete_context.conexao.dispose()

    # 5. Métodos auxiliares específicos
    def _create_balancete_context(self, form: BalanceteForm) -> BalanceteContext:
        """Cria e retorna um contexto BalanceteContext a partir do formulário."""
        dados = form.cleaned_data
        engine = conectar_dominio(dados["conexao"])

        return BalanceteContext(
            request=self.request,
            form=form,
            tipo_balancete=dados["balancete_tipo"],
            data_inicial=dados["data_inicial"],
            data_final=dados["data_final"],
            transferencia=dados.get("transferencia", False),
            zeramento=dados.get("zeramento", False),
            cruzamento_ecf=dados.get("cruzamento_ecf", False),
            consolidado=dados.get("consolidado", False),
            mostrar_conferencia=dados.get("conferencia", False),
            mostrar_resumo=dados.get("resumo", False),
            df_empresas=form.get_empresas_dataframe(),
            empresas=form.get_lista_empresas(),
            conexao=engine,
        )

    # 6. Handlers de erro
    def _handle_error(self, form=None, message=None) -> HttpResponse:
        """Lida com erros durante o processamento do formulário."""
        if message and form:
            form.add_error(None, message)
        self.form_has_errors = True
        return self.render_to_response(self.get_context_data(form=form))
