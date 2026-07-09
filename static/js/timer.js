// timer.js - For the meditation timer functionality

class MeditationTimer {
    constructor(displayElement, startButton, pauseButton, resetButton, soundToggle) {
        this.displayElement = displayElement;
        this.startButton = startButton;
        this.pauseButton = pauseButton;
        this.resetButton = resetButton;
        this.soundToggle = soundToggle;
        
        this.duration = 5 * 60; // Default: 5 minutes in seconds
        this.remainingTime = this.duration;
        this.isRunning = false;
        this.interval = null;
        this.soundEnabled = true;
        
        this.initAudio();
        this.updateDisplay();
        this.initEventListeners();
    }
    
    initAudio() {
        // Bell sound for start, intervals and end
        this.bellSound = new Audio('https://soundbible.com/mp3/meditation-bell-sound_daniel-simion.mp3');
        
        // Ambient background sound
        this.ambientSound = new Audio('https://soundbible.com/mp3/ambient-loop_daniel-simion.mp3');
        this.ambientSound.loop = true;
        this.ambientSound.volume = 0.3;
    }
    
    initEventListeners() {
        this.startButton.addEventListener('click', () => this.start());
        this.pauseButton.addEventListener('click', () => this.pause());
        this.resetButton.addEventListener('click', () => this.reset());
        this.soundToggle.addEventListener('change', () => {
            this.soundEnabled = this.soundToggle.checked;
            if (!this.soundEnabled && this.ambientSound) {
                this.ambientSound.pause();
            } else if (this.soundEnabled && this.isRunning && this.ambientSound) {
                this.ambientSound.play();
            }
        });
        
        // Duration selection
        const durationButtons = document.querySelectorAll('.duration-btn');
        durationButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const minutes = parseInt(e.target.dataset.minutes);
                this.setDuration(minutes * 60);
                
                // Update active state
                durationButtons.forEach(btn => btn.classList.remove('active'));
                e.target.classList.add('active');
            });
        });
    }
    
    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    
    updateDisplay() {
        this.displayElement.textContent = this.formatTime(this.remainingTime);
        
        // Update progress circle if it exists
        const progressCircle = document.querySelector('.progress-ring-circle');
        if (progressCircle) {
            const radius = progressCircle.r.baseVal.value;
            const circumference = radius * 2 * Math.PI;
            
            const progress = this.remainingTime / this.duration;
            const dashoffset = circumference * (1 - progress);
            
            progressCircle.style.strokeDasharray = `${circumference} ${circumference}`;
            progressCircle.style.strokeDashoffset = dashoffset;
        }
    }
    
    setDuration(seconds) {
        // Only allow changing duration when timer is not running
        if (!this.isRunning) {
            this.duration = seconds;
            this.remainingTime = seconds;
            this.updateDisplay();
        }
    }
    
    start() {
        if (!this.isRunning) {
            // Play starting bell
            if (this.soundEnabled && this.bellSound) {
                this.bellSound.play();
            }
            
            // Start ambient sound
            if (this.soundEnabled && this.ambientSound) {
                this.ambientSound.play();
            }
            
            this.isRunning = true;
            this.startButton.disabled = true;
            this.pauseButton.disabled = false;
            
            // Update button text
            this.startButton.innerHTML = '<i class="bi bi-play-fill"></i> Resume';
            
            this.interval = setInterval(() => {
                this.remainingTime--;
                
                // Play interval bell at certain points if enabled
                if (this.soundEnabled && this.bellSound && 
                   (this.remainingTime === Math.floor(this.duration / 2) || // halfway point
                    this.remainingTime === 60)) { // one minute remaining
                    this.bellSound.currentTime = 0;
                    this.bellSound.play();
                }
                
                this.updateDisplay();
                
                if (this.remainingTime <= 0) {
                    this.complete();
                }
            }, 1000);
        }
    }
    
    pause() {
        if (this.isRunning) {
            clearInterval(this.interval);
            this.isRunning = false;
            this.startButton.disabled = false;
            this.pauseButton.disabled = true;
            
            // Pause ambient sound
            if (this.ambientSound) {
                this.ambientSound.pause();
            }
        }
    }
    
    reset() {
        clearInterval(this.interval);
        this.isRunning = false;
        this.remainingTime = this.duration;
        this.updateDisplay();
        
        this.startButton.disabled = false;
        this.pauseButton.disabled = true;
        this.startButton.innerHTML = '<i class="bi bi-play-fill"></i> Start';
        
        // Stop ambient sound
        if (this.ambientSound) {
            this.ambientSound.pause();
            this.ambientSound.currentTime = 0;
        }
    }
    
    complete() {
        clearInterval(this.interval);
        this.isRunning = false;
        
        // Play ending bell (3 times)
        if (this.soundEnabled && this.bellSound) {
            this.playEndingBells(3);
        }
        
        // Stop ambient sound
        if (this.ambientSound) {
            // Fade out ambient sound
            const fadeInterval = setInterval(() => {
                if (this.ambientSound.volume > 0.1) {
                    this.ambientSound.volume -= 0.1;
                } else {
                    this.ambientSound.pause();
                    this.ambientSound.volume = 0.3; // Reset volume for next session
                    clearInterval(fadeInterval);
                }
            }, 100);
        }
        
        // Show completion message
        const completionMessage = document.getElementById('completionMessage');
        if (completionMessage) {
            completionMessage.classList.remove('d-none');
            setTimeout(() => {
                completionMessage.classList.add('d-none');
            }, 5000);
        }
        
        this.startButton.disabled = false;
        this.pauseButton.disabled = true;
        this.startButton.innerHTML = '<i class="bi bi-play-fill"></i> Start';
    }
    
    playEndingBells(count) {
        let bellCount = 0;
        
        const playBell = () => {
            this.bellSound.currentTime = 0;
            this.bellSound.play();
            bellCount++;
            
            if (bellCount < count) {
                setTimeout(playBell, 3000);
            }
        };
        
        playBell();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const timerDisplay = document.getElementById('timerDisplay');
    const startButton = document.getElementById('startTimer');
    const pauseButton = document.getElementById('pauseTimer');
    const resetButton = document.getElementById('resetTimer');
    const soundToggle = document.getElementById('soundToggle');
    
    if (timerDisplay && startButton && pauseButton && resetButton && soundToggle) {
        const meditationTimer = new MeditationTimer(
            timerDisplay, 
            startButton, 
            pauseButton, 
            resetButton, 
            soundToggle
        );
        
        // Disable pause button initially
        pauseButton.disabled = true;
    }
});
