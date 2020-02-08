function allowDrop(ev) {
  ev.preventDefault();
}

function drag(ev) {
  ev.dataTransfer.setData("Text", ev.target.id);
}

function drop(ev) {
  var data = ev.dataTransfer.getData("Text");
  console.log(data);
  ev.target.appendChild(document.getElementById(data));
  ev.preventDefault();
  console.log(ev.target.id)
}

function drop_move(ev) {
  var data = ev.dataTransfer.getData("Text");
  ev.target.appendChild(document.getElementById(data));
  var id = new String(data.replace("drag",""))
  var status = new String(ev.target.id.replace("drop",""))
  var theUrl = new String(`/api/action=update_ticket&ticket=${id}&status=${status}`)
  console.log(theUrl)
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function() { 
    if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
      location.reload();
  }
  xmlHttp.open("GET", theUrl, true);
  xmlHttp.send(null);
  ev.preventDefault();
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