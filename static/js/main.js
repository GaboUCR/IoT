import { SensorChartComponent }  from "./components/sensorChart.js";
import { FormModal }             from "./components/formModal.js";
import { ActuatorComponent }     from "./components/actuatorComponent.js";
import { toggleDashboardView }   from "./components/toggleDashboardView.js";
import { RealTimeUpdater }       from "./components/realTimeUpdater.js";

window.addEventListener("DOMContentLoaded", () => {
  // 1) Obtener el modo de vista desde la URL
  const urlParams = new URLSearchParams(window.location.search);
  const mode = urlParams.get("view") || "sub";
  toggleDashboardView(mode);

  // 2) Instanciar componentes visuales
  document.querySelectorAll(".sensor-component")
    .forEach(el => new SensorChartComponent(el));

  document.querySelectorAll(".actuator-component")
    .forEach(el => new ActuatorComponent(el));

  // 3) Formularios
  new FormModal("form-modal", "open-form-modal", "close-form-modal");
  new FormModal("actuator-form-modal", "open-actuator-form-modal", "close-actuator-form-modal");

  // 4) Toggle pub/sub dinámico
  const toggleBtn = document.getElementById("toggle-pub-sub");
  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      const currentUrl = new URL(window.location.href);
      const currentView = currentUrl.searchParams.get("view") || "sub";
      const newView = currentView === "sub" ? "pub" : "sub";

      // Si NO estamos en dashboard, redirigir allí con el nuevo modo
      if (!window.location.pathname.includes("/dashboard")) {
        window.location.href = `/dashboard/?view=${newView}`;
      } else {
        toggleDashboardView(newView);  // ya estamos en dashboard, solo cambiar la vista
      }
    });
  }

  // 5) Actualización periódica de lecturas
  new RealTimeUpdater({
    url: "/api/latest-readings/",
    interval: 3000,
  });
});
