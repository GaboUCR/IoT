import { SensorChartComponent } from "./components/sensorChart.js";
import { FormModal }             from "./components/formModal.js";
import { ActuatorComponent }     from "./components/actuatorComponent.js";
import { toggleDashboardView }   from "./components/toggleDashboardView.js";
import { RealTimeUpdater }       from "./components/realTimeUpdater.js";

document.addEventListener("DOMContentLoaded", () => {
  // 1) Instanciar los componentes existentes
  document.querySelectorAll(".sensor-component")
    .forEach(el => new SensorChartComponent(el));

  document.querySelectorAll(".actuator-component")
    .forEach(el => new ActuatorComponent(el));

  new FormModal();

  // 2) Inicializar toggle pub/sub…
  const toggleBtn = document.getElementById("toggle-pub-sub");
  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      const img = toggleBtn.querySelector("img.icon-toggle");
      if (img.alt === "pub") {
        img.src = `${window.STATIC_URL}img/pub.png`;
        img.alt = "sub";
        img.title = "Cambiar a Pub";
        toggleDashboardView("sub");
      } else {
        img.src = `${window.STATIC_URL}img/sub.png`;
        img.alt = "pub";
        img.title = "Cambiar a Sub";
        toggleDashboardView("pub");
      }
    });
  }

  // 3) **Polling de lecturas**: un solo fetch para todos los sensores
  new RealTimeUpdater({
    url: "/api/latest-readings/",
    interval: 3000
  });
});
