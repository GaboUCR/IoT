export class FormModal {
    constructor() {
      this.modal = document.getElementById("form-modal");
      this.btnOpen = document.getElementById("open-form-modal");
      this.btnClose = document.getElementById("close-form-modal");
  
      this.init();
    }
  
    init() {
      if (!this.modal || !this.btnOpen || !this.btnClose) return;
  
      this.btnOpen.addEventListener("click", () => this.open());
      this.btnClose.addEventListener("click", () => this.close());
  
      // Cerrar haciendo clic fuera del modal
      this.modal.addEventListener("click", (e) => {
        if (e.target === this.modal) this.close();
      });
    }
  
    open() {
      this.modal.classList.remove("hidden");
    }
  
    close() {
      this.modal.classList.add("hidden");
    }
  }
  