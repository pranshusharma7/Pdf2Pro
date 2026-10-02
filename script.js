document.addEventListener('DOMContentLoaded', () => {
    // --- Global: Check Auth State ---
    const currentUser = sessionStorage.getItem('currentUser');
    const user = currentUser ? JSON.parse(currentUser) : null;

    // Update Header UI
    const navActions = document.querySelector('.nav-actions');
    if (navActions && user) {
        // Remove Login/Signup buttons
        const loginLink = document.getElementById('nav-login-link');
        const signupBtn = document.getElementById('nav-signup-btn');

        if (loginLink) loginLink.remove();
        if (signupBtn) signupBtn.remove();

        // Determine OAuth provider
        const hasOAuthPic = user.picture && (user.loginMethod === 'google' || user.loginMethod === 'github');

        // Build avatar HTML for trigger
        const triggerAvatarHTML = hasOAuthPic
            ? `<img src="${user.picture}" alt="${user.name}">`
            : `<div class="user-avatar-initial">${user.name.charAt(0).toUpperCase()}</div>`;

        // Build avatar HTML for dropdown
        const dropdownAvatarHTML = hasOAuthPic
            ? `<img src="${user.picture}" alt="${user.name}">`
            : `<div class="dropdown-header-avatar-initial">${user.name.charAt(0).toUpperCase()}</div>`;

        // Build OAuth badge
        let oauthBadgeHTML = '';
        if (user.loginMethod === 'google') {
            oauthBadgeHTML = '<span class="oauth-badge oauth-badge-google">G</span>';
        } else if (user.loginMethod === 'github') {
            oauthBadgeHTML = '<span class="oauth-badge oauth-badge-github">GH</span>';
        }

        // Get first name for compact display
        const firstName = user.name.split(' ')[0];

        // Create professional profile trigger
        const userMenu = document.createElement('div');
        userMenu.className = 'user-profile-trigger';
        userMenu.id = 'userProfileTrigger';

        userMenu.innerHTML = `
            <div class="user-profile-info">
                <div class="user-profile-name">
                    ${firstName} ${oauthBadgeHTML}
                </div>
                <div class="user-profile-role">✦ Pro Member</div>
            </div>
            <div class="user-avatar">
                ${triggerAvatarHTML}
                <div class="user-avatar-status"></div>
            </div>
            <svg class="profile-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="6 9 12 15 18 9"></polyline>
            </svg>

            <!-- Premium Dropdown -->
            <div class="user-dropdown-menu" id="userDropdownMenu">
                <!-- Gradient Header -->
                <div class="dropdown-header">
                    <div class="dropdown-header-avatar">
                        ${dropdownAvatarHTML}
                    </div>
                    <div class="dropdown-header-info">
                        <div class="dropdown-header-name">${user.name}</div>
                        <div class="dropdown-header-email">${user.email}</div>
                        <div class="dropdown-plan-badge">
                            <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2z"/></svg>
                            Pro Plan — Active
                        </div>
                    </div>
                </div>

                <!-- Usage Stats -->
                <div class="dropdown-section" style="padding: 0.6rem 1.2rem;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
                        <span style="font-size:0.72rem;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px;">Conversions Today</span>
                        <span style="font-size:0.72rem;font-weight:700;color:#6366f1;">∞ Unlimited</span>
                    </div>
                    <div style="height:4px;background:var(--border-color);border-radius:4px;overflow:hidden;">
                        <div style="width:100%;height:100%;background:linear-gradient(90deg,#6366f1,#a855f7,#ec4899);border-radius:4px;"></div>
                    </div>
                </div>

                <div class="dropdown-divider"></div>

                <!-- Menu Items -->
                <div class="dropdown-section">
                    <a href="#" class="dropdown-item">
                        <div class="dropdown-item-icon icon-settings">
                            <ion-icon name="settings-outline"></ion-icon>
                        </div>
                        <div class="dropdown-item-text">
                            <div class="dropdown-item-label">Account Settings</div>
                            <div class="dropdown-item-hint">Profile, security & preferences</div>
                        </div>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="opacity:0.35;flex-shrink:0;"><polyline points="9 18 15 12 9 6"></polyline></svg>
                    </a>
                    <a href="subscription.html" class="dropdown-item">
                        <div class="dropdown-item-icon icon-subscription">
                            <ion-icon name="diamond-outline"></ion-icon>
                        </div>
                        <div class="dropdown-item-text">
                            <div class="dropdown-item-label">Subscription</div>
                            <div class="dropdown-item-hint">Manage your Pro plan & billing</div>
                        </div>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="opacity:0.35;flex-shrink:0;"><polyline points="9 18 15 12 9 6"></polyline></svg>
                    </a>
                    <a href="#" class="dropdown-item">
                        <div class="dropdown-item-icon icon-history">
                            <ion-icon name="time-outline"></ion-icon>
                        </div>
                        <div class="dropdown-item-text">
                            <div class="dropdown-item-label">Conversion History</div>
                            <div class="dropdown-item-hint">View & download past conversions</div>
                        </div>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="opacity:0.35;flex-shrink:0;"><polyline points="9 18 15 12 9 6"></polyline></svg>
                    </a>
                </div>

                <div class="dropdown-divider"></div>

                <div class="dropdown-section">
                    <a href="#" class="dropdown-item">
                        <div class="dropdown-item-icon icon-help">
                            <ion-icon name="help-circle-outline"></ion-icon>
                        </div>
                        <div class="dropdown-item-text">
                            <div class="dropdown-item-label">Help & Support</div>
                            <div class="dropdown-item-hint">FAQ, guides & contact us</div>
                        </div>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="opacity:0.35;flex-shrink:0;"><polyline points="9 18 15 12 9 6"></polyline></svg>
                    </a>
                </div>

                <div class="dropdown-divider"></div>

                <div class="dropdown-section">
                    <button class="dropdown-item dropdown-item-logout" id="logout-btn">
                        <div class="dropdown-item-icon icon-logout">
                            <ion-icon name="log-out-outline"></ion-icon>
                        </div>
                        <div class="dropdown-item-text">
                            <div class="dropdown-item-label">Log Out</div>
                            <div class="dropdown-item-hint">See you soon, ${firstName}!</div>
                        </div>
                    </button>
                </div>
            </div>
        `;

        navActions.appendChild(userMenu);

        // Toggle Dropdown with smooth animation
        const trigger = document.getElementById('userProfileTrigger');
        const dropdown = document.getElementById('userDropdownMenu');

        trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdown.classList.toggle('show');
            trigger.classList.toggle('open');
        });

        // Logout Logic
        const logoutBtn = userMenu.querySelector('#logout-btn');
        logoutBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            sessionStorage.removeItem('currentUser');
            window.location.reload();
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!userMenu.contains(e.target)) {
                dropdown.classList.remove('show');
                trigger.classList.remove('open');
            }
        });
    }

    // --- Theme System ---
    const themeToggleBtn = document.getElementById('theme-Toggle');
    const body = document.body;

    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        body.classList.add(savedTheme);
        updateThemeIcon(true);
    } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        body.classList.add('dark-mode');
        updateThemeIcon(true);
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            body.classList.toggle('dark-mode');
            const isDark = body.classList.contains('dark-mode');
            localStorage.setItem('theme', isDark ? 'dark-mode' : '');
            updateThemeIcon(isDark);
        });
    }

    function updateThemeIcon(isDark) {
        if (!themeToggleBtn) return;
        const icon = themeToggleBtn.querySelector('ion-icon');
        if (icon) icon.setAttribute('name', isDark ? 'sunny-outline' : 'moon-outline');
    }

    // --- Sticky Nav Active State on Scroll ---
    const navItems = document.querySelectorAll('.tool-nav-item');
    const sections = document.querySelectorAll('.tool-category-section');

    if (sections.length > 0) {
        window.addEventListener('scroll', () => {
            let current = '';
            sections.forEach(section => {
                const sectionTop = section.offsetTop;
                if (scrollY >= (sectionTop - 150)) {
                    current = '#' + section.getAttribute('id');
                }
            });

            navItems.forEach(item => {
                item.classList.remove('active');
                if (item.getAttribute('href') === current) {
                    item.classList.add('active');
                }
            });
        });
    }

    // --- Smooth Scrolling for Sticky Nav ---
    navItems.forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const target = document.querySelector(targetId);
            if (target) {
                const headerOffset = 130;
                const elementPosition = target.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: "smooth"
                });
            }
        });
    });

    // --- Payment Modal Flow ---
    const modalOverlay = document.getElementById('payment-modal-overlay');
    const openBtns = document.querySelectorAll('.open-payment-modal');
    const closeBtn = document.querySelector('.close-modal');
    const paymentForm = document.getElementById('payment-form');

    openBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            if (user) {
                // If user is already logged in, show payment directly
                if (modalOverlay) {
                    modalOverlay.classList.add('active');
                    document.body.style.overflow = 'hidden';
                    // Auto-fill email
                    const emailInput = modalOverlay.querySelector('input[type="email"]');
                    if (emailInput) emailInput.value = user.email;
                }
            } else {
                // If not logged in, redirect to auth
                window.location.href = 'auth.html';
            }
        });
    });

    const closeModal = () => {
        if (modalOverlay) {
            modalOverlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    };

    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (modalOverlay) {
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) closeModal();
        });
    }

    // Payment Submission
    if (paymentForm) {
        paymentForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const submitBtn = paymentForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;

            submitBtn.textContent = 'Processing...';
            submitBtn.disabled = true;
            submitBtn.style.opacity = '0.7';

            setTimeout(() => {
                submitBtn.textContent = 'Success!';
                submitBtn.style.background = '#10b981';
                setTimeout(() => {
                    closeModal();
                    paymentForm.reset();
                    submitBtn.textContent = originalText;
                    submitBtn.style.background = '';
                    submitBtn.disabled = false;
                    submitBtn.style.opacity = '1';
                    alert('Pro features unlocked! welcome to the Elite Club.');
                }, 1000);
            }, 1500);
        });
    }
});
