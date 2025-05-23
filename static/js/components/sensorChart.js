// static/js/components/sensorChart.js

export class SensorChartComponent {
    constructor(root) {this.body
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

      const info = document.createElement("p");

      info.className = "text-sm text-gray-600 mb-2 text-center my-3";
      info.textContent = 
        "Valores promedio";
      
      wrapper.appendChild(info);
  
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
      container.innerHTML = "";         // limpia anteriores
      container.classList.remove("hidden");
      document.body.classList.add("overflow-hidden");

      // 1) placeholder para devolver el nodo original
      this._placeholder = document.createComment("sensor-placeholder");
      this.root.parentNode.replaceChild(this._placeholder, this.root);

      // 2) creamos un div para el botón de cerrar
      const header = document.createElement("div");
      header.className = "flex justify-end mb-4";

      const closeBtn = document.createElement("button");
      closeBtn.type = "button";
      closeBtn.className = "bg-red-500 text-white px-4 py-2 rounded shadow";
      closeBtn.textContent = "Cerrar";
      closeBtn.addEventListener("click", () => this.exitFullscreen());

      header.appendChild(closeBtn);
      container.appendChild(header);

      // 3) metemos la tarjeta (this.root) dentro de otro wrapper
      const wrapper = document.createElement("div");
      wrapper.className = "max-w-5xl mx-auto bg-white rounded shadow p-4";
      wrapper.appendChild(this.root);
      container.appendChild(wrapper);
    }

    exitFullscreen() {
      const container = document.getElementById("fullscreen-container");
      // 1) devolvemos el nodo original a su lugar
      this._placeholder.parentNode.replaceChild(this.root, this._placeholder);
      // 2) limpiamos y ocultamos
      container.classList.add("hidden");
      container.innerHTML = "";
      document.body.classList.remove("overflow-hidden");
    }

    renderChart(canvas, fromISO, toISO) {
      const ctx = canvas.getContext("2d");
      const url = `/api/sensor-readings/?sensor_id=${this.sensorId}&from=${fromISO}&to=${toISO}&buckets=20`;

      fetch(url)
        .then(res => res.json())
        .then(data => {
          // Si no hay datos, destruye el chart y crea uno vacío
          if (!data.data || data.data.length === 0) {
            if (this.chart) this.chart.destroy();
            this.chart = new Chart(ctx, {
              type: "line",
              data: { datasets: [] },
              options: {
                plugins: { legend: { display: false } },
                scales: {
                  x: { type: 'time' },
                  y: { beginAtZero: true }
                }
              }
            });
            return;
          }

          // 1. Mapea tus datos a un array de puntos { x: Date, y: Number }
          const points = data.data.map(d => ({
            x: new Date(d.timestamp),
            y: d.value
          }));

          // 2. Calcula el rango real de datos (min y max)
          const dataMin = points[0].x;
          const dataMax = points[points.length - 1].x;
          const diffMinData = (dataMax - dataMin) / 1000 / 60; // diferencia en minutos

          // 3. Decide la unidad de tiempo según diffMinData
          let timeUnitData = "minute";
          if (diffMinData > 60) timeUnitData = "hour";
          if (diffMinData > 1440) timeUnitData = "day";
          if (diffMinData > 10080) timeUnitData = "week";

          // 4. Destruye el chart anterior (si existe) y crea uno nuevo
          if (this.chart) this.chart.destroy();
          this.chart = new Chart(ctx, {
            type: "line",
            data: {
              datasets: [{
                label: "Sensor",
                data: points,
                borderColor: "rgb(59, 130, 246)",
                backgroundColor: "rgba(59, 130, 246, 0.1)",
                tension: 0.3,
                pointRadius: 0
              }]
            },
            options: {
              responsive: true,
              parsing: {
                xAxisKey: 'x',
                yAxisKey: 'y'
              },
              scales: {
                x: {
                  type: 'time',
                  time: {
                    unit: timeUnitData,
                    displayFormats: {
                      minute: 'HH:mm',
                      hour: 'HH:mm',
                      day: 'dd/MM',
                      week: 'dd/MM/yyyy'
                    }
                  },
                  ticks: {
                    source: 'data',
                    autoSkip: true
                  }
                },
                y: {
                  beginAtZero: false
                }
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
