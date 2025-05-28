export class FormModal {
  /**
   * @param modalId          → id del <div> del modal
   * @param btnOpenId        → id del botón que lo abre
   * @param btnCloseId       → id del botón que lo cierra
   */
  constructor(modalId, btnOpenId, btnCloseId) {
    this.modal     = document.getElementById(modalId);
    this.btnOpen   = document.getElementById(btnOpenId);
    this.btnClose  = document.getElementById(btnCloseId);
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
