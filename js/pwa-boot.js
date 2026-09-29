window.SK = window.SK || {};
SK.pwa = SK.pwa || { deferred: null };
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js", { scope: "/" }).catch(function () {});
}
window.addEventListener("beforeinstallprompt", function (e) {
  e.preventDefault();
  SK.pwa = SK.pwa || {};
  SK.pwa.deferred = e;
});
window.addEventListener("appinstalled", function () {
  SK.pwa = SK.pwa || {};
  SK.pwa.deferred = null;
  try { localStorage.setItem("sk-pwa-installed", "1"); } catch (err) {}
});
