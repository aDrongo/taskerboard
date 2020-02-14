function allowDrop(ev) {
  ev.preventDefault();
}

function drag(ev) {
  ev.dataTransfer.setData("text/plain", ev.target.id);
}

function drop(ev) {
  ev.preventDefault();
  var data = ev.dataTransfer.getData("text/plain");
  ev.target.appendChild(document.getElementById(data));
}

function drop_move(ev) {
  ev.preventDefault();
  var data = ev.dataTransfer.getData("Text");
  ev.target.appendChild(document.getElementById(data))
  var orig_status = new String(ev.srcElement.id.replace("drop",""))
  var id = new String(data.replace("drag",""))
  var status = new String(ev.target.id.replace("drop",""))
  console.log(orig_status)
  console.log(status)
  console.log('test')
  var theUrl = new String(`/api/action=update_ticket&ticket=${id}&status=${status}`)
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function() { 
    if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
      location.reload();
  }
  xmlHttp.open("GET", theUrl, true);
  xmlHttp.send(null);
}

function showDiv(id) {
  if (document.getElementById(id).style.display  == "block") {
    document.getElementById(id).style.display  = "none";
  } else {
    document.getElementById(id).style.display  = "block";
  }
}

function assign(user, id) {
  var theUrl = new String(`/api/action=update_ticket&ticket=${id}&assigned=${user}`)
  console.log(theUrl)
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function() { 
    if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
      location.reload();
  }
  xmlHttp.open("GET", theUrl, true);
  xmlHttp.send(null);
}

function tag(tag, id) {
  var theUrl = new String(`/api/action=update_ticket&ticket=${id}&tags=${tag}`)
  console.log(theUrl)
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function() { 
    if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
      location.reload();
  }
  xmlHttp.open("GET", theUrl, true);
  xmlHttp.send(null);
}

function status(status, id) {
  var theUrl = new String(`/api/action=update_ticket&ticket=${id}&status=${status}`)
  console.log(theUrl)
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function() { 
    if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
      location.reload();
  }
  xmlHttp.open("GET", theUrl, true);
  xmlHttp.send(null);
}

function priority(priority, id) {
  var theUrl = new String(`/api/action=update_ticket&ticket=${id}&priority=${priority}`)
  console.log(theUrl)
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function() { 
    if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
      location.reload();
  }
  xmlHttp.open("GET", theUrl, true);
  xmlHttp.send(null);
}