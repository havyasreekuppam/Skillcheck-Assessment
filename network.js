// Animation Background Code (UNCHANGED)
const canvas = document.getElementById("network");
const ctx = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

window.addEventListener("resize", () => {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
});

let nodes = Array.from({ length: 50 }, () => ({
  x: Math.random() * canvas.width,
  y: Math.random() * canvas.height,
  dx: (Math.random() - 0.5) * 1.2,
  dy: (Math.random() - 0.5) * 1.2
}));

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#fff";
  
  nodes.forEach(node => {
    ctx.beginPath();
    ctx.arc(node.x, node.y, 2, 0, Math.PI * 2);
    ctx.fill();
    
    node.x += node.dx;
    node.y += node.dy;
    
    if (node.x < 0 || node.x > canvas.width) node.dx *= -1;
    if (node.y < 0 || node.y > canvas.height) node.dy *= -1;
    
    nodes.forEach(other => {
      let dist = Math.hypot(node.x - other.x, node.y - other.y);
      if (dist < 120) {
        ctx.strokeStyle = "rgba(255,255,255,0.2)";
        ctx.beginPath();
        ctx.moveTo(node.x, node.y);
        ctx.lineTo(other.x, other.y);
        ctx.stroke();
      }
    });
  });
}

setInterval(draw, 30);


// ✅ ATS Score Fetch Logic (NEW)
document.getElementById("atsForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const resume = document.getElementById("resumeText").value;

  const response = await fetch("/api/ats-score", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume })
  });

  const data = await response.json();
  const score = data.score ?? 0;

  document.getElementById("scoreValue").innerText = score + "%";
  document.querySelector(".ats-score-fill").style.width = score + "%";
});
