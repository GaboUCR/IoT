// static/js/components/actuatorComponent.js

export class ActuatorComponent {
    constructor(root) {
      this.root = root;
      this.type = root.dataset.actuatorType;
      this.id = root.dataset.actuatorId;
      this.body = root.querySelector(".actuator-body");
  
      this.state = false; // false: apagado, true: encendido
      this.render();
      console.log("ActuatorComponent instanciado:", this.root);

    }
  
    render() {
      if (this.type === "binario") {
        this.renderBinary();
      } else if (this.type === "texto") {
        this.renderText();
      }
    }
  
    renderBinary() {
      const btn = document.createElement("button");
      btn.className = "transition p-2 rounded flex items-center justify-center";
      btn.innerHTML = this.getImage("X"); // default
  
      btn.addEventListener("click", async () => {
        btn.innerHTML = this.getImage("loading");
        btn.disabled = true;
  
        // Simulación de acción con delay
        setTimeout(() => {
          this.state = !this.state;
          btn.innerHTML = this.getImage(this.state ? "check" : "x");
          btn.disabled = false;
        }, 800);
      });
  
      // Centrar el botón
      this.body.className = "flex justify-center items-center h-20";
      this.body.appendChild(btn);
    }
  
    renderText() {
      const form = document.createElement("form");
      form.className = "flex flex-col gap-2 w-full max-w-sm";
  
      const input = document.createElement("input");
      input.type = "text";
      input.placeholder = "Enviar comando...";
      input.className = "border px-3 py-2 rounded";
  
      const btn = document.createElement("button");
      btn.type = "submit";
      btn.textContent = "Enviar";
      btn.className = "bg-blue-600 text-white px-4 py-2 rounded";
  
      form.append(input, btn);
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        console.log(`Mock: Enviando "${input.value}" al actuador ${this.id}`);
        input.value = "";
      });
  
      this.body.className = "flex justify-center";
      this.body.appendChild(form);
    }
  
    getImage(tipo) {
        console.log("Obteniendo imagen:", tipo); // ✅ Verifica si se llama

        const base = window.STATIC_URL || "/static/";
        const src = `${base}img/${tipo}.png`;
        return `<img src="${src}" alt="${tipo}" class="w-8 h-8">`;
      }      
  }
  