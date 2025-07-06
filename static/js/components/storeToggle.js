export function initStoreToggles () {
  document.querySelectorAll(".sensor-component").forEach(card => {
    const sensorId = Number(card.dataset.sensorId);
    const btn      = card.querySelector(".toggle-store-btn");
    const icon     = btn.querySelector(".store-icon");

    // render inicial
    function renderIcon(storeEnabled) {
      icon.src = getImg(storeEnabled ? "check" : "x");
    }
    renderIcon(card.dataset.storeEnabled === "1");

    btn.addEventListener("click", async () => {
      // volvemos a leer el estado **actual**
      const currentlyEnabled = card.dataset.storeEnabled === "1";

      // muestra loading
      icon.src = getImg("loading");
      btn.disabled = true;

      try {
        const res = await fetch(`/api/sensors/${sensorId}/store/`, {
          method : "POST",
          headers: {
            "Content-Type"   : "application/json",
            "X-CSRFToken"    : getCookie("csrftoken"),
            "Accept-Encoding": "gzip, deflate, br"
          },
          body   : JSON.stringify({ store: !currentlyEnabled })
        });

        if (!res.ok) throw new Error(await res.text());
        const data = await res.json();

        // actualizar dataset y rerender
        card.dataset.storeEnabled = data.store ? "1" : "0";
        renderIcon(data.store);
      } catch (e) {
        console.error("toggle store failed:", e);
        // rollback a lo que había
        renderIcon(currentlyEnabled);
      } finally {
        btn.disabled = false;
      }
    });
  });
}

// helpers
function getImg(type) {
  const base = window.STATIC_URL || "/static/";
  return `${base}img/${type}.png`;
}
function getCookie(name) {
  return (document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)"))?.pop() || "";
}
