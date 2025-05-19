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
      btn.innerHTML = this.getImage("loading");

      // Inicialmente mostrar loading hasta que el polling lo actualice
      btn.querySelector("img").id = `state-${this.id}`;
      this.body.className = "flex justify-center items-center h-20";
      this.body.appendChild(btn);

      // Activar el botón después de que el valor inicial sea seteado por polling
      const observer = new MutationObserver(() => {
        btn.disabled = false; // habilitar cuando haya valor real
      });

      observer.observe(btn, { childList: true });

      btn.addEventListener("click", async () => {
        const img = btn.querySelector("img");
        if (!img) return;

        // Leer valor actual del src (check o x)
        const isOn = img.src.includes("check");

        // Mostrar loading mientras se envía
        btn.innerHTML = this.getImage("loading");
        btn.disabled = true;

        try {
          const res = await fetch("/api/update-actuator/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              id: Number(this.id),
              value: !isOn
            })
          });

          if (!res.ok) throw new Error("Error al actualizar");

          // Esperar a que polling lo actualice (en segundos siguientes)
        } catch (err) {
          console.error("Error al enviar valor:", err);
          btn.innerHTML = this.getImage(isOn ? "check" : "x"); // volver al estado anterior
          btn.disabled = false;
        }

        // Reasignar ID al nuevo ícono para que polling pueda seguir encontrándolo
        const newImg = btn.querySelector("img");
        if (newImg) newImg.id = `state-${this.id}`;
      });
    }

  
    renderText() {
      const form = document.createElement("form");
      form.className = "flex flex-col gap-2 w-full max-w-sm";

      const input = document.createElement("input");
      input.type = "text";
      input.placeholder = "Enviar comando...";
      input.className = "border px-3 py-2 rounded";

      // ✅ ID único para que polling pueda actualizar
      input.id = `input-${this.id}`;

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
  