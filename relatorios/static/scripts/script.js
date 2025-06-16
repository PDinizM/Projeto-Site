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

//   // Função só para saldo com D e C
//   function formataSaldoCD() {
//     document.querySelectorAll(".saldo").forEach((el) => {
//       let texto = el.textContent.trim();
//       texto = texto.replace(/\./g, "").replace(",", ".");
//       const valor = parseFloat(texto);
//       if (!isNaN(valor) && valor !== 0) {
//         let valorFormatado = Math.abs(valor).toLocaleString("pt-BR", {
//           minimumFractionDigits: 2,
//           maximumFractionDigits: 2,
//         });
//         let sinal = valor > 0 ? " D" : " C";
//         el.textContent = valorFormatado + sinal;
//       } else if (valor === 0) {
//         el.textContent = "0,00";
//       }
//     });
//   }

//   // Chama as duas funções
//   formataMoedaPTBR();
//   formataSaldoCD();
// });
