/**
 * Quantum math engine using math.js for complex number / matrix operations.
 * Tracks a single-qubit state vector |ψ⟩ = α|0⟩ + β|1⟩
 * and computes Bloch sphere coordinates.
 */
const Quantum = (() => {
  const C = math.complex;
  const SQRT2_INV = 1 / Math.sqrt(2);

  // Gate matrices (2×2 complex)
  const GATES = {
    H: math.matrix([
      [C(SQRT2_INV, 0), C(SQRT2_INV, 0)],
      [C(SQRT2_INV, 0), C(-SQRT2_INV, 0)]
    ]),
    X: math.matrix([
      [C(0, 0), C(1, 0)],
      [C(1, 0), C(0, 0)]
    ]),
    Z: math.matrix([
      [C(1, 0), C(0, 0)],
      [C(0, 0), C(-1, 0)]
    ]),
    Y: math.matrix([
      [C(0, 0), C(0, -1)],
      [C(0, 1), C(0, 0)]
    ]),
    S: math.matrix([
      [C(1, 0), C(0, 0)],
      [C(0, 0), C(0, 1)]
    ]),
    T: math.matrix([
      [C(1, 0), C(0, 0)],
      [C(0, 0), C(Math.cos(Math.PI / 4), Math.sin(Math.PI / 4))]
    ])
  };

  // State: column vector [α, β]
  let state = math.matrix([[C(1, 0)], [C(0, 0)]]);

  function reset() {
    state = math.matrix([[C(1, 0)], [C(0, 0)]]);
  }

  function applyGate(gateName) {
    if (gateName === 'RESET') {
      reset();
      return;
    }
    const gate = GATES[gateName];
    if (!gate) return;
    state = math.multiply(gate, state);
  }

  function getState() {
    const alpha = state.get([0, 0]);
    const beta = state.get([1, 0]);
    return { alpha, beta };
  }

  /**
   * Convert state vector to Bloch sphere coordinates (θ, φ).
   * |ψ⟩ = cos(θ/2)|0⟩ + e^{iφ} sin(θ/2)|1⟩
   * Returns { theta, phi, x, y, z } where (x,y,z) is the Bloch vector.
   */
  function getBlochCoords() {
    const { alpha, beta } = getState();

    const absAlpha = math.abs(alpha);
    const absBeta = math.abs(beta);

    // θ from |α| = cos(θ/2)
    const theta = 2 * Math.acos(Math.min(1, absAlpha));

    // φ = arg(β) - arg(α)
    let phi = 0;
    if (absBeta > 1e-10) {
      phi = math.arg(beta) - math.arg(alpha);
    }

    const x = Math.sin(theta) * Math.cos(phi);
    const y = Math.sin(theta) * Math.sin(phi);
    const z = Math.cos(theta);

    return { theta, phi, x, y, z };
  }

  function getProbabilities() {
    const { alpha, beta } = getState();
    const p0 = Math.pow(math.abs(alpha), 2);
    const p1 = Math.pow(math.abs(beta), 2);
    return { p0, p1 };
  }

  function getStateLabel() {
    const { alpha, beta } = getState();

    function fmtComplex(c) {
      const re = c.re;
      const im = c.im;
      if (Math.abs(im) < 1e-6) return re.toFixed(2);
      if (Math.abs(re) < 1e-6) return im.toFixed(2) + 'i';
      const sign = im >= 0 ? '+' : '-';
      return `${re.toFixed(2)}${sign}${Math.abs(im).toFixed(2)}i`;
    }

    return `|ψ⟩ = (${fmtComplex(alpha)})|0⟩ + (${fmtComplex(beta)})|1⟩`;
  }

  return { applyGate, getState, getBlochCoords, getProbabilities, getStateLabel, reset };
})();
