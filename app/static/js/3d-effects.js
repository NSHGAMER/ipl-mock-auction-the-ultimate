// 3D Interactive Effects for IPL Mock Auction

document.addEventListener('DOMContentLoaded', function() {
    // Initialize 3D card hover effects
    initializeCardHoverEffects();
    
    // Initialize parallax scrolling
    initializeParallax();
    
    // Enhanced animations
    initializeEnhancedAnimations();
    
    // Mouse tracking for 3D depth effect
    initializeMouseTracking();
    
    // scroll tilt and nav tilt
    initializeScrollTilt();
    initializeNavTilt();
});

// 3D Card Hover Effects
function initializeCardHoverEffects() {
    const cards = document.querySelectorAll('.player-card, .college-card, .card');
    
    cards.forEach(card => {
        card.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / 10;
            const rotateY = (centerX - x) / 10;
            
            this.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.05)`;
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale(1)';
        });
    });
}

// Parallax Scrolling Effect
function initializeParallax() {
    const parallaxElements = document.querySelectorAll('[data-parallax]');
    
    if (parallaxElements.length === 0) return;
    
    window.addEventListener('scroll', function() {
        const scrollY = window.pageYOffset;
        parallaxElements.forEach(element => {
            const speed = parseFloat(element.dataset.parallax || 0.5);
            const yPos = scrollY * speed;
            element.style.transform = `translateY(${yPos}px) translateZ(-${scrollY * 0.1}px)`; // add subtle depth shift
        });
    });
}

// Rotate main container on scroll for 3D effect
function initializeScrollTilt() {
    const container = document.querySelector('.container');
    if (!container) return;
    window.addEventListener('scroll', () => {
        const maxTilt = 5; // degrees
        const scrollPct = window.pageYOffset / (document.body.scrollHeight - window.innerHeight);
        const tilt = (scrollPct - 0.5) * maxTilt * 2; // center around 0
        container.style.transform = `rotateX(${tilt}deg)`;
    });
}

// add nav tilt on hover
function initializeNavTilt() {
    const navLinks = document.querySelectorAll('nav a');
    navLinks.forEach(link => {
        link.addEventListener('mousemove', (e) => {
            const rect = link.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width/2;
            const y = e.clientY - rect.top - rect.height/2;
            const tiltX = (y / rect.height) * 10;
            const tiltY = (x / rect.width) * -10;
            link.style.transform = `perspective(500px) rotateX(${tiltX}deg) rotateY(${tiltY}deg)`;
        });
        link.addEventListener('mouseleave', () => {
            link.style.transform = '';
        });
    });
}

// Enhanced Animations with Anime.js
function initializeEnhancedAnimations() {
    // Staggered animations for player cards
    if (typeof anime !== 'undefined') {
        const playerCards = document.querySelectorAll('.player-card');
        
        anime.set(playerCards, {
            opacity: 0,
            scale: 0.5
        });
        
        anime({
            targets: playerCards,
            opacity: [0, 1],
            scale: [0.5, 1],
            rotate: [0, 0],
            duration: 800,
            easing: 'easeOutElastic(1, .6)',
            delay: anime.stagger(50)
        });
        
        // Continuous floating animation
        anime({
            targets: playerCards,
            translateY: [0, -10],
            duration: 3000,
            easing: 'easeInOutQuad',
            direction: 'alternate',
            loop: true,
            delay: anime.stagger(100)
        });
    }
}

// Mouse Tracking for Depth Effects
function initializeMouseTracking() {
    const container = document.querySelector('.players-grid') || document.querySelector('.container');
    
    if (!container) return;
    
    let mouseX = 0;
    let mouseY = 0;
    
    document.addEventListener('mousemove', function(e) {
        mouseX = e.clientX / window.innerWidth;
        mouseY = e.clientY / window.innerHeight;
        
        // Apply subtle light effect based on mouse position
        const cards = document.querySelectorAll('.player-card');
        cards.forEach(card => {
            const lightIntensity = 0.05;
            const bgColor = `linear-gradient(${mouseX * 90}deg, rgba(255, 107, 53, ${lightIntensity * mouseX}), rgba(247, 147, 30, ${lightIntensity * mouseY}))`;
            // Subtle effect without breaking the existing gradient
        });
    });
}

// Scroll animations
window.addEventListener('scroll', function() {
    const elements = document.querySelectorAll('[data-scroll-animate]');
    
    elements.forEach(element => {
        const elementPosition = element.getBoundingClientRect().top;
        const screenPosition = window.innerHeight / 1.3;
        
        if (elementPosition < screenPosition) {
            element.classList.add('active');
        }
    });
});

// Add glow effect on scroll
window.addEventListener('scroll', function() {
    const cards = document.querySelectorAll('.card');
    
    cards.forEach(card => {
        const rect = card.getBoundingClientRect();
        const isVisible = rect.top < window.innerHeight && rect.bottom > 0;
        
        if (isVisible) {
            card.style.opacity = '1';
        }
    });
});

// Animate on page load
window.addEventListener('load', function() {
    // Fade in nav
    const nav = document.querySelector('nav');
    if (nav) {
        nav.style.animation = 'fadeIn 0.6s ease-out';
    }
    
    // Cascade animation for alerts
    const alerts = document.querySelectorAll('.alert');
    if (typeof anime !== 'undefined' && alerts.length) {
        anime({
            targets: alerts,
            translateX: [-30, 0],
            opacity: [0, 1],
            duration: 600,
            easing: 'easeOutExpo',
            delay: anime.stagger(100)
        });
    }
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href !== '#') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    });
});

// Add CSS classes for animations
function addAnimationClasses() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInLeft {
            from {
                opacity: 0;
                transform: translateX(-50px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(50px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes float {
            0%, 100% {
                transform: translateY(0px);
            }
            50% {
                transform: translateY(-20px);
            }
        }
        
        .slide-in-left {
            animation: slideInLeft 0.6s ease-out forwards;
        }
        
        .slide-in-right {
            animation: slideInRight 0.6s ease-out forwards;
        }
        
        .float {
            animation: float 3s ease-in-out infinite;
        }
    `;
    document.head.appendChild(style);
}

addAnimationClasses();

// Ripple effect on button click
const buttons = document.querySelectorAll('button');
buttons.forEach(button => {
    button.addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.style.position = 'absolute';
        ripple.style.borderRadius = '50%';
        ripple.style.background = 'rgba(255, 255, 255, 0.5)';
        ripple.style.pointerEvents = 'none';
        ripple.style.transform = 'scale(0)';
        ripple.style.animation = 'rippleEffect 0.6s ease-out';
        
        this.style.position = 'relative';
        this.style.overflow = 'hidden';
        this.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    });
});

// Add ripple animation
const style = document.createElement('style');
style.textContent = `
    @keyframes rippleEffect {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
