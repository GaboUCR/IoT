// static/js/components/toggleDashboardView.js
export function toggleDashboardView(to) {
  const sensors  = document.getElementById("sensor-container");
  const actuators= document.getElementById("actuator-container");
  const icon     = document.getElementById("pub-sub-icon");

  // Mostrar/ocultar contenedores
  if (to === "pub") {
    actuators?.classList.remove("hidden");
    sensors?.classList.add("hidden");
  } else {
    sensors?.classList.remove("hidden");
    actuators?.classList.add("hidden");
  }

  // Cambiar el icono
  if (icon) {
    // Ajusta estas rutas si tu STATIC_URL es distinto
    const base = window.STATIC_URL || "/static/";
    const mapping = {
      sub: base + "img/pub.png",
      pub: base + "img/sub.png"
    };
    icon.src = mapping[to];
  }

  // Actualizar la URL sin recargar
  const url = new URL(window.location);
  url.searchParams.set("view", to);
  window.history.replaceState({}, "", url);
}
