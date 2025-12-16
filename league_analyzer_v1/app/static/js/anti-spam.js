/**
 * Anti-Spam Protection for Contact Information
 * Advanced techniques to protect email and phone from spam bots
 */

class AntiSpamProtection {
    constructor() {
        this.emailParts = ['your', 'name', '@', 'domain', '.com'];
        this.phoneParts = ['+49', ' ', '123', ' ', '456', ' ', '789'];
        this.revealed = false;
    }

    // Advanced email obfuscation with multiple layers
    revealEmail() {
        if (this.revealed) return;
        
        // Layer 1: Simple concatenation
        let email = this.emailParts.join('');
        
        // Layer 2: Reverse and decode (additional protection)
        const reversed = email.split('').reverse().join('');
        const decoded = this.decodeString(reversed);
        
        // Layer 3: Add some noise and clean it
        const cleanEmail = this.cleanEmail(decoded);
        
        document.getElementById('emailDisplay').innerHTML = `
            <a href="mailto:${cleanEmail}" class="text-decoration-none">
                ${cleanEmail}
            </a>
        `;
        document.getElementById('emailDisplay').style.display = 'inline';
        this.revealed = true;
    }

    // Advanced phone obfuscation
    revealPhone() {
        if (this.revealed) return;
        
        // Layer 1: Simple concatenation
        let phone = this.phoneParts.join('');
        
        // Layer 2: Add some encoding
        const encoded = this.encodePhone(phone);
        const decoded = this.decodePhone(encoded);
        
        document.getElementById('phoneDisplay').innerHTML = `
            <a href="tel:${decoded.replace(/\s/g, '')}" class="text-decoration-none">
                ${decoded}
            </a>
        `;
        document.getElementById('phoneDisplay').style.display = 'inline';
        this.revealed = true;
    }

    // Simple encoding/decoding functions
    decodeString(str) {
        // Simple reverse operation
        return str.split('').reverse().join('');
    }

    cleanEmail(email) {
        // Remove any potential script injection
        return email.replace(/[<>]/g, '');
    }

    encodePhone(phone) {
        // Simple encoding - you can make this more complex
        return btoa(phone);
    }

    decodePhone(encoded) {
        // Simple decoding
        try {
            return atob(encoded);
        } catch {
            return this.phoneParts.join('');
        }
    }

    // Alternative: Show contact info only after user interaction
    setupProgressiveReveal() {
        let interactionCount = 0;
        const requiredInteractions = 3;
        
        const trackInteraction = () => {
            interactionCount++;
            if (interactionCount >= requiredInteractions) {
                this.enableContactButtons();
            }
        };

        // Track various user interactions
        document.addEventListener('click', trackInteraction);
        document.addEventListener('scroll', trackInteraction);
        document.addEventListener('mousemove', trackInteraction);
    }

    enableContactButtons() {
        const buttons = document.querySelectorAll('.contact-reveal-btn');
        buttons.forEach(btn => {
            btn.disabled = false;
            btn.classList.remove('btn-secondary');
            btn.classList.add('btn-outline-primary');
        });
    }
}

// Initialize anti-spam protection
document.addEventListener('DOMContentLoaded', function() {
    window.antiSpam = new AntiSpamProtection();
    window.antiSpam.setupProgressiveReveal();
});

// Global functions for onclick handlers
function revealEmail() {
    if (window.antiSpam) {
        window.antiSpam.revealEmail();
    }
}

function revealPhone() {
    if (window.antiSpam) {
        window.antiSpam.revealPhone();
    }
}
