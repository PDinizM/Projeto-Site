from django.http import HttpRequest, HttpResponse
from django.views.generic import TemplateView

from relatorios.forms.comparativo import ComparativoForm
from relatorios.mixin.mixins import FormSessionMixin
from relatorios.services.comparativo import (
    ComparativoContext,
    ComparativoReportResult,
    ComparativoReportService,
    montar_contexto,
)
from relatorios.utils.conexao import conectar_dominio


class ComparativoRelatorioView(FormSessionMixin, TemplateView):
    # ------------------------ Váriaveis ------------------------
    template_form = "relatorios/comparativo/form.html"
    template_result = "relatorios/comparativo/result.html"
    session_key = "comparativo_form_inputs"

    # Atributos privados para armazenar o resultado do relatório e o contexto de geração
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._report_result: ComparativoReportResult | None = None
        self._comparativo_context: ComparativoContext | None = None
        self._service_has_erros: bool | None = None

    # ------------------------ GET ------------------------
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Exibe o formulário de balancete.
        Se houver dados anteriores na sessão, eles são usados para preencher o formulário.
        """
        form = ComparativoForm(initial=self.get_previous_form_data(request))
        return self.render_to_response({"form": form})

    def get_template_names(self) -> str:
        """Determina qual template deve ser renderizado com base no estado da view."""

        return (
            self.template_result
            if self._comparativo_context and not self._service_has_erros
            else self.template_form
        )

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Processa a submissão do formulário:
        1. Valida o formulário
        2. Cria o contexto de geração do comparativo
        3. Chama o serviço de geração de relatório
        4. Trata erro, exportação para Excel ou renderização do template de resultados
        """
        form = ComparativoForm(request.POST)
        if not form.is_valid():
            # Retorna o formulário com erros se inválido
            return self._render_form_with_errors(form)

        # 1. Monta o contexto do balancete com base nos dados do formulário
        self.store_form_data(request, form)  # Salva os dados do relátorio
        self._comparativo_context = self._create_comparativo_context(form)

        # 2. Chama o service para gerar o relatório
        try:
            self._report_result = ComparativoReportService.gerar(
                self._comparativo_context
            )

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
        context = montar_contexto(self._comparativo_context, self._report_result)
        return self.render_to_response(context)

    # -------------- Helpers -----------------
    def _render_form_with_errors(
        self, form: ComparativoForm, message: str | None = None
    ) -> HttpResponse:
        """
        Exibe o formulário novamente com mensagens de erro, se houver.
        """

        self._service_has_erros = True

        if message:
            form.add_error(None, message)
        return self.render_to_response({"form": form})

    def _create_comparativo_context(self, form: ComparativoForm) -> ComparativoContext:
        """
        Cria um objeto BalanceteContext com os dados validados do formulário.
        Este objeto encapsula todos os parâmetros necessários para geração do balancete.
        """
        dados = form.cleaned_data
        engine = conectar_dominio(dados["conexao"])

        return ComparativoContext(
            request=self.request,
            form=form,
            data_inicial=dados["data_inicial"],
            data_final=dados["data_final"],
            transferencia=dados.get("transferencia", False),
            zeramento=dados.get("zeramento", False),
            mostrar_resumo=dados.get("resumo", False),
            saldo_acumulado=dados.get("saldo_acumulado"),
            saldo_anterior=dados.get("saldo_anterior"),
            classificacoes=dados["classificacoes"],
            df_empresas=form.get_empresas_dataframe(),
            empresas=form.get_lista_empresas(),
            conexao=engine,
        )

    def _dispose_connection(self):
        """
        Fecha a conexão do SQLAlchemy com o banco, se existente.
        Evita conexões pendentes.
        """
        if self._comparativo_context is not None:
            self._comparativo_context.conexao.dispose()
