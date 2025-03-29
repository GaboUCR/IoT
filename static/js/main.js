// static/js/main.js

import { SensorChartComponent } from "./components/sensorChart.js";

document.addEventListener("DOMContentLoaded", () => {
  document
    .querySelectorAll(".sensor-component")
    .forEach((el) => new SensorChartComponent(el));
});
