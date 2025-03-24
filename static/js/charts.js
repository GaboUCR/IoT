// static/js/charts.js

// Simulación de valor actual en tiempo real
function actualizarValorTemperatura() {
    const valor = (20 + Math.random() * 10).toFixed(2);
    document.getElementById("valor-temperatura").textContent = `${valor} °C`;
  }
  setInterval(actualizarValorTemperatura, 2000);
  actualizarValorTemperatura();
  
  // Simulación de gráfico de histórico
  const ctx = document.getElementById("grafico-temperatura").getContext("2d");
  let labels = [];
  let data = [];
  
  for (let i = 0; i < 10; i++) {
    const hora = new Date(Date.now() - i * 60000).toLocaleTimeString().slice(0, 5);
    labels.unshift(hora);
    data.unshift((20 + Math.random() * 10).toFixed(2));
  }
  
  new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [{
        label: "Temperatura (°C)",
        data: data,
        borderColor: "rgb(59, 130, 246)",
        backgroundColor: "rgba(59, 130, 246, 0.2)",
        tension: 0.3
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: false
        }
      }
    }
  });
  