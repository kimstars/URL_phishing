var background = chrome.extension.getBackgroundPage();
var colors = {
  "-1": "#58bc8a",
  0: "#ffeb3c",
  1: "#ff8b66",
};
var featureList = document.getElementById("features");

chrome.tabs.query({ currentWindow: true, active: true }, function (tabs) {
  var result = background.results[tabs[0].id];
  var isPhish = background.isPhish[tabs[0].id];
  var legitimatePercent = background.legitimatePercents[tabs[0].id];

  // for (var key in result) {
  //     var newFeature = document.createElement("li");
  //     //console.log(key);
  //     newFeature.textContent = key;
  //     //newFeature.className = "rounded";
  //     newFeature.style.backgroundColor = colors[0];
  //     featureList.appendChild(newFeature);
  // }

  $("#site_score").text("SAFE");

  if (isPhish == 'UNSAFE') {
    $("#res-circle").css("background", "#ff8b66");
    $("#site_msg").text("This website is unsafe");
    $("#site_score").text("UNSAFE");
  }
  else if (isPhish == 'SUSPICIOUS') {
    $("#res-circle").css("background", "#ffc107");
    $("#site_msg").text("This website is suspicious");
    $("#site_score").text("SUSPICIOUS");
  }

  // $("#site_score").text(isPhish);
  // $("#site_msg").text(isPhish);
});

document.getElementById("bl_domain1").addEventListener("click", function () {
  chrome.storage.local.get(["blocked"], function (local) {
    const { blocked } = local;
    chrome.tabs.query({ active: true, lastFocusedWindow: true }, (tabs) => {
      let domain = new URL(tabs[0].url);
      blocked.push(domain.hostname);
      chrome.storage.local.set({ blocked });
      chrome.tabs.remove(tabs[0].id);
    });
  });
});
