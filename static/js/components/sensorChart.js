// static/js/components/sensorChart.js

export class SensorChartComponent {
    constructor(root) {
      this.root = root;
      this.sensorId = root.dataset.sensorId;
      this.mode = "realtime";
  
      this.btnToggle = this.root.querySelector(".toggle-mode");
      this.body = this.root.querySelector(".sensor-body");
      this.fullscreenBtn = this.root.querySelector(".fullscreen-btn");
      this.fullscreenBtn.addEventListener("click", () => this.expandToFullscreen());
      
      this.chart = null; // instancia Chart.js
      this.init();
    }
  
    init() {
      this.btnToggle.addEventListener("click", () => this.toggleMode());
      this.render();
    }
  
    toggleMode() {
      this.mode = this.mode === "realtime" ? "historical" : "realtime";
    
      const icon = this.btnToggle.querySelector("img.icon-toggle");
    
      if (this.mode === "realtime") {
        icon.src = "/static/img/graph.png";
        icon.alt = "Gráfico";
        this.btnToggle.title = "Ver gráfico";
      } else {
        icon.src = "/static/img/live.png";
        icon.alt = "Tiempo real";
        this.btnToggle.title = "Ver tiempo real";
      }
    
      this.render();
    }
    
    render() {
      this.body.innerHTML = "";
      if (this.mode === "historical") {
        this.renderHistorical();
      }
      // En modo realtime no se renderiza gráfico: el componente externo 'RealTimeUpdater' se encarga de actualizar valores.
    }
  
    renderHistorical() {
      const wrapper = document.createElement("div");
  
      // Selectores de fecha/hora
      const form = document.createElement("form");
      form.className = "flex flex-wrap gap-4 items-end mb-4";
  
      const from = this.createDateInput("from", "Desde:");
      const to = this.createDateInput("to", "Hasta:");
  
      const btn = document.createElement("button");
      btn.type = "submit";
      btn.textContent = "Actualizar";
      btn.className = "bg-blue-600 text-white px-3 py-1 rounded";
  
      form.append(from.group, to.group, btn);
      wrapper.appendChild(form);
  
      const canvas = document.createElement("canvas");
      canvas.height = 200;
      wrapper.appendChild(canvas);
  
      this.body.appendChild(wrapper);
  
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        this.renderChart(canvas, from.input.value, to.input.value);
      });
  
      // Preload con datos falsos
      const now = new Date();
      const before = new Date(now.getTime() - 10 * 60000);
      from.input.value = before.toISOString().slice(0, 16);
      to.input.value = now.toISOString().slice(0, 16);
  
      this.renderChart(canvas, from.input.value, to.input.value);
    }
  
    createDateInput(name, label) {
      const group = document.createElement("div");
      group.className = "flex flex-col";
  
      const lbl = document.createElement("label");
      lbl.textContent = label;
      lbl.className = "text-sm font-medium";
  
      const input = document.createElement("input");
      input.type = "datetime-local";
      input.className = "border rounded px-2 py-1";
  
      group.append(lbl, input);
      return { group, input };
    }

    expandToFullscreen() {
      const container = document.getElementById("fullscreen-container");
      container.innerHTML = ""; // limpiar anteriores
    
      const wrapper = document.createElement("div");
      wrapper.className = "max-w-5xl mx-auto";

      const cloned = this.root.cloneNode(true);
      cloned.classList.add("bg-white", "rounded", "shadow", "p-4");

      const closeBtn = document.createElement("button");
      closeBtn.innerHTML = `
        <button class="bg-red-500 text-white px-4 py-2 rounded shadow">
          Cerrar
        </button>
      `;
      closeBtn.className = "exit-fullscreen flex justify-end w-full mb-4";
      closeBtn.addEventListener("click", () => this.exitFullscreen());

      wrapper.appendChild(cloned);
      container.appendChild(closeBtn);  
      container.appendChild(wrapper);

      container.classList.remove("hidden");
      document.body.classList.add("overflow-hidden");
    
      new SensorChartComponent(cloned);
    }

    exitFullscreen() {
      const container = document.getElementById("fullscreen-container");
      container.classList.add("hidden");
      container.innerHTML = "";
      document.body.classList.remove("overflow-hidden");
    }
    
    renderChart(canvas, fromISO, toISO) {
      const fromDate = new Date(fromISO);
      const toDate = new Date(toISO);
      const diffMin = (toDate - fromDate) / 1000 / 60;
    
      let timeUnit = "minute";
      if (diffMin <= 60) timeUnit = "minute";
      else if (diffMin <= 60 * 6) timeUnit = "minute";
      else if (diffMin <= 60 * 24) timeUnit = "hour";
      else if (diffMin <= 60 * 24 * 7) timeUnit = "day";
      else timeUnit = "week";
    
      const numPoints = 15;
      const labels = [];
      const values = [];
      const step = (toDate - fromDate) / numPoints;
    
      for (let i = 0; i < numPoints; i++) {
        const ts = new Date(fromDate.getTime() + i * step);
        labels.push(ts.toISOString());
        values.push((20 + Math.random() * 10).toFixed(2));
      }
    
      if (this.chart) this.chart.destroy();
    
      this.chart = new Chart(canvas.getContext("2d"), {
        type: "line",
        data: {
          labels,
          datasets: [{
            label: "Temperatura",
            data: labels.map((t, i) => ({ x: t, y: values[i] })),
            tension: 0.3
          }]
        },
        options: {
          responsive: true,
          scales: {
            x: { type: 'time', time: { unit: timeUnit } },
            y: { beginAtZero: false }
          }
        }
      });
    }
  }
