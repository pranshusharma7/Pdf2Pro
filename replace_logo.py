import os
import re

new_logo_css = """
/* --- BEAUTIFUL STARTUP LOGO REDESIGN --- */
.brand-logo {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 1.45rem !important;
    font-weight: 900 !important;
    letter-spacing: -0.04em !important;
    perspective: 1000px;
    transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.brand-logo:hover {
    transform: scale(1.05);
}

.brand-logo .logo-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275), filter 0.3s;
    position: relative;
}

.brand-logo:hover .logo-icon {
    transform: rotate(-12deg) scale(1.1);
    filter: drop-shadow(0 10px 15px rgba(99, 102, 241, 0.4));
}

/* Pulsing aura */
.brand-logo .logo-icon::after {
    content: '';
    position: absolute;
    width: 100%;
    height: 100%;
    background: radial-gradient(circle, rgba(99,102,241,0.4) 0%, transparent 70%);
    z-index: -1;
    border-radius: 50%;
    opacity: 0;
    transition: opacity 0.3s, transform 0.3s;
    transform: scale(0.5);
}

.brand-logo:hover .logo-icon::after {
    opacity: 1;
    transform: scale(1.8);
}

.logo-text, .brand-logo .logo-text {
    display: flex;
    align-items: center;
    background: linear-gradient(135deg, var(--slate-900) 0%, var(--slate-700) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    transition: all 0.3s ease;
    font-weight: 900;
}

body.dark-mode .logo-text, body.dark-mode .brand-logo .logo-text {
    background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.logo-text span.pro-badge, .brand-logo .logo-text span.pro-badge {
    margin-left: 0.2rem;
    background: linear-gradient(135deg, #ec4899, #8b5cf6, #3b82f6);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-style: italic;
    animation: shine-pro 4s linear infinite;
    padding-right: 5px;
}

@keyframes shine-pro {
    to { background-position: 200% center; }
}

.logo-star {
    transform-origin: 25px 23px; /* Center of star */
    animation: logo-spin 6s linear infinite;
}

@keyframes logo-spin {
    100% { transform: rotate(360deg); }
}

/* Fix CSS empty ruleset if any and override default logo-text span */
.logo-text span {
    color: inherit;
}
/* --- END BEAUTIFUL STARTUP LOGO REDESIGN --- */
"""

new_logo_html = """            <a href="index.html" class="brand-logo">
                <div class="logo-icon">
                    <svg width="44" height="44" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <rect x="4" y="4" width="36" height="36" rx="14" fill="url(#bg-grad-new)" opacity="0.12" />
                        <rect x="8" y="8" width="28" height="28" rx="10" fill="url(#bg-grad-new)" opacity="0.1" />
                        <!-- Soft overlapping document base -->
                        <path d="M12 14C12 11.7909 13.7909 10 16 10H25L32 17V30C32 32.2091 30.2091 34 28 34H16C13.7909 34 12 32.2091 12 30V14Z" fill="url(#doc-grad-new)" />
                        <!-- Elegant fold -->
                        <path d="M25 10V15C25 16.1046 25.8954 17 27 17H32" fill="#fff" fill-opacity="0.2" />
                        <path d="M25 10L32 17" stroke="#fff" stroke-opacity="0.4" stroke-width="1.5" />
                        
                        <!-- Internal design lines for a tech/startup vibe -->
                        <rect x="17" y="18" width="8" height="2" rx="1" fill="#fff" opacity="0.8"/>
                        <rect x="17" y="24" width="11" height="2" rx="1" fill="#fff" opacity="0.8"/>
                        
                        <!-- Premium AI/Startup Spark Component -->
                        <path class="logo-star" d="M25 20L26.5 24L30.5 25.5L26.5 27L25 31L23.5 27L19.5 25.5L23.5 24L25 20Z" fill="url(#spark-grad-new)" filter="drop-shadow(0 0 4px rgba(251,191,36,0.8))"/>
                        <circle cx="25" cy="25.5" r="1.5" fill="#fff" />

                        <defs>
                            <linearGradient id="bg-grad-new" x1="4" y1="4" x2="40" y2="40" gradientUnits="userSpaceOnUse">
                                <stop stop-color="#4f46e5" />
                                <stop offset="1" stop-color="#ec4899" />
                            </linearGradient>
                            <linearGradient id="doc-grad-new" x1="12" y1="10" x2="32" y2="34" gradientUnits="userSpaceOnUse">
                                <stop stop-color="#3b82f6" />
                                <stop offset="1" stop-color="#8b5cf6" />
                            </linearGradient>
                            <linearGradient id="spark-grad-new" x1="19.5" y1="20" x2="30.5" y2="31" gradientUnits="userSpaceOnUse">
                                <stop stop-color="#fbbf24" />
                                <stop offset="1" stop-color="#f59e0b" />
                            </linearGradient>
                        </defs>
                    </svg>
                </div>
                <div class="logo-text">
                    PDF <span class="pro-badge">Pro</span>
                </div>
            </a>"""

def update_html_files():
    directory = '/Volumes/HP USB20FD/PDF CONVERTER PRO copy/'
    
    # Regex to capture the old <a href="..." class="brand-logo"> ... </a>
    logo_re = re.compile(r'<a\s+href="[^"]*"\s+class="brand-logo">.*?</a>', re.DOTALL)
    
    # Regex to catch footer logo separately if it's just <div class="logo-text">PDF <span>Pro</span></div>
    footer_logo_re = re.compile(r'<div\s+class="logo-text">PDF\s*<span>Pro</span></div>', re.DOTALL)
    footer_new = '<div class="logo-text">PDF <span class="pro-badge">Pro</span></div>'

    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            old_content = content
            content = logo_re.sub(new_logo_html, content)
            content = footer_logo_re.sub(footer_new, content)
            
            if content != old_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Updated {filename}")

def append_css():
    css_path = '/Volumes/HP USB20FD/PDF CONVERTER PRO copy/style.css'
    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Only append if not already there
    if "BEAUTIFUL STARTUP LOGO REDESIGN" not in content:
        with open(css_path, 'a', encoding='utf-8') as f:
            f.write("\n" + new_logo_css)
        print("Updated style.css")
        
if __name__ == "__main__":
    update_html_files()
    append_css()
