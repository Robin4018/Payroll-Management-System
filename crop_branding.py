from PIL import Image
import os

# Path from prompt
img_path = r"C:/Users/Lenovo/.gemini/antigravity/brain/193cdb44-48b9-46ef-a27f-f164b8a5bb31/uploaded_media_1771497283084.jpg"
output_dir = r"d:\Project\Payroll Management System\universal-payroll-system\media\assets\branding"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

try:
    img = Image.open(img_path)
    width, height = img.size

    # Crop Header (Top ~22%)
    header = img.crop((0, 0, width, int(height * 0.22)))
    header.save(os.path.join(output_dir, "payslip_header.png"))

    # Crop Signature Area (Around the Principal's sign and seal)
    # Positioning based on visual observation: 
    # Left: 10%, Top: 45%, Right: 50%, Bottom: 75%
    signature = img.crop((int(width * 0.05), int(height * 0.45), int(width * 0.55), int(height * 0.78)))
    signature.save(os.path.join(output_dir, "payslip_signature.png"))

    # Crop Footer (Bottom ~10%)
    footer = img.crop((0, int(height * 0.90), width, height))
    footer.save(os.path.join(output_dir, "payslip_footer.png"))

    print("Crops created successfully.")
except Exception as e:
    print(f"Error: {e}")
