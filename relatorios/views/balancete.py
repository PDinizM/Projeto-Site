from django.http import HttpRequest, HttpResponse
from django.views.generic import TemplateView

from relatorios.forms.balancete import BalanceteForm
from relatorios.mixin.mixins import FormSessionMixin
from relatorios.services.balancete import (
    BalanceteContext,
    BalanceteReportResult,
    BalanceteReportService,
    montar_contexto,
)
from relatorios.utils.conexao import conectar_dominio


class BalanceteRelatorioView(FormSessionMixin, TemplateView):
    # ------------------------ Váriaveis ------------------------
    template_form = "relatorios/balancete/form.html"
    template_result = "relatorios/balancete/result.html"
    session_key = "balancete_form_inputs"

    # Atributos privados para armazenar o resultado do relatório e o contexto de geração
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._report_result: BalanceteReportResult | None = None
        self._balancete_context: BalanceteContext | None = None
        self._service_has_erros: bool | None = None

    # ------------------------ GET ------------------------
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Exibe o formulário de balancete.
        Se houver dados anteriores na sessão, eles são usados para preencher o formulário.
        """
        form = BalanceteForm()
        return self.render_to_response({"form": form})

    def get_template_names(self) -> str:
        """Determina qual template deve ser renderizado com base no estado da view."""

        return (
            self.template_result
            if self._balancete_context and not self._service_has_erros
            else self.template_form
        )

    # ------------------------ POST -----------------------
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Processa a submissão do formulário:
        1. Valida o formulário
        2. Cria o contexto de geração do balancete
        3. Chama o serviço de geração de relatório
        4. Trata erro, exportação para Excel ou renderização do template de resultados
        """
        form = BalanceteForm(request.POST)
        if not form.is_valid():
            # Retorna o formulário com erros se inválido
            return self._render_form_with_errors(form)

        # 1. Monta o contexto do balancete com base nos dados do formulário
        self.store_form_data(request, form)  # Salva os dados do relátorio
        self._balancete_context = self._create_balancete_context(form)

        # 2. Chama o service para gerar o relatório
        try:
            self._report_result = BalanceteReportService.gerar(self._balancete_context)

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
        context = montar_contexto(self._balancete_context, self._report_result)
        return self.render_to_response(context)

    # -------------- Helpers -----------------
    def _render_form_with_errors(
        self, form: BalanceteForm, message: str | None = None
    ) -> HttpResponse:
        """
        Exibe o formulário novamente com mensagens de erro, se houver.
        """

        self._service_has_erros = True

        if message:
            form.add_error(None, message)
        return self.render_to_response({"form": form})

    def _create_balancete_context(self, form: BalanceteForm) -> BalanceteContext:
        """
        Cria um objeto BalanceteContext com os dados validados do formulário.
        Este objeto encapsula todos os parâmetros necessários para geração do balancete.
        """
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

    def _dispose_connection(self):
        """
        Fecha a conexão do SQLAlchemy com o banco, se existente.
        Evita conexões pendentes.
        """
        if self._balancete_context is not None:
            self._balancete_context.conexao.dispose()
