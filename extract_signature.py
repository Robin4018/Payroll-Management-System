from PIL import Image
import os

# New PNG source
img_path = r"C:/Users/Lenovo/.gemini/antigravity/brain/193cdb44-48b9-46ef-a27f-f164b8a5bb31/uploaded_media_1771497757866.png"
output_dir = r"d:\Project\Payroll Management System\universal-payroll-system\media\assets\branding"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

try:
    img = Image.open(img_path)
    # Ensure it has transparency or handle white background if needed
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    width, height = img.size

    # Crop Signature Area (Around the Principal's sign and seal)
    # Positioning based on visual observation of the new PNG:
    # It seems to be slightly higher/lower than before.
    # Let's take a generous crop and hope it fits well.
    # Left: 0.05, Top: 0.40, Right: 0.55, Bottom: 0.78
    signature = img.crop((int(width * 0.05), int(height * 0.45), int(width * 0.55), int(height * 0.75)))
    
    # Optional: Make white background transparent
    datas = signature.getdata()
    newData = []
    for item in datas:
        # If it's very close to white, make it transparent
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    signature.putdata(newData)
    
    signature.save(os.path.join(output_dir, "payslip_signature.png"), "PNG")

    print("Signature extracted from PNG successfully with transparency.")
except Exception as e:
    print(f"Error: {e}")
