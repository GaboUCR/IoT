// static/js/main.js

import { SensorChartComponent } from "./components/sensorChart.js";
import { FormModal } from "./components/formModal.js";
import { ActuatorComponent } from "./components/actuatorComponent.js";

document.addEventListener("DOMContentLoaded", () => {
  // Inicializar cada sensor (si quieres mantenerlos)
  document.querySelectorAll(".sensor-component").forEach((el) => {
    new SensorChartComponent(el);
  });

  // Inicializar actuadores
  document.querySelectorAll(".actuator-component").forEach((el) => {
    console.log("Inicializando componente actuador:", el);
    new ActuatorComponent(el);
  });

  // Inicializar modal
  new FormModal();
});
