/**
 * Buxoro Test System - Main JavaScript
 * Professional test examination system functionality
 */

class TestSystem {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeComponents();
    }

    setupEventListeners() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initTooltips();
            this.initModals();
            this.setupFormValidation();
        });
    }

    initializeComponents() {
        // Initialize Bootstrap components
        this.initTooltips();
        this.initModals();
    }

    initTooltips() {
        // Initialize Bootstrap tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    initModals() {
        // Initialize Bootstrap modals
        const modalTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="modal"]'));
        modalTriggerList.map(function (modalTriggerEl) {
            return new bootstrap.Modal(modalTriggerEl);
        });
    }

    setupFormValidation() {
        // Add form validation
        const forms = document.querySelectorAll('.needs-validation');
        Array.prototype.slice.call(forms).forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    }
}

class TestInterface {
    constructor(testId, timeLimit) {
        this.testId = testId;
        this.timeLimit = timeLimit; // in seconds
        this.timeRemaining = timeLimit;
        this.currentQuestion = 0;
        this.answers = {};
        this.isSubmitted = false;
        this.autoSaveInterval = null;
        this.heartbeatInterval = null;
        this.focusLostCount = 0;
        this.suspiciousActivity = [];
        
        this.init();
    }

    init() {
        this.setupTimer();
        this.setupAutoSave();
        this.setupHeartbeat();
        this.setupAntiCheat();
        this.setupNavigation();
        this.loadSavedAnswers();
    }

    setupTimer() {
        const timerElement = document.getElementById('timer');
        if (!timerElement) return;

        this.timerInterval = setInterval(() => {
            if (this.timeRemaining <= 0) {
                this.autoSubmitTest();
                return;
            }

            this.timeRemaining--;
            this.updateTimerDisplay();
            
            // Warning when 5 minutes left
            if (this.timeRemaining <= 300) {
                timerElement.classList.add('timer-warning');
            }
        }, 1000);

        this.updateTimerDisplay();
    }

    updateTimerDisplay() {
        const timerElement = document.getElementById('timer');
        if (!timerElement) return;

        const hours = Math.floor(this.timeRemaining / 3600);
        const minutes = Math.floor((this.timeRemaining % 3600) / 60);
        const seconds = this.timeRemaining % 60;

        let display = '';
        if (hours > 0) {
            display = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        } else {
            display = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }

        timerElement.textContent = display;
    }

    setupAutoSave() {
        // Auto-save every 30 seconds
        this.autoSaveInterval = setInterval(() => {
            this.saveAnswers();
        }, 30000);

        // Save on answer change
        document.addEventListener('change', (e) => {
            if (e.target.closest('.question-container')) {
                this.saveCurrentAnswer();
                this.saveAnswers();
            }
        });
    }

    setupHeartbeat() {
        // Send heartbeat every 60 seconds
        this.heartbeatInterval = setInterval(() => {
            this.sendHeartbeat();
        }, 60000);
    }

