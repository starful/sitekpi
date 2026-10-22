/* Runs in <head> (not deferred) so the board paints in the right mode without a flash.
   First visit → かんたん (simple). The choice is remembered per browser. */
(function () {
  var mode = "simple";
  try {
    var saved = localStorage.getItem("sitekpi.board.mode");
    if (saved === "simple" || saved === "detail") mode = saved;
  } catch (e) { /* storage blocked: default */ }
  document.documentElement.setAttribute("data-board-mode", mode);
})();
