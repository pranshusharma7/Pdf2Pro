import os
import re

TOOLS = {
    'pdf-to-word': {
        'title': 'PDF to <span class="text-gradient">Word</span>',
        'desc': 'Convert PDF files to editable Word documents instantly.',
        'icon': 'document-text-outline',
        'types': 'PDF',
        'action_target': 'PDF to Word',
        'action_verb': 'Convert'
    },
    'pdf-to-excel': {
        'title': 'PDF to <span class="text-gradient">Excel</span>',
        'desc': 'Extract tables and data from PDF into Excel spreadsheets.',
        'icon': 'stats-chart-outline',
        'types': 'PDF',
        'action_target': 'PDF to Excel',
        'action_verb': 'Convert'
    },
    'pdf-to-ppt': {
        'title': 'PDF to <span class="text-gradient">PowerPoint</span>',
        'desc': 'Turn PDF pages into editable PPT slides.',
        'icon': 'easel-outline',
        'types': 'PDF',
        'action_target': 'PDF to PowerPoint',
        'action_verb': 'Convert'
    },
    'word-to-pdf': {
        'title': 'Word to <span class="text-gradient">PDF</span>',
        'desc': 'Securely convert DOCX files into high-quality PDFs.',
        'icon': 'document-outline',
        'types': 'DOC, DOCX',
        'action_target': 'Word to PDF',
        'action_verb': 'Convert'
    },
    'excel-to-pdf': {
        'title': 'Excel to <span class="text-gradient">PDF</span>',
        'desc': 'Convert XLS/XLSX spreadsheets to PDF format.',
        'icon': 'grid-outline',
        'types': 'XLS, XLSX',
        'action_target': 'Excel to PDF',
        'action_verb': 'Convert'
    },
    'ppt-to-pdf': {
        'title': 'PPT to <span class="text-gradient">PDF</span>',
        'desc': 'Convert PowerPoint presentations to PDF.',
        'icon': 'easel-outline',
        'types': 'PPT, PPTX',
        'action_target': 'PPT to PDF',
        'action_verb': 'Convert'
    },
    'merge-pdf': {
        'title': '<span class="text-gradient">Merge</span> PDF',
        'desc': 'Combine multiple PDF files into one clean document.',
        'icon': 'git-merge-outline',
        'types': 'PDF',
        'action_target': 'Merge PDF',
        'action_verb': 'Merge'
    },
    'split-pdf': {
        'title': '<span class="text-gradient">Split</span> PDF',
        'desc': 'Extract pages or split a large PDF into smaller files.',
        'icon': 'cut-outline',
        'types': 'PDF',
        'action_target': 'Split PDF',
        'action_verb': 'Split'
    },
    'compress-pdf': {
        'title': '<span class="text-gradient">Compress</span> PDF',
        'desc': 'Reduce the file size of your PDF without losing quality.',
        'icon': 'contract-outline',
        'types': 'PDF',
        'action_target': 'Compress PDF',
        'action_verb': 'Compress'
    },
    'protect-pdf': {
        'title': '<span class="text-gradient">Protect</span> PDF',
        'desc': 'Secure your PDF files with a strong password.',
        'icon': 'lock-closed-outline',
        'types': 'PDF',
        'action_target': 'Protect PDF',
        'action_verb': 'Protect'
    },
    'unlock-pdf': {
        'title': '<span class="text-gradient">Unlock</span> PDF',
        'desc': 'Remove password protection from a PDF document.',
        'icon': 'lock-open-outline',
        'types': 'PDF',
        'action_target': 'Unlock PDF',
        'action_verb': 'Unlock'
    },
    'pdf-to-jpg': {
        'title': 'PDF to <span class="text-gradient">JPG</span>',
        'desc': 'Extract images or save PDF pages as high-quality JPGs.',
        'icon': 'images-outline',
        'types': 'PDF',
        'action_target': 'PDF to JPG',
        'action_verb': 'Convert'
    },
    'pdf-to-png': {
        'title': 'PDF to <span class="text-gradient">PNG</span>',
        'desc': 'Convert PDF to transparent or high-quality PNG images.',
        'icon': 'image-outline',
        'types': 'PDF',
        'action_target': 'PDF to PNG',
        'action_verb': 'Convert'
    },
    'jpg-to-pdf': {
        'title': 'JPG to <span class="text-gradient">PDF</span>',
        'desc': 'Combine multiple JPG images into a single PDF.',
        'icon': 'images-outline',
        'types': 'JPG, JPEG',
        'action_target': 'JPG to PDF',
        'action_verb': 'Convert'
    },
    'edit-pdf': {
        'title': '<span class="text-gradient">Edit</span> PDF',
        'desc': 'Add text, shapes, and annotations directly to your PDF.',
        'icon': 'create-outline',
        'types': 'PDF',
        'action_target': 'Edit PDF',
        'action_verb': 'Edit'
    },
    'sign-pdf': {
        'title': '<span class="text-gradient">Sign</span> PDF',
        'desc': 'Add your electronic signature to any PDF document.',
        'icon': 'pencil-outline',
        'types': 'PDF',
        'action_target': 'Sign PDF',
        'action_verb': 'Sign'
    }
}

