document.addEventListener("alpine:init", () => {
  Alpine.data("reportForm", function (dadosIniciais = {}) {
    return {
      // Estado do formulário
      balancete_tipo: dadosIniciais.balancete_tipo || "DOMINIO",
      cruzamento_ecf: Boolean(dadosIniciais.cruzamento_ecf),
      consolidado: Boolean(dadosIniciais.consolidado),
      codigo_empresa: dadosIniciais.codigo_empresa || "",
      zeramento: Boolean(dadosIniciais.zeramento),
      transferencia: Boolean(dadosIniciais.transferencia),
      resumo: Boolean(dadosIniciais.resumo),
      conferencia: Boolean(dadosIniciais.conferencia),

      // Inicialização
      init() {
        this.sincronizarCheckboxes();
        this.configurarObservadores();
      },

      // Sincroniza checkboxes com o estado inicial
      sincronizarCheckboxes() {
        [
          "cruzamento_ecf",
          "consolidado",
          "zeramento",
          "transferencia",
          "resumo",
          "conferencia",
        ].forEach((campo) => {
          const checkbox = document.getElementById(`id_${campo}`);
          if (checkbox) checkbox.checked = this[campo];
        });
      },

      // Configura observadores para campos condicionais
      configurarObservadores() {
        // Observa mudanças no tipo de balancete
        this.$watch("balancete_tipo", (valor) => {
          if (valor === "ECF") {
            this.cruzamento_ecf = false; // Reseta quando ocultar
          }
        });
      },

      // Controla o comportamento do cruzamento_ecf
      aoAlterarCruzamento() {
        if (this.cruzamento_ecf) {
          this.desativarOutrosCampos();
        }
      },

      // Desativa todos os outros checkboxes
      desativarOutrosCampos() {
        const outrosCampos = [
          "zeramento",
          "transferencia",
          "resumo",
          "conferencia",
          "consolidado",
        ];
        outrosCampos.forEach((campo) => {
          this[campo] = false;
        });
      },

      filtrarEmpresa(event) {
        this.codigo_empresa = event.target.value
          .replace(/[^0-9,]/g, "") // Remove tudo que não for número ou vírgula
          .replace(/^,/, "") // Remove vírgula no início
          .replace(/,+/g, ","); // Substitui múltiplas vírgulas por uma única
      },

      // Computed properties
      get exibirCruzamentoECF() {
        return this.balancete_tipo !== "ECF";
      },

      get outrosCamposDesabilitados() {
        return this.cruzamento_ecf;
      },
    };
  });
});
