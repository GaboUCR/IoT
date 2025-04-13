// static/js/components/toggleDashboardView.js


export function toggleDashboardView(to) {
    const sensors = document.getElementById("sensor-container");
    const actuators = document.getElementById("actuator-container");
  
    if (to === "sub") {
      sensors.classList.remove("hidden");
      actuators.classList.add("hidden");
    } else {
      actuators.classList.remove("hidden");
      sensors.classList.add("hidden");
    }
  }
  