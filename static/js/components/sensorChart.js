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
  
      // 🆕 Botón de descarga
      const downloadBtn = document.createElement("button");
      downloadBtn.type = "button";
      downloadBtn.title = "Descargar";
      downloadBtn.className = "ml-2";
      downloadBtn.innerHTML = `
        <img src="/static/img/download.png" class="w-6 h-6" alt="Descargar">
      `;

      downloadBtn.addEventListener("click", () => {
        const fromDate = from.input.value;
        const toDate = to.input.value;
        if (!fromDate || !toDate) return;

        const url = `/api/sensor-readings/?sensor_id=${this.sensorId}&from=${fromDate}&to=${toDate}`;
        fetch(url)
          .then(res => res.json())
          .then(data => {
            if (!data.data) return;

            const rows = [["timestamp", "value"]];
            data.data.forEach(d => rows.push([d.timestamp, d.value]));

            const csv = rows.map(r => r.join(",")).join("\n");
            const blob = new Blob([csv], { type: "text/csv" });
            const link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = `sensor_${this.sensorId}_data.csv`;
            link.click();
          });
      });

      // Grupo para acciones
      const actions = document.createElement("div");
      actions.className = "flex items-center gap-2";

      actions.appendChild(btn);
      actions.appendChild(downloadBtn);

      form.append(from.group, to.group, actions);

      wrapper.appendChild(form);
  
      const canvas = document.createElement("canvas");
      canvas.height = 200;
      wrapper.appendChild(canvas);
  
      this.body.appendChild(wrapper);
        
      this.chart = new Chart(canvas.getContext("2d"), {
        type: "line",
        data: {
          labels: [],
          datasets: [{
            label: "Sin datos",
            data: [],
            borderColor: "rgba(0, 0, 0, 0.2)",
            backgroundColor: "rgba(0, 0, 0, 0.05)",
          }]
        },
        options: {
          responsive: true,
          scales: {
            x: { type: 'time' },
            y: { beginAtZero: true }
          },
          plugins: {
            legend: { display: false },
            tooltip: { enabled: false }
          }
        }
      });

      form.addEventListener("submit", (e) => {
        e.preventDefault();
        this.renderChart(canvas, from.input.value, to.input.value);
      });

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
      else if (diffMin <= 360) timeUnit = "minute";
      else if (diffMin <= 1440) timeUnit = "hour";
      else if (diffMin <= 10080) timeUnit = "day";
      else timeUnit = "week";

      const url = `/api/sensor-readings/?sensor_id=${this.sensorId}&from=${fromISO}&to=${toISO}`;

      fetch(url)
        .then(res => res.json())
        .then(data => {
          if (!data.data || data.data.length === 0) {
            if (this.chart) this.chart.destroy();
            this.chart = new Chart(canvas.getContext("2d"), {
              type: "line",
              data: { labels: [], datasets: [] },
              options: {
                plugins: { legend: { display: false } },
                scales: { x: { type: 'time' }, y: { beginAtZero: true } }
              }
            });
            return;
          }

          const labels = data.data.map(d => d.timestamp);
          const values = data.data.map(d => d.value);

          if (this.chart) this.chart.destroy();

          this.chart = new Chart(canvas.getContext("2d"), {
            type: "line",
            data: {
              labels,
              datasets: [{
                label: "Sensor",
                data: labels.map((x, i) => ({ x, y: values[i] })),
                borderColor: "rgb(59, 130, 246)",
                backgroundColor: "rgba(59, 130, 246, 0.1)",
                tension: 0.3,
                pointRadius: 3
              }]
            },
            options: {
              responsive: true,
              scales: {
                x: {
                  type: 'time',
                  time: { unit: timeUnit }
                },
                y: { beginAtZero: false }
              },
              plugins: {
                legend: { display: true },
                tooltip: { intersect: false, mode: 'index' }
              }
            }
          });
        })
        .catch(err => {
          console.error("Error cargando datos del sensor:", err);
        });
    }

  }
