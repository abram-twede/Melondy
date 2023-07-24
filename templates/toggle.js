function toggleText() {
  var text = document.getElementById("add");
  console.log(text); // Should log the HTML element, or null if not found.
  if (text.style.display === "none") {
    text.style.display = "block";
  } else {
    text.style.display = "none";
  }
  console.log(text.style.display); // Should log the new display style.
}