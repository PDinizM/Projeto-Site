document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("reportForm");
  const overlay = document.getElementById("loading-overlay");
  const submitBtn = form?.querySelector('button[type="submit"]');

  if (!form || !overlay) return; // segurança – evita erro se elementos não existirem

  form.addEventListener("submit", async (e) => {
    // se já estamos exibindo erros (GET) deixa o navegador continuar
    if (form.dataset.showingErrors === "true") return;

    e.preventDefault(); // evita submit normal

    if (!form.checkValidity()) return;

    try {
      activateLoading(); // ⭐️ mostra spinner

      const formData = new FormData(form);
      const response = await fetch(form.action || window.location.href, {
        method: "POST",
        body: formData,
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });

      const ctype = response.headers.get("Content-Type") || "";

      // ⇣⇣⇣ 1) RESPOSTA É XLSX  ⇣⇣⇣
      if (
        response.ok &&
        ctype.includes(
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
      ) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        // tenta obter nome do arquivo do cabeçalho
        const disp = response.headers.get("Content-Disposition") || "";
        const match = disp.match(/filename\*?=([^;]+)/);
        const filename = "relatorio.xlsx";

        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }

      // ⇣⇣⇣ 2) RESPOSTA É HTML SEM ERRO  ⇣⇣⇣
      else {
        const text = await response.text();

        const temErro =
          text.includes("alert alert-danger") || text.includes("is-invalid");

        if (!temErro) {
          const novaAba = window.open("", "_blank");
          novaAba.document.write(text);
          novaAba.document.close();
        } else {
          // força renderização dos erros na própria página
          form.dataset.showingErrors = "true";
          form.submit(); // GET
        }
      }
    } catch (err) {
      console.error("Erro:", err);
      form.dataset.showingErrors = "true";
      form.submit(); // fallback GET para exibir erros
    } finally {
      deactivateLoading(); // 🛑 esconde spinner mesmo com erro
    }
  });

  /* utilidades de loading -------------------------------------------------- */
  function activateLoading() {
    document.body.classList.add("loading-active");
    overlay.classList.remove("d-none");

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.setAttribute("data-original-text", submitBtn.innerHTML);
      submitBtn.innerHTML = `
        <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
        Processando...
      `;
    }
  }

  function deactivateLoading() {
    document.body.classList.remove("loading-active");
    overlay.classList.add("d-none");

    if (submitBtn) {
      submitBtn.disabled = false;
      const original = submitBtn.getAttribute("data-original-text");
      if (original) submitBtn.innerHTML = original;
    }
  }
});
