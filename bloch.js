/**
 * Bloch sphere renderer on a 2D canvas.
 * Draws a wireframe sphere with the qubit state vector, animated transitions.
 */
const BlochRenderer = (() => {
  let canvas, ctx;
  let currentCoords = { x: 0, y: 0, z: 1 }; // start at |0⟩
  let targetCoords = { x: 0, y: 0, z: 1 };
  let animating = false;
  const ANIM_DURATION = 400; // ms
  let animStart = 0;

  const SPHERE_RADIUS = 140;
  const TILT = 0.35; // isometric tilt angle (radians)

  function init(canvasEl) {
    canvas = canvasEl;
    ctx = canvas.getContext('2d');
    draw(currentCoords);
  }

  /**
   * Project 3D Bloch coordinates to 2D canvas.
   * Simple orthographic with slight tilt for depth.
   */
  function project(x, y, z) {
    const cosT = Math.cos(TILT);
    const sinT = Math.sin(TILT);
    const px = x;
    const py = -z * cosT + y * sinT;
    return {
      x: canvas.width / 2 + px * SPHERE_RADIUS,
      y: canvas.height / 2 + py * SPHERE_RADIUS
    };
  }

  function draw(coords) {
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    const cx = w / 2;
    const cy = h / 2;
    const r = SPHERE_RADIUS;

    // Subtle glow behind sphere
    const glow = ctx.createRadialGradient(cx, cy, r * 0.2, cx, cy, r * 1.5);
    glow.addColorStop(0, 'rgba(108, 99, 255, 0.06)');
    glow.addColorStop(1, 'rgba(108, 99, 255, 0)');
    ctx.fillStyle = glow;
    ctx.fillRect(0, 0, w, h);

    // Draw sphere outline
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();

    // Draw equator ellipse (tilted)
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
    ctx.beginPath();
    ctx.ellipse(cx, cy, r, r * Math.sin(TILT), 0, 0, Math.PI * 2);
    ctx.stroke();

    // Draw meridian (front half visible)
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
    ctx.beginPath();
    ctx.ellipse(cx, cy, r * 0.02, r, 0, 0, Math.PI * 2);
    ctx.stroke();

    // Axes (X, Y, Z) as dashed lines
    ctx.setLineDash([4, 4]);
    ctx.lineWidth = 0.8;

    // Z axis (vertical)
    const zTop = project(0, 0, 1);
    const zBot = project(0, 0, -1);
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.beginPath();
    ctx.moveTo(zTop.x, zTop.y);
    ctx.lineTo(zBot.x, zBot.y);
    ctx.stroke();

    // X axis
    const xP = project(1, 0, 0);
    const xN = project(-1, 0, 0);
    ctx.beginPath();
    ctx.moveTo(xP.x, xP.y);
    ctx.lineTo(xN.x, xN.y);
    ctx.stroke();

    // Y axis
    const yP = project(0, 1, 0);
    const yN = project(0, -1, 0);
    ctx.beginPath();
    ctx.moveTo(yP.x, yP.y);
    ctx.lineTo(yN.x, yN.y);
    ctx.stroke();

    ctx.setLineDash([]);

    // Axis labels
    ctx.font = '12px monospace';
    ctx.fillStyle = 'rgba(255, 255, 255, 0.35)';
    ctx.fillText('|0⟩', zTop.x + 6, zTop.y - 4);
    ctx.fillText('|1⟩', zBot.x + 6, zBot.y + 14);
    ctx.fillText('+X', xP.x + 6, xP.y);
    ctx.fillText('+Y', yP.x + 6, yP.y);

    // State vector
    const tip = project(coords.x, coords.y, coords.z);

    // Vector line
    ctx.strokeStyle = '#6c63ff';
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(tip.x, tip.y);
    ctx.stroke();

    // Tip dot with glow
    ctx.shadowColor = '#6c63ff';
    ctx.shadowBlur = 16;
    ctx.fillStyle = '#6c63ff';
    ctx.beginPath();
    ctx.arc(tip.x, tip.y, 6, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;

    // Small origin dot
    ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.beginPath();
    ctx.arc(cx, cy, 3, 0, Math.PI * 2);
    ctx.fill();
  }

  function easeInOutCubic(t) {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  }

  function lerp(a, b, t) {
    return a + (b - a) * t;
  }

  function animateStep(timestamp) {
    if (!animStart) animStart = timestamp;
    const elapsed = timestamp - animStart;
    const progress = Math.min(1, elapsed / ANIM_DURATION);
    const eased = easeInOutCubic(progress);

    const interp = {
      x: lerp(currentCoords.x, targetCoords.x, eased),
      y: lerp(currentCoords.y, targetCoords.y, eased),
      z: lerp(currentCoords.z, targetCoords.z, eased)
    };

    // Normalize to keep on sphere surface
    const mag = Math.sqrt(interp.x ** 2 + interp.y ** 2 + interp.z ** 2);
    if (mag > 0.001) {
      interp.x /= mag;
      interp.y /= mag;
      interp.z /= mag;
    }

    draw(interp);

    if (progress < 1) {
      requestAnimationFrame(animateStep);
    } else {
      currentCoords = { ...targetCoords };
      animating = false;
    }
  }

  function animateTo(newCoords) {
    targetCoords = { ...newCoords };
    animStart = 0;
    animating = true;
    requestAnimationFrame(animateStep);
  }

  function updateImmediate(coords) {
    currentCoords = { ...coords };
    targetCoords = { ...coords };
    draw(coords);
  }

  return { init, animateTo, updateImmediate, draw };
})();
