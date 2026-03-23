const form  = document.getElementById("form-chat");
const input = document.getElementById("mensaje");
const chat  = document.getElementById("chat");
const btnReiniciar = document.getElementById("btn-reiniciar");

form.addEventListener("submit", function (e) {
  e.preventDefault();

  const texto = input.value.trim();
  if (!texto) return;

  agregarMensaje("Tú", texto);
  input.value = "";
  input.disabled = true;

  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `pregunta=${encodeURIComponent(texto)}`
  })
  .then(response => response.json())
  .then(data => {
    agregarMensaje("Coach", data.respuesta);
    actualizarProgreso(data.progreso);
    input.disabled = false;
    input.focus();
  })
  .catch(error => {
    console.error("Error:", error);
    input.disabled = false;
  });
});

if (btnReiniciar) {
  btnReiniciar.addEventListener("click", function () {
    window.location.href = "/";
  });
}

// ─────────────────────────────────────────────
//  FUNCIONES
// ─────────────────────────────────────────────

function agregarMensaje(autor, mensaje) {
  const div = document.createElement("div");

  if (autor === "Tú") {
    div.className = "mensaje usuario";
    div.innerHTML = `<strong>${autor}:</strong> <p>${mensaje}</p>`;
  } else {
    div.className = "mensaje asistente";
    div.innerHTML = `<strong>${autor}:</strong> ${mensaje}`;
  }

  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function actualizarProgreso(progreso) {
  const explorar    = document.querySelector(".paso-explorar");
  const entender    = document.querySelector(".paso-entender");
  const identificar = document.querySelector(".paso-identificar");
  const dirigir     = document.querySelector(".paso-dirigir");

  if (explorar)    explorar.classList.toggle("activo",    !!progreso.explorar);
  if (entender)    entender.classList.toggle("activo",    !!progreso.entender);
  if (identificar) identificar.classList.toggle("activo", !!progreso.identificar);
  if (dirigir)     dirigir.classList.toggle("activo",     !!progreso.dirigir);
}

// Scroll al fondo al cargar
window.addEventListener("load", function () {
  chat.scrollTop = chat.scrollHeight;
});
