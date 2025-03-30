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
        icon.src = "/static/img/graph.png";        // cambiar al ícono de gráfico
        icon.alt = "Gráfico";
        this.btnToggle.title = "Ver gráfico";
      } else {
        icon.src = "/static/img/live.png";         // cambiar al ícono de live
        icon.alt = "Tiempo real";
        this.btnToggle.title = "Ver tiempo real";
      }
    
      this.render();
    }
    
    render() {
      this.body.innerHTML = "";
      if (this.mode === "realtime") {
        this.renderRealtime();
      } else {
        this.renderHistorical();
      }
    }
  
    renderRealtime() {
      const valor = document.createElement("p");
      valor.id = `valor-${this.sensorId}`;
      valor.className = "text-4xl font-bold text-blue-600";
      valor.textContent = "-- °C";
  
      this.body.appendChild(valor);
      this.startRealtimeSimulation(valor);
    }
  
    startRealtimeSimulation(valorEl) {
      if (this.interval) clearInterval(this.interval);
  
      const update = () => {
        const val = (20 + Math.random() * 10).toFixed(2);
        valorEl.textContent = `${val} °C`;
      };
  
      update();
      this.interval = setInterval(update, 2000);
    }

    renderHistorical() {
      if (this.interval) clearInterval(this.interval);
  
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
    
      // Crear wrapper para el componente fullscreen
      const wrapper = document.createElement("div");
      wrapper.className = "max-w-5xl mx-auto";
    
      // Clonar el nodo original del componente
      const cloned = this.root.cloneNode(true);
      cloned.classList.add("bg-white", "rounded", "shadow", "p-4");
    
      // Cambiar el botón toggle fullscreen dentro del clon a "cerrar"
      const closeBtn = document.createElement("button");
      closeBtn.textContent = "Cerrar";
      closeBtn.className = "exit-fullscreen absolute top-4 right-4 bg-red-500 text-white px-3 py-1 rounded";
      closeBtn.addEventListener("click", () => this.exitFullscreen());
    
      // Append
      wrapper.appendChild(closeBtn);
      wrapper.appendChild(cloned);
      container.appendChild(wrapper);
    
      // Mostrar overlay
      container.classList.remove("hidden");
      document.body.classList.add("overflow-hidden");
    
      // Inicializar funcionalidad JS en el nuevo clon
      new SensorChartComponent(cloned);  // crear nueva instancia sobre el clon
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
    
      // Elegir unidad para eje X según el rango
      let timeUnit = "minute";
      if (diffMin <= 60) timeUnit = "minute";
      else if (diffMin <= 60 * 6) timeUnit = "minute";
      else if (diffMin <= 60 * 24) timeUnit = "hour";
      else if (diffMin <= 60 * 24 * 7) timeUnit = "day";
      else timeUnit = "week";
    
      // Generar datos simulados entre from y to
      const numPoints = 15;
      const labels = [];
      const values = [];
      const step = (toDate - fromDate) / numPoints;
    
      for (let i = 0; i < numPoints; i++) {
        const ts = new Date(fromDate.getTime() + i * step);
        labels.push(ts.toISOString()); // timestamp ISO para eje temporal
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
            borderColor: "rgb(59, 130, 246)",
            backgroundColor: "rgba(59, 130, 246, 0.2)",
            tension: 0.3
          }]
        },
        options: {
          responsive: true,
          scales: {
            x: {
              type: 'time',
              time: {
                unit: timeUnit,
                tooltipFormat: 'DD T',
                displayFormats: {
                  minute: 'HH:mm',
                  hour: 'HH:mm',
                  day: 'dd/MM',
                  week: 'dd/MM',
                },
              },
              title: {
                display: true,
                text: 'Tiempo'
              }
            },
            y: {
              beginAtZero: false,
              title: {
                display: true,
                text: '°C'
              }
            }
          },
          plugins: {
            legend: {
              display: true
            },
            tooltip: {
              mode: 'index',
              intersect: false
            }
          }
        }
      });
    }
  }
  