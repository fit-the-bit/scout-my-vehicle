import os
import subprocess
from PIL import Image

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
IMAGES_DIR = os.path.join(PROJECT_DIR, "app", "static", "images")
TEMP_HTML_DIR = os.path.join(os.environ.get("TEMP", "."), "svm_logo_gen")
os.makedirs(TEMP_HTML_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
USER_DATA_DIR = os.path.join(TEMP_HTML_DIR, "chrome_profile")

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700;800;900&display=swap" rel="stylesheet">
  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    html, body {
      width: 1200px;
      height: 1200px;
      overflow: hidden;
      background: transparent;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      -webkit-font-smoothing: antialiased;
    }
    .logo-container {
      display: inline-flex;
      flex-direction: column;
      align-items: stretch;
      width: max-content;
    }
    .brand-title {
      font-size: 110px;
      font-weight: 900;
      letter-spacing: -0.015em;
      line-height: 1.05;
      color: {{TITLE_COLOR}};
      white-space: nowrap;
    }
    .red-accent {
      color: #c0262b;
    }
    .tagline-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
      font-size: 47px;
      font-weight: 800;
      text-transform: uppercase;
      color: {{TAGLINE_COLOR}};
      margin-top: 14px;
      line-height: 1;
    }
    .tagline-pipe {
      color: #c0262b;
      font-weight: 900;
    }
  </style>
</head>
<body>
  <div class="logo-container">
    <div class="brand-title">
      <span class="red-accent">S</span>cout<span class="red-accent">M</span>y<span class="red-accent">V</span>ehicle
    </div>
    <div class="tagline-row">
      <span>FIND</span>
      <span class="tagline-pipe">|</span>
      <span>VERIFY</span>
      <span class="tagline-pipe">|</span>
      <span>DRIVE</span>
    </div>
  </div>
</body>
</html>
"""

def render_html_to_png(html_content, temp_name):
    html_path = os.path.join(TEMP_HTML_DIR, f"{temp_name}.html")
    raw_png_path = os.path.join(TEMP_HTML_DIR, f"{temp_name}_raw.png")
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    cmd = [
        "cmd", "/c", "start", "/wait", "",
        CHROME_PATH,
        "--headless=new",
        f"--user-data-dir={USER_DATA_DIR}",
        f"--screenshot={raw_png_path}",
        "--window-size=1200,1200",
        "--default-background-color=00000000",
        f"file:///{html_path.replace(os.sep, '/')}"
    ]
    subprocess.run(cmd, check=True)
    return raw_png_path

def create_1x1(raw_png_path, output_path, bg_color=None, target_size=1024, content_width=840):
    img = Image.open(raw_png_path).convert("RGBA")
    bbox = img.getbbox()
    if not bbox:
        raise ValueError("Image appears empty")
        
    cropped = img.crop(bbox)
    w, h = cropped.size
    
    # Scale so cropped width matches content_width
    scale = content_width / float(w)
    new_w = int(round(w * scale))
    new_h = int(round(h * scale))
    resized = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Create final 1:1 canvas
    if bg_color:
        final_img = Image.new("RGBA", (target_size, target_size), bg_color)
    else:
        final_img = Image.new("RGBA", (target_size, target_size), (0, 0, 0, 0))
        
    pos_x = (target_size - new_w) // 2
    pos_y = (target_size - new_h) // 2
    
    final_img.paste(resized, (pos_x, pos_y), resized)
    final_img.save(output_path, "PNG")
    print(f"Generated: {output_path} (Size: {target_size}x{target_size})")

def main():
    # 1. Light theme (Dark text, for transparent & white background)
    light_html = HTML_TEMPLATE.replace("{{TITLE_COLOR}}", "#0f172a").replace("{{TAGLINE_COLOR}}", "#1e293b")
    raw_light = render_html_to_png(light_html, "light")
    
    # Generate transparent 1:1
    out_transparent = os.path.join(IMAGES_DIR, "svm_logo_text_1x1.png")
    create_1x1(raw_light, out_transparent, bg_color=None)
    
    # Generate white background 1:1
    out_white = os.path.join(IMAGES_DIR, "svm_logo_text_white_1x1.png")
    create_1x1(raw_light, out_white, bg_color=(255, 255, 255, 255))
    
    # 2. Dark theme (White text, for dark background & dark transparent)
    dark_html = HTML_TEMPLATE.replace("{{TITLE_COLOR}}", "#ffffff").replace("{{TAGLINE_COLOR}}", "#a1a1aa")
    raw_dark = render_html_to_png(dark_html, "dark")
    
    # Generate dark charcoal background 1:1 (#18181b)
    out_dark = os.path.join(IMAGES_DIR, "svm_logo_text_dark_1x1.png")
    create_1x1(raw_dark, out_dark, bg_color=(24, 24, 27, 255))
    
    # Generate dark transparent 1:1
    out_dark_transparent = os.path.join(IMAGES_DIR, "svm_logo_text_dark_transparent_1x1.png")
    create_1x1(raw_dark, out_dark_transparent, bg_color=None)

if __name__ == "__main__":
    main()
