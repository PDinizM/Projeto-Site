function reportForm(initialData = {}) {
  return {
    balancete_tipo: initialData.balancete_tipo || "DOMINIO",
    cruzamento_ecf: initialData.cruzamento_ecf,
    consolidado: initialData.consolidado,
    codigo_empresa: initialData.codigo_empresa,

    // getters...
    get balancete_normal() {
      return this.balancete_tipo === "DOMINIO";
    },

    get balancete_referencial() {
      return this.balancete_tipo === "ECF";
    },

    get permitir_multiplas_empresas() {
      return true;
    },

    atualizarEstado() {
      if (this.balancete_referencial && this.cruzamento_ecf) {
        this.cruzamento_ecf = false;
      }
      if (this.balancete_normal && this.consolidado) {
        this.consolidado = false;
      }

      if (!this.cruzamento_ecf) {
        this.emitir_varias_empresas = false;
      }
    },

    filtrarEmpresa($event) {
      this.codigo_empresa = $event.target.value
        .replace(/[^0-9,]/g, "")
        .replace(/^,/, "")
        .replace(/,+/g, ",");
    },

    init() {
      this.$el.addEventListener("change", this.atualizarEstado.bind(this));
      this.$el.addEventListener("reset", () => {
        setTimeout(() => this.atualizarEstado(), 0);
      });

      const limparSeDesmarcar = (campo) =>
        this.$watch(campo, (novo, antigo) => {
          if (antigo && !novo) this.codigo_empresa = "";
        });

      limparSeDesmarcar("consolidado");
      limparSeDesmarcar("emitir_varias_empresas");

      // Chamada inicial
      this.atualizarEstado();
    },
  };
}
