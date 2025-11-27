class FormManager {
  constructor(fields, data) {
    this.fields = fields;
    this.data = data;
    this.currentRound = 0;
  }

  renderForm() {
    const form = document.getElementById('challengeForm');
    form.innerHTML = '';

    // Fisher-Yates shuffle
    const shuffled = [...this.fields].sort(() => Math.random() - 0.5);

    shuffled.forEach(field => {
      const div = document.createElement('div');
      div.className = 'form-row';

      const label = document.createElement('label');
      label.textContent = field.label;

      const input = document.createElement('input');
      input.setAttribute('ng-reflect-name', field.name);
      input.type = 'text';
      input.required = true;

      div.appendChild(label);
      div.appendChild(input);
      form.appendChild(div);
    });

    const submit = document.createElement('input');
    submit.type = 'submit';
    submit.value = 'Submit';
    form.appendChild(submit);
  }

  validateRound() {
    const currentData = this.data[this.currentRound];
    let correct = 0;

    console.log(`[VALIDATE] Round ${this.currentRound + 1}, Expected data:`, currentData);

    this.fields.forEach(field => {
      const input = document.querySelector(`[ng-reflect-name="${field.name}"]`);
      const expected = currentData[field.excelCol];
      const actual = input ? input.value.trim() : '<not found>';
      const match = input && input.value.trim() === expected.trim();

      console.log(`  ${field.excelCol}: expected="${expected}" actual="${actual}" match=${match}`);

      if (match) {
        correct++;
      }
    });

    console.log(`[VALIDATE] Correct: ${correct}/${this.fields.length}`);
    return correct;
  }

  nextRound() {
    this.currentRound++;
    if (this.currentRound < this.data.length) {
      this.renderForm();
      return true;
    }
    return false;
  }

  reset() {
    this.currentRound = 0;
  }
}
