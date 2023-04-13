// Purpose - This file contains all the logic relevant to the extension such as getting the URL, calling the server
// side clientServer.php which then calls the core logic.

function transfer(){	
	var tablink;
	chrome.tabs.getSelected(null,function(tab) {
	   	tablink = tab.url;
		$("#p1").text("The URL being tested is - "+tablink);

		// var xhr=new XMLHttpRequest();
		// params="url="+tablink;
        // alert(params);
		// var markup = "url="+tablink;
		// xhr.open("POST","http://127.0.0.1:5000/extension", false);
		// xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
		// xhr.send(markup);

		var xhr = new XMLHttpRequest();
		alert(tablink);
		a = "http://127.0.0.1:5000/extension?url=" + tablink
		xhr.open("POST", a, false);
		xhr.setRequestHeader('Content-Type', "application/x-www-form-urlencoded");
		xhr.send();

		// Uncomment this line if you see some error on the extension to see the full error message for debugging.
		alert(xhr.responseText);

		$("#div1").text(xhr.responseText);
		return xhr.responseText;
	});
}


$(document).ready(function(){
    $("button").click(function(){	
		var val = transfer();
    });
});

chrome.tabs.getSelected(null,function(tab) {
   	var tablink = tab.url;
	$("#p1").text("The URL being tested is - "+tablink);
});
