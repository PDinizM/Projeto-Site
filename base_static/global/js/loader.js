document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("reportForm");
  const overlay = document.getElementById("loading-overlay");

  if (!form || !overlay) {
    return;
  }

  const submitButton = form.querySelector('button[type="submit"]');

  form.addEventListener("submit", (e) => {
    if (form.checkValidity()) {
      activateLoading();
      checkDownloadComplete();
    }
  });

  function activateLoading() {
    document.body.classList.add("loading-active");
    overlay.classList.remove("d-none");

    if (submitButton) {
      submitButton.disabled = true;
      const originalText = submitButton.innerHTML;
      submitButton.setAttribute("data-original-text", originalText);
      submitButton.innerHTML = `
                        <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                        Processando...
                    `;
    }
  }

  function deactivateLoading() {
    document.body.classList.remove("loading-active");
    overlay.classList.add("d-none");

    if (submitButton) {
      submitButton.disabled = false;
      const originalText = submitButton.getAttribute("data-original-text");
      if (originalText) {
        submitButton.innerHTML = originalText;
      }
    }
    document.cookie =
      "download_complete=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
  }

  function checkDownloadComplete() {
    const interval = setInterval(() => {
      if (
        document.cookie
          .split("; ")
          .find((row) => row.startsWith("download_complete="))
      ) {
        deactivateLoading();
        clearInterval(interval);
      }
    }, 1000); // Verifica a cada segundo
  }
});
