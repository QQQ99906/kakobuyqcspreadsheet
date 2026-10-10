/* kakobuyqcspreadsheet.com — Firebase Analytics / GA4 (kweb-f6d3e) */
(function () {
  var firebaseConfig = {
    apiKey: "AIzaSyD5n5wQ7utyLFG5Jm6mhIRtPZrP-_f7FH4",
    authDomain: "kweb-f6d3e.firebaseapp.com",
    projectId: "kweb-f6d3e",
    storageBucket: "kweb-f6d3e.firebasestorage.app",
    messagingSenderId: "830362085247",
    appId: "1:830362085247:web:c80d6b8bb065a3d0189c4a",
    measurementId: "G-X7K28JSWBB",
  };

  var MEASUREMENT_ID = firebaseConfig.measurementId;
  window.SK_FIREBASE = firebaseConfig;
  window.SK = window.SK || {};
  window.SK.analyticsId = MEASUREMENT_ID;

  window.dataLayer = window.dataLayer || [];
  function gtag() {
    window.dataLayer.push(arguments);
  }
  window.gtag = window.gtag || gtag;
  gtag("js", new Date());
  gtag("config", MEASUREMENT_ID, {
    send_page_view: true,
    cookie_flags: "SameSite=None;Secure",
  });

  var s = document.createElement("script");
  s.async = true;
  s.src = "https://www.googletagmanager.com/gtag/js?id=" + MEASUREMENT_ID;
  document.head.appendChild(s);

  var mod = document.createElement("script");
  mod.type = "module";
  mod.textContent =
    'import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.0/firebase-app.js";\n' +
    'import { getAnalytics } from "https://www.gstatic.com/firebasejs/11.6.0/firebase-analytics.js";\n' +
    "const firebaseConfig = " +
    JSON.stringify(firebaseConfig) +
    ";\n" +
    "const app = initializeApp(firebaseConfig);\n" +
    "window.SK.firebaseApp = app;\n" +
    "window.SK.firebaseAnalytics = getAnalytics(app);\n";
  document.head.appendChild(mod);
})();
