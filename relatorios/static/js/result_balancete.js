$(document).ready(function () {
  var table = $("#balancete").DataTable({
    paging: false,
    ordering: false,
    info: false,
    searching: true,
    dom: "Brtip",
    language: {
      url: "https://cdn.datatables.net/plug-ins/2.3.2/i18n/pt-BR.json",
      search: "Pesquisar:",
    },
    buttons: [],
  });
  $("#customSearchInput").on("keyup", function () {
    table.search(this.value).draw();
  });
  // Botões de exportação

  $("#btn-save-pdf").on("click", function () {
    const element = document.getElementById("conteudo-para-exportar");
    const options = {
      margin: 0.5,
      filename: "balancete_relatorio.pdf",
      image: { type: "jpeg", quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true },
      jsPDF: { unit: "in", format: "a4", orientation: "landscape" },
      pagebreak: { mode: ["avoid-all", "css", "legacy"] },
    };

    html2pdf().from(element).set(options).save();
  });

  // botão copiar texto
  $("#btn-copy-text").on("click", function () {
    table.button().add(0, {
      extend: "copyHtml5",
      title: "", // Remove título padrão
    });
    table.button(0).trigger();
    table.buttons().remove();
  });

  $("#btn-save-xlsx").on("click", function () {
    table.button().add(0, {
      extend: "excelHtml5",
      title: null,
      customizeData: function (data) {
        for (var i = 0; i < data.body.length; i++) {
          let colunasNumericas = [4, 6, 7, 8]; // ajuste conforme sua tabela
          colunasNumericas.forEach(function (index) {
            if (data.body[i][index]) {
              let valor = data.body[i][index]
                .replace(/\./g, "")
                .replace(",", ".");
              let numero = parseFloat(valor);
              if (!isNaN(numero)) {
                data.body[i][index] = numero;
              }
            }
          });
          if (data.body[i][1]) {
            data.body[i][1] = "\u200C" + data.body[i][1];
          }
        }
      },
    });
    table.button(0).trigger();
    table.buttons().remove();
  });
});
