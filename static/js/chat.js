const form = document.getElementById("form-chat");
const input = document.getElementById("mensaje");
const chat = document.getElementById("chat");

form.addEventListener("submit", function (e) {
  e.preventDefault();

  const texto = input.value.trim();
  if (!texto) return;

  agregarMensaje("Tú", texto);
  input.value = "";

  fetch("/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: `pregunta=${encodeURIComponent(texto)}`
  })
  .then(response => response.json())
  .then(data => {
    // 👇 AQUÍ VA EXACTAMENTE LO QUE PREGUNTASTE
    console.log(data)
    agregarMensaje("Coach", data.respuesta);
    actualizarProgreso(data.progreso);
  })
  .catch(error => {
    console.error("Error:", error);
  });
});

// ---------------- FUNCIONES ----------------

function agregarMensaje(autor, mensaje) {
  const div = document.createElement("div");
  
  if(autor == "Tú"){
    div.className = "mensaje usuario";
    div.innerHTML = `<strong>${autor}:</strong> <p>${mensaje}</p>`;
  }

  if(autor == "Coach"){
    div.className = "mensaje asistente";
    div.innerHTML = `<strong>${autor}:</strong> ${mensaje}`;
  }

  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function actualizarProgreso(progreso) {
  const pasos = document.querySelectorAll(".paso");

  pasos[0].classList.toggle("activo", progreso.meta);
  pasos[1].classList.toggle("activo", progreso.accion);
  pasos[2].classList.toggle("activo", progreso.reflexion);
}
