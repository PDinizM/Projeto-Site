// FORMULA JS QUE LIMITA O INPUT DE EMPRESA E MOSTRA O INPUT DE CONSOLIDADO
document.addEventListener("DOMContentLoaded", () => {
  const inputConsolidado = document.getElementById("id_consolidado");
  const inputEmpresa = document.getElementById("id_codigo_empresa");
  const grupoConsolidado = document.getElementById("grupo-consolidado");
  const helpConsolidado = document.getElementById("help-multiplas-empresas");

  if (!inputConsolidado || !inputEmpresa) return;

  function atualizarExibicaoConsolidado() {
    const isReferencial = document.getElementById("id_balancete_tipo_1")?.checked;

    if (isReferencial) {
      grupoConsolidado.style.display = "block";
    } else {
      grupoConsolidado.style.display = "none";

      if (inputConsolidado.checked) {
        inputConsolidado.checked = false;
        limparCampoEmpresa();
      }
    }

    atualizarHelpConsolidado();
    atualizarAtributosEmpresa();
  }

  function atualizarHelpConsolidado() {
    if (inputConsolidado.checked && grupoConsolidado.style.display !== "none") {
      helpConsolidado.style.display = "block";
    } else {
      helpConsolidado.style.display = "none";
    }
  }

  function atualizarAtributosEmpresa() {
    const isReferencial = document.getElementById("id_balancete_tipo_1")?.checked;
    const isConsolidado = inputConsolidado.checked;

    removerRestringidores();

    if (isReferencial && isConsolidado) {
      // Modo consolidado: aceita números separados por vírgula
      inputEmpresa.setAttribute("pattern", "^(\\d+)(,\\d+)*$");
      inputEmpresa.setAttribute("maxlength", "255");
      inputEmpresa.setAttribute("oninvalid", "this.setCustomValidity('Digite apenas números separados por vírgula')");
      inputEmpresa.setAttribute("oninput", "this.setCustomValidity('')");
      inputEmpresa.setAttribute("placeholder", "");
      inputEmpresa.addEventListener("input", bloquearNaoNumerosVirgulaValidos);
    } else {
      // Modo normal: apenas número
      inputEmpresa.setAttribute("pattern", "^[0-9]+$");
      inputEmpresa.setAttribute("maxlength", "7");
      inputEmpresa.setAttribute("oninvalid", "this.setCustomValidity('Por favor, digite apenas números')");
      inputEmpresa.setAttribute("oninput", "this.setCustomValidity('')");
      inputEmpresa.setAttribute("placeholder", "Digite apenas números");
      inputEmpresa.addEventListener("input", bloquearNaoNumeros);
    }
  }

  function limparCampoEmpresa() {
    inputEmpresa.value = "";
  }

  // Apenas números (modo normal)
  function bloquearNaoNumeros(e) {
    e.target.value = e.target.value.replace(/[^0-9]/g, '');
  }

  // Números separados por vírgula, permite vírgula no final
  function bloquearNaoNumerosVirgulaValidos(e) {
    let valor = e.target.value;

    // Remove caracteres inválidos
    valor = valor.replace(/[^0-9,]/g, '');

    // Remove vírgulas duplicadas e no início
    valor = valor.replace(/^,/, '');
    valor = valor.replace(/,+/g, ',');
    valor = valor.replace(/(,\s*,)+/g, ',');

    e.target.value = valor;
  }

  function removerRestringidores() {
    inputEmpresa.removeEventListener("input", bloquearNaoNumeros);
    inputEmpresa.removeEventListener("input", bloquearNaoNumerosVirgulaValidos);
  }

  // Eventos
  inputConsolidado.addEventListener("change", () => {
    if (!inputConsolidado.checked) {
      limparCampoEmpresa();
    }

    atualizarHelpConsolidado();
    atualizarAtributosEmpresa();
  });

  const radios = document.querySelectorAll("input[name='balancete_tipo']");
  radios.forEach((radio) => {
    radio.addEventListener("change", atualizarExibicaoConsolidado);
  });

  // Inicialização
  atualizarExibicaoConsolidado();
});
