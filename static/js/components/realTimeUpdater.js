export class RealTimeUpdater {
  /**
   * @param {string} url      Endpoint que devuelve { sensors: [ {id, name, value, timestamp} ] }
   * @param {number} interval Intervalo en ms para refrescar (por defecto 3000ms)
   */
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
      const body = await resp.json();
      return body.sensors || [];
    } catch (err) {
      console.error("RealTimeUpdater fetch error:", err);
      return [];
    }
  }

  async update() {
    const sensors = await this.fetchLatest();

    console.log(sensors);
    sensors.forEach(({ id, value, timestamp }) => {
      const container = document.getElementById(`sensor-${id}`);
      if (!container) return;

      const valueEl = container.querySelector(".last-value");
      const tsEl    = container.querySelector(".timestamp");
      if (valueEl) valueEl.textContent = value !== null ? value : "--";
      if (tsEl)    tsEl.textContent    = timestamp
        ? new Date(timestamp).toLocaleTimeString()
        : "";
    });
  }

  start() {
    // Primera actualización inmediata
    this.update();
    // Luego cada interval ms
    this.timer = setInterval(() => this.update(), this.interval);
  }

  stop() {
    if (this.timer) clearInterval(this.timer);
  }
}
