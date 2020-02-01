function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    ev.dataTransfer.setData("Text", ev.target.id);
}

function drop(ev) {
    var data = ev.dataTransfer.getData("Text");
    ev.target.appendChild(document.getElementById(data));
    ev.preventDefault();
}
function showDiv() {
  if (document.getElementById('expand').style.display  === "block") {
    document.getElementById('expand').style.display  = "none";
  } else {
    document.getElementById('expand').style.display  = "block";
  }
}
function showDiv1() {
    if (document.getElementById('expand1').style.display  === "block") {
      document.getElementById('expand1').style.display  = "none";
    } else {
      document.getElementById('expand1').style.display  = "block";
    }
  }