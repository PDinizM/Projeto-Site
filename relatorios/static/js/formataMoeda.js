document.addEventListener("DOMContentLoaded", () => {
  function formataMoedaPTBR() {
    document.querySelectorAll(".moeda-pt-br").forEach((el) => {
      let texto = el.textContent.trim();
      texto = texto.replace(/\./g, "").replace(",", ".");
      const valor = parseFloat(texto);
      if (!isNaN(valor)) {
        el.textContent = valor.toLocaleString("pt-BR", {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        });
      }
    });
  }

  // Chama a função para formatar
  formataMoedaPTBR();
});