    setupAntiCheat() {
        // Monitor window focus
        window.addEventListener('blur', () => {
            this.focusLostCount++;
            this.suspiciousActivity.push({
                type: 'focus_lost',
                timestamp: new Date().toISOString(),
                count: this.focusLostCount
            });
            
            this.showFocusWarning();
        });

        window.addEventListener('focus', () => {
            this.hideFocusWarning();
        });

        // Disable right-click context menu
        document.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            this.suspiciousActivity.push({
                type: 'right_click_attempt',
                timestamp: new Date().toISOString()
            });
        });

        // Disable common keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Disable F12, Ctrl+Shift+I, Ctrl+U, etc.
            if (e.key === 'F12' || 
                (e.ctrlKey && e.shiftKey && e.key === 'I') ||
                (e.ctrlKey && e.key === 'u')) {
                e.preventDefault();
                this.suspiciousActivity.push({
                    type: 'dev_tools_attempt',
                    timestamp: new Date().toISOString(),
                    key: e.key
                });
            }
        });

        // Enter fullscreen mode
        this.enterFullscreen();
    }

    setupNavigation() {
        // Question navigation
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('question-number')) {
                const questionIndex = parseInt(e.target.dataset.questionIndex);
                this.goToQuestion(questionIndex);
            }
        });

        // Previous/Next buttons
        const prevBtn = document.getElementById('prev-question');
        const nextBtn = document.getElementById('next-question');

        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.previousQuestion());
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.nextQuestion());
        }

        // Submit button
        const submitBtn = document.getElementById('submit-test');
        if (submitBtn) {
            submitBtn.addEventListener('click', () => this.submitTest());
        }
    }

    saveCurrentAnswer() {
        const questionContainer = document.querySelector('.question-container.active');
        if (!questionContainer) return;

        const questionId = questionContainer.dataset.questionId;
        const questionType = questionContainer.dataset.questionType;
        
        let answer = null;

        switch (questionType) {
            case 'single_choice':
                const radioInput = questionContainer.querySelector('input[type="radio"]:checked');
                answer = radioInput ? radioInput.value : null;
                break;

            case 'multiple_choice':
                const checkboxInputs = questionContainer.querySelectorAll('input[type="checkbox"]:checked');
                answer = Array.from(checkboxInputs).map(input => input.value);
                break;

            case 'true_false':
                const booleanInput = questionContainer.querySelector('input[type="radio"]:checked');
                answer = booleanInput ? booleanInput.value : null;
                break;

            case 'numeric':
                const numericInput = questionContainer.querySelector('input[type="number"]');
                answer = numericInput ? parseFloat(numericInput.value) : null;
                break;

            case 'text':
            case 'essay':
                const textInput = questionContainer.querySelector('textarea, input[type="text"]');
                answer = textInput ? textInput.value.trim() : null;
                break;
        }

        if (answer !== null && answer !== '' && answer.length !== 0) {
            this.answers[questionId] = {
                answer: answer,
                questionType: questionType,
                timestamp: new Date().toISOString()
            };
            
            // Update question navigation indicator
            this.updateQuestionStatus(questionId, 'answered');
        }
    }

    async saveAnswers() {
        if (this.isSubmitted) return;

        try {
            const response = await fetch(`/api/tests/attempts/${this.attemptId}/auto-save/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({
                    answers: this.answers,
                    current_question: this.currentQuestion,
                    time_remaining: this.timeRemaining,
                    suspicious_activity: this.suspiciousActivity
                })
            });

            if (response.ok) {
                console.log('Answers auto-saved successfully');
            }
        } catch (error) {
            console.error('Auto-save failed:', error);
        }
    }

    async sendHeartbeat() {
        if (this.isSubmitted) return;

        try {
            await fetch(`/api/tests/attempts/${this.attemptId}/heartbeat/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({
                    timestamp: new Date().toISOString(),
                    window_focus: document.hasFocus(),
                    time_remaining: this.timeRemaining
                })
            });
        } catch (error) {
            console.error('Heartbeat failed:', error);
        }
    }

    goToQuestion(index) {
        // Save current answer before switching
        this.saveCurrentAnswer();

        // Hide all questions
        const questions = document.querySelectorAll('.question-container');
        questions.forEach(q => q.classList.remove('active'));

        // Show target question
        const targetQuestion = document.querySelector(`[data-question-index="${index}"]`);
        if (targetQuestion) {
            targetQuestion.classList.add('active');
            this.currentQuestion = index;
            this.updateNavigationButtons();
            this.updateProgressBar();
        }
    }

    previousQuestion() {
        if (this.currentQuestion > 0) {
            this.goToQuestion(this.currentQuestion - 1);
        }
    }

    nextQuestion() {
        const totalQuestions = document.querySelectorAll('.question-container').length;
        if (this.currentQuestion < totalQuestions - 1) {
            this.goToQuestion(this.currentQuestion + 1);
        }
    }

    updateNavigationButtons() {
        const prevBtn = document.getElementById('prev-question');
        const nextBtn = document.getElementById('next-question');
        const totalQuestions = document.querySelectorAll('.question-container').length;

        if (prevBtn) {
            prevBtn.disabled = this.currentQuestion === 0;
        }

        if (nextBtn) {
            nextBtn.disabled = this.currentQuestion === totalQuestions - 1;
        }
    }

    updateProgressBar() {
        const progressBar = document.querySelector('.progress-bar');
        if (progressBar) {
            const totalQuestions = document.querySelectorAll('.question-container').length;
            const progress = ((this.currentQuestion + 1) / totalQuestions) * 100;
            progressBar.style.width = `${progress}%`;
            progressBar.setAttribute('aria-valuenow', progress);
        }
    }

    updateQuestionStatus(questionId, status) {
        const questionNumber = document.querySelector(`[data-question-id="${questionId}"]`);
        if (questionNumber) {
            questionNumber.classList.remove('answered', 'unanswered', 'marked');
            questionNumber.classList.add(status);
        }
    }

    showFocusWarning() {
        const warning = document.createElement('div');
        warning.id = 'focus-warning';
        warning.className = 'focus-warning';
        warning.innerHTML = `
            <div>
                <h2><i class="fas fa-exclamation-triangle"></i> Diqqat!</h2>
                <p>Test oynasidan chiqish taqiqlanadi. Iltimos, testga qaytishni bosing.</p>
                <p>Focus yo'qolgan soni: ${this.focusLostCount}</p>
                <button class="btn btn-warning btn-lg" onclick="document.getElementById('focus-warning').remove()">
                    Testga qaytish
                </button>
            </div>
        `;
        document.body.appendChild(warning);
    }

    hideFocusWarning() {
        const warning = document.getElementById('focus-warning');
        if (warning) {
            warning.remove();
        }
    }

    enterFullscreen() {
        const elem = document.documentElement;
        if (elem.requestFullscreen) {
            elem.requestFullscreen();
        } else if (elem.mozRequestFullScreen) {
            elem.mozRequestFullScreen();
        } else if (elem.webkitRequestFullscreen) {
            elem.webkitRequestFullscreen();
        }
    }

    async submitTest() {
        if (this.isSubmitted) return;

        // Show confirmation dialog
        if (!confirm('Testni tugatishni xohlaysizmi? Bu amalni bekor qilib bo\'lmaydi.')) {
            return;
        }

        this.isSubmitted = true;
        
        // Save final answers
        this.saveCurrentAnswer();
        
        // Clear intervals
        clearInterval(this.timerInterval);
        clearInterval(this.autoSaveInterval);
        clearInterval(this.heartbeatInterval);

        try {
            const response = await fetch(`/api/tests/attempts/${this.attemptId}/submit/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({
                    answers: this.answers,
                    time_spent: this.timeLimit - this.timeRemaining,
                    suspicious_activity: this.suspiciousActivity,
                    focus_lost_count: this.focusLostCount
                })
            });

            if (response.ok) {
                const result = await response.json();
                window.location.href = `/tests/results/${result.attempt_id}/`;
            } else {
                throw new Error('Submit failed');
            }
        } catch (error) {
            console.error('Test submission failed:', error);
            alert('Test topshirishda xatolik yuz berdi. Iltimos, qayta urinib ko\'ring.');
            this.isSubmitted = false;
        }
    }

    autoSubmitTest() {
        this.submitTest();
    }

    loadSavedAnswers() {
        // Load previously saved answers from server
        // This would be called when resuming a test
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
}

// Utility Functions
const Utils = {
    // Format time duration
    formatDuration(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;

        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    },

    // Show toast notification
    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        // Remove after hiding
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1080';
        document.body.appendChild(container);
        return container;
    },

    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Copy to clipboard
    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showToast('Clipboard ga nusxalandi', 'success');
        }).catch(() => {
            this.showToast('Nusxalashda xatolik', 'error');
        });
    }
};

// Initialize system
const testSystem = new TestSystem();

// Export for global use
window.TestSystem = TestSystem;
window.TestInterface = TestInterface;
window.Utils = Utils;