def build_pages():
    template_path = 'convert.html'
    if not os.path.exists(template_path):
        print("Error: convert.html template not found!")
        return
        
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # We need to strip out the JS block that tries to modify the DOM dynamically based on urlParams
    # since these are now statically generated correctly.
    js_dynamic_block = re.search(r'// 1\. Dynamic Titles from URL Params.*?// 2\. Drag and Drop Functionality', template, re.DOTALL)
    
    for tool_id, config in TOOLS.items():
        html = template
        
        clean_title = re.sub(r'<[^>]+>', '', config["title"])

        # Title Tag
        html = re.sub(r'<title>.*?</title>', f'<title>{clean_title} - PDF Pro</title>', html)
        
        # Heading Section
        html = re.sub(r'<div class="tool-badge".*?</div>', f'<div class="tool-badge" id="dynamic-tool-badge">\n                        <ion-icon name="{config["icon"]}"></ion-icon> {clean_title}\n                    </div>', html, flags=re.DOTALL)
        html = re.sub(r'<h1 class="hero-heading".*?</h1>', f'<h1 class="hero-heading" id="dynamic-tool-title">\n                        {config["title"]}\n                    </h1>', html, flags=re.DOTALL)
        html = re.sub(r'<p class="hero-subtext".*?</p>', f'<p class="hero-subtext" id="dynamic-tool-desc">\n                        {config["desc"]}\n                    </p>', html, flags=re.DOTALL)
        
        # Supported Types
        html = re.sub(r'Supported: PDF, Word, Excel, PPT, JPG, PNG \(Max 50MB\)', f'Supported: {config["types"]} (Max 50MB)', html)
        
        # Supported Action text
        html = re.sub(r'<span class="options-label" id="dynamic-conversion-label".*?</span>', f'<span class="options-label" id="dynamic-conversion-label"\n                                style="font-size: 1.1rem; color: var(--text-main);">Click {config["action_verb"].lower()} to get your <b>{config["action_target"]}</b></span>', html, flags=re.DOTALL)

        # Main Button Text
        html = re.sub(r'<button class="btn btn-primary btn-lg convert-trigger-btn" id="start-conversion-btn">\s*Convert Now\s*</button>', f'<button class="btn btn-primary btn-lg convert-trigger-btn" id="start-conversion-btn">{config["action_verb"]} Now</button>', html, flags=re.DOTALL)

        # Remove the dynamic JS if found, replace with hardcoded toolId
        if js_dynamic_block:
            html = html.replace(js_dynamic_block.group(0), f"const toolId = '{tool_id}';\n\n            // 2. Drag and Drop Functionality")

        output_filename = f"{tool_id}.html"
        with open(output_filename, 'w', encoding='utf-8') as out:
            out.write(html)
            
        print(f"Generated: {output_filename}")

if __name__ == "__main__":
    build_pages()
