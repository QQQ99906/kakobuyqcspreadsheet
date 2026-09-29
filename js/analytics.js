/* kakobuyqcspreadsheet.com — Firebase Analytics / GA4 (kakobuywebsite) */
(function () {
  var firebaseConfig = {
    apiKey: "AIzaSyCjVTTHt-nDqR3bPYLQKV45F41tVpTOxBk",
    authDomain: "kakobuywebsite.firebaseapp.com",
    projectId: "kakobuywebsite",
    storageBucket: "kakobuywebsite.firebasestorage.app",
    messagingSenderId: "588401556889",
    appId: "1:588401556889:web:7f2a1040a423b4a961a708",
    measurementId: "G-J7XGTCP578",
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
