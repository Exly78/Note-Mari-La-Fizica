/**
 * Main application — wires up tabs, gates, and Schrödinger controls.
 */
(function () {
  // ── Tab switching ──
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.tab;
      tabBtns.forEach(b => b.classList.remove('active'));
      tabContents.forEach(tc => tc.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById('tab-' + target).classList.add('active');
    });
  });

  // ── Tab 1: Qubit Simulator ──
  const blochCanvas = document.getElementById('bloch-canvas');
  BlochRenderer.init(blochCanvas);

  const stateLabel = document.getElementById('state-label');
  const probLabel = document.getElementById('prob-label');

  function updateQubitDisplay() {
    stateLabel.textContent = Quantum.getStateLabel();
    const { p0, p1 } = Quantum.getProbabilities();
    probLabel.textContent = `P(|0⟩) = ${(p0 * 100).toFixed(1)}%   P(|1⟩) = ${(p1 * 100).toFixed(1)}%`;
  }

  document.querySelectorAll('.gate-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const gate = btn.dataset.gate;
      Quantum.applyGate(gate);
      const coords = Quantum.getBlochCoords();
      BlochRenderer.animateTo(coords);
      updateQubitDisplay();
    });
  });

  // ── Tab 2: Schrödinger's Box ──
  const schrodingerCanvas = document.getElementById('schrodinger-canvas');
  SchrodingerSim.init(schrodingerCanvas);

  const timeSlider = document.getElementById('time-slider');
  const timeValue = document.getElementById('time-value');
  const probCircleFill = document.getElementById('prob-circle-fill');
  const probSquareFill = document.getElementById('prob-square-fill');
  const probA = document.getElementById('prob-a');
  const probB = document.getElementById('prob-b');
  const observeBtn = document.getElementById('observe-btn');
  const resultText = document.getElementById('result-text');

  function updateProbDisplay() {
    const p = parseInt(timeSlider.value, 10);
    // Map slider to probability: center = 50/50, edges skew
    const prob = p / 100;
    timeValue.textContent = p + '%';

    SchrodingerSim.setProbability(prob);

    probCircleFill.style.width = (prob * 100) + '%';
    probSquareFill.style.width = ((1 - prob) * 100) + '%';
    probA.textContent = `● Cerc: ${(prob * 100).toFixed(0)}%`;
    probB.textContent = `■ Pătrat: ${((1 - prob) * 100).toFixed(0)}%`;

    // Reset result text and button if probability changed after collapse
    resultText.textContent = '';
    observeBtn.textContent = 'OBSERVĂ';
    observeBtn.classList.remove('collapsed');
  }

  timeSlider.addEventListener('input', updateProbDisplay);
  updateProbDisplay();

  observeBtn.addEventListener('click', () => {
    if (observeBtn.classList.contains('collapsed')) {
      // Reset
      SchrodingerSim.resetState();
      resultText.textContent = '';
      observeBtn.textContent = 'OBSERVĂ';
      observeBtn.classList.remove('collapsed');
      return;
    }

    const result = SchrodingerSim.observe();
    if (result === null) return;

    if (result === 'circle') {
      resultText.textContent = '◉ Funcția de undă a colapsat → CERC';
      resultText.style.color = '#6c63ff';
    } else {
      resultText.textContent = '◼ Funcția de undă a colapsat → PĂTRAT';
      resultText.style.color = '#ff6c63';
    }

    observeBtn.textContent = 'RESETEAZĂ';
    observeBtn.classList.add('collapsed');
  });
})();
