// static/js/main.js

import { SensorChartComponent } from "./components/sensorChart.js";
import { FormModal } from "./components/formModal.js";
import { ActuatorComponent } from "./components/actuatorComponent.js";

document.addEventListener("DOMContentLoaded", () => {
  // Inicialización de sensores
  document.querySelectorAll(".sensor-component").forEach(el => {
    new SensorChartComponent(el);
  });

  // Inicialización de actuadores
  document.querySelectorAll(".actuator-component").forEach(el => {
    new ActuatorComponent(el);
  });

  // Inicialización del formulario modal
  new FormModal();

  // Lógica de toggle pub/sub
  const toggleBtn = document.getElementById("toggle-pub-sub");
  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      const img = toggleBtn.querySelector("img.icon-toggle");
      if (img.alt === "pub") {
        // Actualmente en modo "pub", cambiar a "sub"
        img.src = `${window.STATIC_URL}img/sub.png`;
        img.alt = "sub";
        img.title = "Cambiar a Pub";
        // Aquí podrías ocultar actuadores y mostrar sensors, etc.
        console.log("Cambiado a SUB");
      } else {
        // Modo "sub", cambiar a "pub"
        img.src = `${window.STATIC_URL}img/pub.png`;
        img.alt = "pub";
        img.title = "Cambiar a Sub";
        console.log("Cambiado a PUB");
      }
    });
  }
});
