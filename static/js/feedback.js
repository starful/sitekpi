/* 「ご意見」: open the dialog from the rail, send 👍/👎 + one line to /feedback. */
(function () {
  const dlg = document.getElementById("feedback");
  if (!dlg) return;
  const form = dlg.querySelector("[data-feedback-form]");
  const msg = dlg.querySelector("[data-feedback-msg]");
  const send = form.querySelector(".fb-send");
  document.addEventListener("click", (e) => {
    if (e.target.closest("[data-feedback-open]")) {
      form.reset(); msg.textContent = ""; send.disabled = false;
      dlg.showModal();
    }
    if (e.target.closest("[data-feedback-close]")) dlg.close();
  });
  dlg.addEventListener("click", (e) => { if (e.target === dlg) dlg.close(); });
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    const body = {
      vote: fd.get("vote") || "", comment: (fd.get("comment") || "").toString().trim(),
      website: fd.get("website") || "", screen: dlg.dataset.screen || "", path: location.pathname,
    };
    if (!body.vote && !body.comment) return;
    send.disabled = true;
    try {
      const r = await fetch("/feedback", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      if (!r.ok) throw new Error(String(r.status));
      msg.textContent = msg.dataset.ok;
      setTimeout(() => dlg.close(), 1200);
    } catch (_) {
      msg.textContent = msg.dataset.err; send.disabled = false;
    }
  });
})();
