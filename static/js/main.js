import { SensorChartComponent } from "./components/sensorChart.js";
import { FormModal } from "./components/formModal.js";

document.addEventListener("DOMContentLoaded", () => {
  // Inicializar cada sensor
  document.querySelectorAll(".sensor-component").forEach((el) => {
    new SensorChartComponent(el);
  });
  // Inicializar modal
  new FormModal();

});
