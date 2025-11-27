class Timer {
  constructor() {
    this.startTime = null;
    this.interval = null;
  }

  start() {
    this.startTime = Date.now();
    this.interval = setInterval(() => this.update(), 10);
  }

  stop() {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
    }
    return Date.now() - this.startTime;
  }

  update() {
    const elapsed = Date.now() - this.startTime;
    const formatted = this.format(elapsed);
    document.getElementById('timer').textContent = formatted;
  }

  format(ms) {
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    const millis = ms % 1000;
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}.${millis.toString().padStart(3, '0')}`;
  }
}
