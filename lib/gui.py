import tkinter as tk
from PIL import Image, ImageTk
# import functions_cli.py  # uncomment later

def quit_app():
    root.destroy()

root = tk.Tk()
root.title("CSIRT Laudry")

# Load and display 'csirt.png' with a width of 512 pixels
image_path = "img/csirt.png"  # Adjust the path to your actual image location
img = Image.open(image_path)

# Calculate the new height to maintain the aspect ratio
aspect_ratio = img.height / img.width
new_width = 512
new_height = int(new_width * aspect_ratio)

img = img.resize((new_width, new_height), Image.ANTIALIAS)
img_tk = ImageTk.PhotoImage(img)

label_image = tk.Label(root, image=img_tk)
label_image.pack()

# Create a Quit button
quit_button = tk.Button(root, text="Quit", command=quit_app)
quit_button.pack(side=tk.BOTTOM)

root.mainloop()
