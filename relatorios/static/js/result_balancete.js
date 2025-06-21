$(document).ready(function () {
  var table = $("#balancete").DataTable({
    paging: false,
    ordering: false,
    info: false,
    searching: true,
    language: {
      url: "https://cdn.datatables.net/plug-ins/2.3.2/i18n/pt-BR.json",
      search: "Pesquisar:",
    },
    dom: "Bfrtip",
    buttons: [],
  });

  // Botões de exportação

  $("#btn-save-pdf").on("click", function () {
    table.button().add(0, {
      extend: "pdfHtml5",
      title: "", // Remove título padrão
    });
    table.button(0).trigger();
    table.buttons().remove();
  });

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
      footer: true,
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
