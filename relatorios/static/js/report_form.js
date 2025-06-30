// document
//   .getElementById("reportForm")
//   .addEventListener("submit", async function (event) {
//     event.preventDefault(); // impede envio padrão com target="_blank"

//     const form = event.target;
//     const formData = new FormData(form);

//     const response = await fetch(form.action, {
//       method: "POST",
//       body: formData,
//       headers: {
//         "X-Requested-With": "XMLHttpRequest",
//       },
//     });

//     if (response.ok) {
//       const blob = await response.blob();

//       // Cria uma URL temporária para o conteúdo
//       const url = window.URL.createObjectURL(blob);

//       // Abre nova aba com o conteúdo retornado
//       const novaAba = window.open();
//       novaAba.location.href = url;
//     } else {
//       alert("Erro ao processar. Tente novamente.");
//     }
//   });
