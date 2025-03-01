function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function validateNumber(value, defaultValue) {
  const number = parseFloat(value);
  return isNaN(number) ? defaultValue : number;
}

function counter(initialData) {
  return {
    ...initialData,

    increment() {
      this.currentVal = clamp(
        this.currentVal + this.incrementAmount,
        this.minVal,
        this.maxVal,
      );
    },

    decrement() {
      this.currentVal = clamp(
        this.currentVal - this.incrementAmount,
        this.minVal,
        this.maxVal,
      );
    },

    startIncrementing() {
      this.stopCounting(); // Clear any existing intervals or timeouts

      this.timeout = setTimeout(() => {
        let elapsedTime = 0;
        this.interval = setInterval(() => {
          this.increment();
          elapsedTime += 100; // Time passed since last increment
          this.speed = Math.max(
            10,
            100 - Math.floor(elapsedTime / 1000) * this.acceleration,
          );

          clearInterval(this.interval);
          this.interval = setInterval(() => {
            this.increment();
          }, this.speed);
        }, this.speed);
      }, this.delayBeforeStart);
    },

    startDecrementing() {
      this.stopCounting(); // Clear any existing intervals or timeouts

      this.timeout = setTimeout(() => {
        let elapsedTime = 0;
        this.interval = setInterval(() => {
          this.decrement();
          elapsedTime += 100; // Time passed since last decrement
          this.speed = Math.max(
            10,
            100 - Math.floor(elapsedTime / 1000) * this.acceleration,
          );

          clearInterval(this.interval);
          this.interval = setInterval(() => {
            this.decrement();
          }, this.speed);
        }, this.speed);
      }, this.delayBeforeStart);
    },

    stopCounting() {
      if (this.interval) {
        clearInterval(this.interval);
        this.interval = null;
      }
      if (this.timeout) {
        clearTimeout(this.timeout);
        this.timeout = null;
      }
    },

    updateCurrentVal(value) {
      this.currentVal = validateNumber(value, this.currentVal);
    },
  };
}
