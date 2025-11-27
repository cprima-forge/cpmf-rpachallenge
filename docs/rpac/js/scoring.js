class Scoring {
  constructor(totalRounds, fieldsPerRound) {
    this.totalRounds = totalRounds;
    this.fieldsPerRound = fieldsPerRound;
    this.totalFields = totalRounds * fieldsPerRound;
    this.correctFields = 0;
  }

  addRoundScore(correct) {
    this.correctFields += correct;
  }

  getSuccessRate() {
    return Math.round((this.correctFields / this.totalFields) * 100);
  }

  formatResult(timeMs) {
    const rate = this.getSuccessRate();
    return `Your success rate is ${rate}% (${this.correctFields} out of ${this.totalFields} fields) in ${timeMs} milliseconds`;
  }
}
