/**
 * Schrödinger's Box — superposition visualization and wave function collapse.
 */
const SchrodingerSim = (() => {
  let canvas, ctx;
  let probability = 0.5; // probability of "circle" outcome
  let collapsed = false;
  let collapsedResult = null; // 'circle' or 'square'
  let animFrame = 0;
  let running = false;

  // Wave function animation state
  let phase = 0;

  function init(canvasEl) {
    canvas = canvasEl;
    ctx = canvas.getContext('2d');
    running = true;
    animate();
  }

  function setProbability(p) {
    probability = p;
    if (collapsed) {
      // Reset on slider change
      collapsed = false;
      collapsedResult = null;
    }
  }

  function observe() {
    if (collapsed) return null;
    collapsed = true;
    collapsedResult = Math.random() < probability ? 'circle' : 'square';
    return collapsedResult;
  }

  function resetState() {
    collapsed = false;
    collapsedResult = null;
  }

  function drawBox(openAmount) {
    const w = canvas.width;
    const h = canvas.height;
    const cx = w / 2;
    const cy = h / 2;

    // Isometric box parameters
    const bw = 120; // half-width
    const bh = 80;  // half-height
    const bd = 50;   // depth offset

    // Box faces (isometric projection)
    // Front face
    ctx.fillStyle = 'rgba(18, 18, 26, 0.95)';
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
    ctx.lineWidth = 1.5;

    // Bottom face
    ctx.beginPath();
    ctx.moveTo(cx - bw, cy + bh);
    ctx.lineTo(cx + bw, cy + bh);
    ctx.lineTo(cx + bw + bd * 0.6, cy + bh - bd * 0.4);
    ctx.lineTo(cx - bw + bd * 0.6, cy + bh - bd * 0.4);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Front face
    ctx.fillStyle = 'rgba(18, 18, 26, 0.9)';
    ctx.beginPath();
    ctx.moveTo(cx - bw, cy - bh);
    ctx.lineTo(cx + bw, cy - bh);
    ctx.lineTo(cx + bw, cy + bh);
    ctx.lineTo(cx - bw, cy + bh);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Right face
    ctx.fillStyle = 'rgba(14, 14, 22, 0.9)';
    ctx.beginPath();
    ctx.moveTo(cx + bw, cy - bh);
    ctx.lineTo(cx + bw + bd * 0.6, cy - bh - bd * 0.4);
    ctx.lineTo(cx + bw + bd * 0.6, cy + bh - bd * 0.4);
    ctx.lineTo(cx + bw, cy + bh);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Lid (animated open/close)
    const lidAngle = openAmount * 0.7;
    ctx.fillStyle = 'rgba(22, 22, 34, 0.95)';

    ctx.save();
    ctx.beginPath();
    // Top face - tilts back when opening
    const lidY = cy - bh - lidAngle * 80;
    const lidBackY = cy - bh - bd * 0.4 - lidAngle * 120;
    ctx.moveTo(cx - bw, cy - bh - lidAngle * 40);
    ctx.lineTo(cx + bw, cy - bh - lidAngle * 40);
    ctx.lineTo(cx + bw + bd * 0.6, lidBackY);
    ctx.lineTo(cx - bw + bd * 0.6, lidBackY);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    ctx.restore();

    return { cx, cy, bw, bh };
  }

  function drawSuperposition(cx, cy, t) {
    // Two overlapping shapes pulsating — circle and square
    const pulse1 = 0.6 + 0.4 * Math.sin(t * 2);
    const pulse2 = 0.6 + 0.4 * Math.sin(t * 2 + Math.PI);

    // Circle (probability-weighted opacity)
    const circleAlpha = probability * pulse1 * 0.6;
    ctx.shadowColor = '#6c63ff';
    ctx.shadowBlur = 20 * pulse1;
    ctx.strokeStyle = `rgba(108, 99, 255, ${circleAlpha})`;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(cx - 15 * Math.sin(t), cy - 20, 30 + 5 * pulse1, 0, Math.PI * 2);
    ctx.stroke();

    // Square (probability-weighted opacity)
    const squareAlpha = (1 - probability) * pulse2 * 0.6;
    ctx.shadowColor = '#ff6c63';
    ctx.shadowBlur = 20 * pulse2;
    ctx.strokeStyle = `rgba(255, 108, 99, ${squareAlpha})`;
    const sz = 25 + 5 * pulse2;
    ctx.strokeRect(cx + 15 * Math.sin(t) - sz, cy - 20 - sz, sz * 2, sz * 2);

    ctx.shadowBlur = 0;

    // Sine wave above the box
    ctx.strokeStyle = `rgba(108, 99, 255, 0.2)`;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    for (let i = -80; i <= 80; i++) {
      const wx = cx + i;
      const wave = Math.sin(i * 0.05 + t * 3) * 12 * Math.sin(i * 0.02);
      const wy = cy - 90 + wave;
      if (i === -80) ctx.moveTo(wx, wy);
      else ctx.lineTo(wx, wy);
    }
    ctx.stroke();
  }

  function drawCollapsedResult(cx, cy, result) {
    if (result === 'circle') {
      // Solid circle
      ctx.shadowColor = '#6c63ff';
      ctx.shadowBlur = 30;
      ctx.fillStyle = 'rgba(108, 99, 255, 0.8)';
      ctx.strokeStyle = '#6c63ff';
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.arc(cx, cy - 20, 35, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      ctx.shadowBlur = 0;
    } else {
      // Solid square
      ctx.shadowColor = '#ff6c63';
      ctx.shadowBlur = 30;
      ctx.fillStyle = 'rgba(255, 108, 99, 0.8)';
      ctx.strokeStyle = '#ff6c63';
      ctx.lineWidth = 2.5;
      ctx.fillRect(cx - 35, cy - 55, 70, 70);
      ctx.strokeRect(cx - 35, cy - 55, 70, 70);
      ctx.shadowBlur = 0;
    }
  }

  function animate() {
    if (!running) return;
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    phase += 0.02;
    animFrame++;

    const openAmount = collapsed ? 1 : 0;
    const { cx, cy } = drawBox(openAmount);

    if (!collapsed) {
      drawSuperposition(cx, cy, phase);
    } else {
      drawCollapsedResult(cx, cy, collapsedResult);
    }

    requestAnimationFrame(animate);
  }

  function destroy() {
    running = false;
  }

  return { init, setProbability, observe, resetState, destroy };
})();
