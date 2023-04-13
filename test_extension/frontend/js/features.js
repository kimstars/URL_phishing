var result = {};

// lấy url
url = window.location.href;

result["url"] = url;
// Length Of Url
result["url_length"] = url.length;
// Length of Hostname
result["hostname_length"] = window.location.hostname.length;
// Length Of Path
result["path_length"] = window.location.pathname.length;
// Length Of First Directory
result["fd_length"] = window.location.pathname.split("/")[1].length;
// Length Of Top Level Domain
result["tld_length"] = window.location.origin.split(".").pop().length;
// Count Of '-'
//resuls = (url.match(/-/g) || []).length
result["count-"] = url.split("-").length - 1;
// Count Of '@'
//(url.match(/@/g) || []).length
result["count@"] = url.split("@").length - 1;
// Count Of '?'
result["count?"] = url.split("?").length - 1;
// Count Of '%'
result["count%"] = url.split("%").length - 1;
// Count Of '.'
result["count."] = url.split(".").length - 1;
// Count Of '='
result["count="] = url.split("=").length - 1;
// Count Of 'http'
result["count//"] = url.split("//").length - 1;
// Count Of 'https'
result["count-https"] = url.split("https").length - 1;
// Count Of 'www'
result["count-www"] = url.split("www").length - 1;
// Count Of Digits
result["count-digits"] = url.replace(/[^0-9]/g, "").length;
// Count Of Letters
result["count-letters"] =
  url.replace(/[^A-Z]/g, "").length + url.replace(/[^a-z]/g, "").length;
// Count Of Number Of Directories
result["count_dir"] = location.pathname.split("/").length - 1;
// Use of IP or not
var urlDomain = window.location.hostname;

var patt = /(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[0-9]?[0-9])(\.|$){4}/;
var patt2 = /(0x([0-9][0-9]|[A-F][A-F]|[A-F][0-9]|[0-9][A-F]))(\.|$){4}/;
var ip = /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/;

if (ip.test(urlDomain) || patt.test(urlDomain) || patt2.test(urlDomain)) {
  result["use_of_ip"] = -1;
} else {
  result["use_of_ip"] = 1;
}
// Use of Shortening URL or not
var re =
  /(bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|db\.tt|qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|q\.gs|is\.gd|po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|x\.co|prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|tr\.im|link\.zip\.net)/;

if (url.search(re) == -1) {
  result["short_url"] = 1;
} else {
  result["short_url"] = -1;
}

//---------------------- Sending the result  ----------------------

chrome.runtime.sendMessage(result, function (response) {
  console.log(result);
  //console.log(response);
});

chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  if (request.action == "alert_user") {
    alert("Nguyen Anh Dung !!!");
    // window.open("https://www.w3schools.com");
  }
  if (request.type === "popup-modal") {
    showModal();
  }
});

const showModal = () => {
  const modal = document.createElement("dialog");
  modal.setAttribute(
    "style",
    `
        padding: 5px 10px;
        width: 500px;
        z-index: 100;
        border: solid 1px #000;
        border-radius: 10px;
        position: fixed;  
        bottom: 30%;
        font-family: 'Franklin Gothic Medium', 'Arial Narrow', Arial, sans-serif;
        box-shadow: 10px 10px 10px #423a3a;
        `
  );
  modal.id = "modal-warning";
  modal.innerHTML = `           
        <div style="
            text-align: center;
            margin:30px 0px 20px;
            font-weight:600;
            color:#db270f;
            font-size:30px">
            This website is UNSAFE
        </div>
        <div style=" 
            display: flex;
            justify-content: center;
            color:white;
            margin: 10px 10px 20px">
            <button id="button-cancel" style="
                    margin: 10px 30px ;
                    font-size:20px;
                    background-color:#ff2614;
                    border: none;color: white;
                    cursor: pointer;
                    outline: none;
                    padding: 8px;border-radius:10px;">CANCEL</button>
            <button id="button-back" style = "
                    margin: 10px 30px;
                    font-size:20px;
                    background-color:#6291d9;
                    border: none;
                    color: white;
                    padding: 8px;
                    cursor: pointer;
                    outline: none;
                    border-radius:10px;">BACK</button>
            <button id="button-block" style = "
                    margin: 10px 30px;
                    font-size:20px;
                    background-color:#198754;
                    border: none;
                    color: white;
                    padding: 8px;
                    cursor: pointer;
                    outline: none;
                    border-radius:10px;">BLOCK</button>
        </div>
    `;
  document.body.appendChild(modal);
  const dialog = document.querySelector("dialog");

  dialog.showModal();
  // const iframe = document.getElementById("popup-content");
  // iframe.src = chrome.extension.getURL("index.html");
  // iframe.frameBorder = 0;
  document.getElementById("button-cancel").addEventListener("click", () => {
    dialog.close();
  });
  console.log(history.length);
  if (history.length <= 1) {
    document
      .getElementById("button-back")
      .setAttribute("style", `display:none;`);
  }
  document.getElementById("button-back").addEventListener("click", () => {
    history.back();
  });
  document
    .getElementById("button-block")
    .addEventListener("click", function () {
      chrome.storage.local.get(["blocked"], function (local) {
        const { blocked } = local;
        let domain = new URL(window.location.href);
        blocked.push(domain.hostname);
        chrome.storage.local.set({ blocked });
      });
      history.back();
    });
};
