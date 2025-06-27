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
    initComplete: function () {
      $("#balancete").css("font-size", "0.8rem");
    },
  });

  // Campo de busca customizado
  $("#customSearchInput").on("keyup", function () {
    table.search(this.value).draw();
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

  // Botão Excel
  $("#btn-save-xlsx").on("click", function () {
    // --- AJUSTE AQUI: índice (0-based) da coluna do checkbox -----------------
    // Se preferir descobrir dinamicamente, use:
    // const colunaCheckbox = table.columns().count() - 1;
    const colunaCheckbox = 10; // <- troque para o índice correto
    // -------------------------------------------------------------------------

    table.button().add(0, {
      extend: "excelHtml5",
      title: null,

      /* 1) Converte o checkbox ↦ “Sim”/“Não” já no momento em que
              o DataTables coleta as células do DOM.                  */
      exportOptions: {
        columns: ":visible",
        format: {
          body: function (data, rowIdx, colIdx, node) {
            if (colIdx === colunaCheckbox) {
              const chk = $(node).find('input[type="checkbox"]');
              return chk.length ? (chk.is(":checked") ? "✅" : "") : "";
            }
            // Para as demais células, devolve apenas o texto:
            return $(node).text().trim();
          },
        },
      },

      /* 2) Continua fazendo os ajustes que você já tinha
              (números em colunas financeiras, etc.).                */
      customizeData: function (data) {
        for (let i = 0; i < data.body.length; i++) {
          /* --- CONVERSÃO DE COLUNAS NUMÉRICAS ---------------- */
          const colunasNumericas = [4, 6, 7, 8]; // ajuste se necessário
          colunasNumericas.forEach(function (idx) {
            if (data.body[i][idx]) {
              const valor = data.body[i][idx]
                .replace(/\./g, "") // remove separador milhar
                .replace(",", "."); // troca vírgula por ponto
              const numero = parseFloat(valor);
              if (!isNaN(numero)) {
                data.body[i][idx] = numero;
              }
            }
          });

          /* --- FORÇA A COLUNA 1 A SER TEXTO ------------------ */
          if (data.body[i][1]) {
            data.body[i][1] = "\u200C" + data.body[i][1];
          }
        }
      },
    });

    /* 3) Aciona imediatamente o botão recém-criado.                 */
    table.button(0).trigger();
    table.buttons().remove();
  });
});

// FUNÇÃO DO CHECK
$("#balancete").on("click", "tr", function (e) {
  if ($(e.target).is('input[type="checkbox"]')) return;

  const $linha = $(this);
  const $checkbox = $linha.find(".conferencia-check");
  if (!$checkbox.length) return;

  const isChecked = $checkbox.prop("checked");
  $checkbox.prop("checked", !isChecked).trigger("change");
  $linha.toggleClass("checked", !isChecked);

  const tipoConta = $linha.data("tipo");
  const classificacao = String($linha.data("classificacao") || "").trim();

  console.log(
    "Clicou na linha:",
    classificacao,
    tipoConta,
    "Marcado agora:",
    !isChecked
  );

  if (tipoConta === "S" && classificacao !== "") {
    $("#balancete tbody tr").each(function () {
      const $outraLinha = $(this);
      const outraClass = String($outraLinha.data("classificacao") || "").trim();
      const $outraCheck = $outraLinha.find(".conferencia-check");

      if (
        outraClass &&
        outraClass !== classificacao &&
        outraClass.startsWith(classificacao)
      ) {
        console.log(" - Marcando filho:", outraClass);
        $outraCheck.prop("checked", !isChecked).trigger("change");
        $outraLinha.toggleClass("checked", !isChecked);
      }
    });
  }
});
