export class ActuatorComponent {
    constructor(root) {
      this.root = root;
      this.id = root.dataset.actuatorId;
      this.type = root.dataset.actuatorType;  // "binary" o "text"
      this.bodyEl = root.querySelector(".actuator-body");
  
      this.render();
    }
  
    render() {
      // Limpia contenido antes de agregar
      this.bodyEl.className = "actuator-body flex flex-col items-center justify-center text-center gap-4 min-h-[100px]";
      this.bodyEl.innerHTML = "";
  
      if (this.type === "binary") {
        this.renderBinary();
      } else if (this.type === "text") {
        this.renderTextForm();
      }
    }
  
    // ======================
    // 1. Actuador binario
    // ======================
    renderBinary() {
      const button = document.createElement("button");
      button.textContent = "X";  // estado inicial
      button.className = "w-10 h-10 bg-red-500 text-white text-center font-bold text-xl rounded transition";  
      // Toggle de X a ✓
      button.addEventListener("click", () => {
        button.textContent = (button.textContent === "X") ? "✓" : "X";
        button.classList.toggle("bg-red-500");
        button.classList.toggle("bg-green-500");
      });
  
      this.bodyEl.appendChild(button);
    }
  
    // ======================
    // 2. Actuador de texto
    // ======================
    renderTextForm() {
        const form = document.createElement("form");
        form.className = "flex flex-col gap-2 items-center w-full";
      
        const input = document.createElement("input");
        input.type = "text";
        input.placeholder = "Ingrese valor...";
        input.className = "border rounded px-3 py-2 w-full";
      
        const submitBtn = document.createElement("button");
        submitBtn.type = "submit";
        submitBtn.textContent = "Enviar";
        submitBtn.className = "bg-blue-600 text-white text-center px-4 py-2 rounded";
      
        form.append(input, submitBtn);
      
        form.addEventListener("submit", (e) => {
          e.preventDefault();
          console.log(`Enviado: ${input.value}`);
          input.value = "";
        });
      
        this.bodyEl.appendChild(form);
    }

  }
  