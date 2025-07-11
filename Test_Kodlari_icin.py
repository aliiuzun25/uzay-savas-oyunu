import os

current_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(current_dir, "assets", "uzay_gemisi.png")

print(image_path)
print(os.path.exists(image_path))  # True dönmeli