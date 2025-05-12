export class RealTimeUpdater {
  constructor({ url = "/api/latest-readings/", interval = 3000 } = {}) {
    this.url = url;
    this.interval = interval;
    this.timer = null;
    this.start();
  }

  async fetchLatest() {
    try {
      const resp = await fetch(this.url, {
        headers: { "X-Requested-With": "XMLHttpRequest" },
        credentials: "same-origin"
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      return await resp.json();
    } catch (err) {
      console.error("RealTimeUpdater fetch error:", err);
      return { sensors: [], actuators: [] };
    }
  }

  async update() {
    const { sensors = [], actuators = [] } = await this.fetchLatest();

    // Actualizar sensores
    sensors.forEach(({ id, value, timestamp }) => {
      const container = document.getElementById(`sensor-${id}`);
      if (!container) return;

      const valueEl = container.querySelector(".last-value");
      const tsEl = container.querySelector(".timestamp");

      if (valueEl) valueEl.textContent = value !== null ? value : "--";
      if (tsEl) tsEl.textContent = timestamp
        ? new Date(timestamp).toLocaleTimeString()
        : "";
    });

    // Actualizar actuadores
    actuators.forEach(({ id, type, value }) => {
      if (type === "binario") {
        const img = document.getElementById(`state-${id}`);
        if (img) {
          const src = value
            ? `${window.STATIC_URL}img/check.png`
            : `${window.STATIC_URL}img/x.png`;
          img.src = src;
        }
      } else if (type === "texto") {
        const container = document.querySelector(`.actuator-component[data-actuator-id="${id}"]`);
        if (!container) return;

        const input = container.querySelector("input[type='text']");
        if (input) input.placeholder = value || "Enviar comando...";
      }
    });
  }

  start() {
    this.update();
    this.timer = setInterval(() => this.update(), this.interval);
  }

  stop() {
    if (this.timer) clearInterval(this.timer);
  }
}
