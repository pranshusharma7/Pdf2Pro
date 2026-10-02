import os
import re

new_logo_html = """            <a href="index.html" class="brand-logo" style="display: flex; align-items: center; text-decoration: none;">
                <img src="image.png" alt="PDF2Pro Logo" style="height: 46px; width: auto; max-width: 200px; object-fit: contain;">
            </a>"""

footer_new_logo_html = """<div class="footer-brand-logo" style="margin-bottom: 1rem;">
                        <img src="image.png" alt="PDF2Pro Logo" style="height: 40px; width: auto; max-width: 180px; object-fit: contain;">
                    </div>"""

def fix():
    dir_path = '/Volumes/HP USB20FD/PDF CONVERTER PRO copy/'
    
    logo_re = re.compile(r'<a\s+href="[^"]*"\s+class="brand-logo".*?</a>', re.DOTALL)
    
    # Matching existing footer logo variations
    footer_logo_re = re.compile(r'<div\s+class="logo-text">PDF\s*<span[^>]*>.*?</span></div>')
    footer_logo_re2 = re.compile(r'<div\s+class="logo-text">PDF \s*<span>Pro</span></div>')
    footer_logo_re3 = re.compile(r'<div\s+class="logo-text">PDF <span>Pro</span></div>')
    footer_logo_re4 = re.compile(r'<div\s+class="footer-brand-logo".*?</div>', re.DOTALL)

    for filename in os.listdir(dir_path):
        if filename.endswith('.html'):
            filepath = os.path.join(dir_path, filename)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            old = content
            content = logo_re.sub(new_logo_html, content)
            
            # Replace footer logo
            if footer_logo_re4.search(content):
                content = footer_logo_re4.sub(footer_new_logo_html, content)
            else:
                content = footer_logo_re.sub(footer_new_logo_html, content)
                content = footer_logo_re2.sub(footer_new_logo_html, content)
                content = footer_logo_re3.sub(footer_new_logo_html, content)
            
            if content != old:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Updated HTML: {filename}")
                
    # Also clean up the CSS injected previously if possible, to avoid weird styles affecting image.
    css_path = os.path.join(dir_path, 'style.css')
    with open(css_path, 'r', encoding='utf-8', errors='ignore') as f:
        css = f.read()
        
    css_block_re = re.compile(r'/\*\s*---\s*BEAUTIFUL STARTUP LOGO REDESIGN\s*---\s*\*/.*?/\*\s*---\s*END BEAUTIFUL STARTUP LOGO REDESIGN\s*---\s*\*/\n*', re.DOTALL)
    new_css = css_block_re.sub('', css)
    
    if new_css != css:
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(new_css)
        print("Cleaned up custom CSS from style.css")

if __name__ == '__main__':
    fix()
