class App {
  constructor() {
    this.timer = new Timer();

    // Validate and clamp rounds to available data
    const maxRounds = CHALLENGE_DATA.length;
    const requestedRounds = CONFIG.TOTAL_ROUNDS;
    this.totalRounds = Math.min(Math.max(1, requestedRounds), maxRounds);

    // Slice data to match requested rounds
    const slicedData = CHALLENGE_DATA.slice(0, this.totalRounds);

    this.scoring = new Scoring(this.totalRounds, CONFIG.FIELDS.length);
    this.formManager = new FormManager(CONFIG.FIELDS, slicedData);

    this.bindEvents();
    this.updateRoundDisplay();
  }

  bindEvents() {
    document.getElementById('startBtn').addEventListener('click', () => this.start());
    document.getElementById('challengeForm').addEventListener('submit', (e) => {
      e.preventDefault();
      this.submitForm();
    });
  }

  start() {
    document.getElementById('startBtn').style.display = 'none';
    document.getElementById('challengeForm').style.display = 'block';
    document.querySelector('.congratulations').style.display = 'none';

    this.timer.start();
    this.formManager.reset();
    this.formManager.renderForm();
    this.updateRound();
  }

  submitForm() {
    console.log('[APP] ========== SUBMIT FORM ==========');
    console.log('[APP] Current round before validation:', this.formManager.currentRound);

    const correct = this.formManager.validateRound();
    this.scoring.addRoundScore(correct);

    console.log('[APP] Adding score:', correct);
    console.log('[APP] Total correct so far:', this.scoring.correctFields);

    const hasNext = this.formManager.nextRound();
    console.log('[APP] Has next round?', hasNext);

    if (hasNext) {
      this.updateRound();
    } else {
      this.complete();
    }
    console.log('[APP] =====================================\n');
  }

  updateRound() {
    document.getElementById('round').textContent = this.formManager.currentRound + 1;
    this.updateRoundDisplay();
  }

  updateRoundDisplay() {
    const roundEl = document.getElementById('round');
    if (roundEl) {
      const totalRoundsEl = roundEl.parentElement.querySelector('.total-rounds');
      if (totalRoundsEl) {
        totalRoundsEl.textContent = this.totalRounds;
      }
    }
  }

  complete() {
    const timeMs = this.timer.stop();
    const message = this.scoring.formatResult(timeMs);

    document.getElementById('challengeForm').style.display = 'none';
    document.querySelector('.congratulations').style.display = 'block';
    document.getElementById('resultMessage').textContent = message;

    // Change button to RESET
    const btn = document.getElementById('startBtn');
    btn.textContent = 'RESET';
    btn.style.display = 'block';
    btn.onclick = () => location.reload();
  }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new App();
});
