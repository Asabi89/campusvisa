// CampusVisa - Main JavaScript

document.addEventListener('DOMContentLoaded', function () {

    // ── Mobile Menu ──────────────────────────────────────────
    const menuBtn = document.getElementById('mobile-menu-btn');
    const closeBtn = document.getElementById('mobile-close-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    const overlay = document.getElementById('mobile-overlay');
    const bar1 = document.getElementById('bar-1');
    const bar2 = document.getElementById('bar-2');
    const bar3 = document.getElementById('bar-3');
    const hasMobileMenu = menuBtn && closeBtn && mobileMenu && overlay && bar1 && bar2 && bar3;

    function openMenu() {
        if (!hasMobileMenu) return;
        mobileMenu.classList.remove('translate-x-full');
        mobileMenu.classList.add('translate-x-0');
        overlay.classList.remove('opacity-0', 'pointer-events-none');
        overlay.classList.add('opacity-100', 'pointer-events-auto');
        document.body.style.overflow = 'hidden';
        // Hamburger → X animation
        bar1.classList.add('rotate-45', 'translate-y-[7px]');
        bar2.classList.add('opacity-0', 'scale-x-0');
        bar3.classList.add('-rotate-45', '-translate-y-[7px]');
    }

    function closeMenu() {
        if (!hasMobileMenu) return;
        mobileMenu.classList.add('translate-x-full');
        mobileMenu.classList.remove('translate-x-0');
        overlay.classList.add('opacity-0', 'pointer-events-none');
        overlay.classList.remove('opacity-100', 'pointer-events-auto');
        document.body.style.overflow = '';
        // X → Hamburger animation
        bar1.classList.remove('rotate-45', 'translate-y-[7px]');
        bar2.classList.remove('opacity-0', 'scale-x-0');
        bar3.classList.remove('-rotate-45', '-translate-y-[7px]');
    }

    if (hasMobileMenu) {
        menuBtn.addEventListener('click', openMenu);
        closeBtn.addEventListener('click', closeMenu);
        overlay.addEventListener('click', closeMenu);

        // Close on Escape key
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') closeMenu();
        });
    }

    // ── Global Dropdown Icon State ────────────────────────────
    const globalNavMenu = document.getElementById('global-nav-menu');
    const hamburgerIcon = document.getElementById('menu-icon-hamburger');
    const openBookIcon = document.getElementById('menu-icon-book-open');
    const closedBookIcon = document.getElementById('menu-icon-book-closed');

    if (globalNavMenu && hamburgerIcon && openBookIcon && closedBookIcon) {
        var hasBeenOpened = false;

        function syncGlobalMenuIcon() {
            if (globalNavMenu.open) {
                hasBeenOpened = true;
                hamburgerIcon.classList.add('hidden');
                closedBookIcon.classList.add('hidden');
                openBookIcon.classList.remove('hidden');
                return;
            }

            openBookIcon.classList.add('hidden');
            if (hasBeenOpened) {
                hamburgerIcon.classList.add('hidden');
                closedBookIcon.classList.remove('hidden');
            } else {
                closedBookIcon.classList.add('hidden');
                hamburgerIcon.classList.remove('hidden');
            }
        }

        globalNavMenu.addEventListener('toggle', syncGlobalMenuIcon);
        syncGlobalMenuIcon();
    }

    // ── Navbar Scroll Effect ─────────────────────────────────
    const navbar = document.getElementById('navbar');
    if (navbar) {
        function updateNavbar() {
            if (window.scrollY > 10) {
                navbar.classList.add('shadow-md', 'border-b', 'border-gray-100', 'bg-white/95');
                navbar.classList.remove('bg-white/80');
            } else {
                navbar.classList.remove('shadow-md', 'border-b', 'border-gray-100', 'bg-white/95');
                navbar.classList.add('bg-white/80');
            }
        }
        window.addEventListener('scroll', updateNavbar, { passive: true });
        updateNavbar();
    }

    // ── Auto-dismiss Messages ────────────────────────────────
    var messages = document.querySelectorAll('#messages-container > div');
    messages.forEach(function (msg, index) {
        setTimeout(function () {
            msg.style.transition = 'opacity 0.3s, transform 0.3s';
            msg.style.opacity = '0';
            msg.style.transform = 'translateX(100%)';
            setTimeout(function () { msg.remove(); }, 300);
        }, 5000 + (index * 500));
    });

    // ── Cookie Banner ───────────────────────────────────────
    var cookieBanner = document.getElementById('cookie-banner');
    var cookieModal = document.getElementById('cookie-modal');
    var cookieKey = 'campusvisa_cookie_consent_v2';

    if (cookieBanner) {
        var cookieInputs = {
            analytics: cookieModal ? cookieModal.querySelector('[data-cookie-option="analytics"]') : null,
            personalization: cookieModal ? cookieModal.querySelector('[data-cookie-option="personalization"]') : null,
            marketing: cookieModal ? cookieModal.querySelector('[data-cookie-option="marketing"]') : null,
        };

        function defaultConsent() {
            return {
                essential: true,
                analytics: false,
                personalization: false,
                marketing: false,
            };
        }

        function normalizeConsent(rawValue) {
            if (!rawValue) return null;

            // Backward compatibility with v1 string values.
            if (rawValue === 'accept') {
                return {
                    essential: true,
                    analytics: true,
                    personalization: true,
                    marketing: true,
                };
            }
            if (rawValue === 'decline') {
                return defaultConsent();
            }

            try {
                var parsed = JSON.parse(rawValue);
                return {
                    essential: true,
                    analytics: !!parsed.analytics,
                    personalization: !!parsed.personalization,
                    marketing: !!parsed.marketing,
                };
            } catch (err) {
                return null;
            }
        }

        function readStorage() {
            try {
                return window.localStorage.getItem(cookieKey) || window.localStorage.getItem('campusvisa_cookie_consent_v1');
            } catch (err) {
                return null;
            }
        }

        function applyConsentToUI(consent) {
            if (cookieInputs.analytics) cookieInputs.analytics.checked = !!consent.analytics;
            if (cookieInputs.personalization) cookieInputs.personalization.checked = !!consent.personalization;
            if (cookieInputs.marketing) cookieInputs.marketing.checked = !!consent.marketing;
        }

        function readConsentFromUI() {
            return {
                essential: true,
                analytics: !!(cookieInputs.analytics && cookieInputs.analytics.checked),
                personalization: !!(cookieInputs.personalization && cookieInputs.personalization.checked),
                marketing: !!(cookieInputs.marketing && cookieInputs.marketing.checked),
            };
        }

        function publishConsent(consent) {
            window.CampusVisaCookieConsent = consent;
            window.dispatchEvent(new CustomEvent('campusvisa:cookie-consent', { detail: consent }));
        }

        function openCookieModal() {
            if (!cookieModal) return;
            cookieModal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
        }

        function closeCookieModal() {
            if (!cookieModal) return;
            cookieModal.classList.add('hidden');
            document.body.style.overflow = '';
        }

        function persistAndClose(consent, source) {
            var payload = {
                essential: true,
                analytics: !!consent.analytics,
                personalization: !!consent.personalization,
                marketing: !!consent.marketing,
                source: source,
                saved_at: new Date().toISOString(),
            };
            try {
                window.localStorage.setItem(cookieKey, JSON.stringify(payload));
            } catch (err) {
                // Ignore storage errors; banner still closes.
            }
            publishConsent(payload);
            cookieBanner.classList.add('hidden');
            closeCookieModal();
        }

        var stored = normalizeConsent(readStorage());
        if (stored) {
            publishConsent(stored);
            cookieBanner.classList.add('hidden');
            closeCookieModal();
        } else {
            var initial = defaultConsent();
            applyConsentToUI(initial);
            cookieBanner.classList.remove('hidden');
            closeCookieModal();
        }

        var cookieButtons = document.querySelectorAll('#cookie-banner [data-cookie-action], #cookie-modal [data-cookie-action]');
        cookieButtons.forEach(function (btn) {
            btn.addEventListener('click', function () {
                var action = btn.getAttribute('data-cookie-action') || 'save_selection';
                if (action === 'open_customize') {
                    openCookieModal();
                    return;
                }

                if (action === 'close_modal') {
                    closeCookieModal();
                    return;
                }

                if (action === 'accept_all') {
                    var all = {
                        essential: true,
                        analytics: true,
                        personalization: true,
                        marketing: true,
                    };
                    applyConsentToUI(all);
                    persistAndClose(all, action);
                    return;
                }

                if (action === 'reject_optional') {
                    var requiredOnly = defaultConsent();
                    applyConsentToUI(requiredOnly);
                    persistAndClose(requiredOnly, action);
                    return;
                }

                var selected = readConsentFromUI();
                persistAndClose(selected, action);
            });
        });

        if (cookieModal) {
            cookieModal.addEventListener('click', function (ev) {
                if (ev.target === cookieModal) {
                    closeCookieModal();
                }
            });
        }
    }
});
