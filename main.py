import os
import tempfile
import tkinter as tk
from tkinter import filedialog, simpledialog, ttk, colorchooser
from PIL import Image, ImageTk, ImageEnhance, ImageFilter, ImageOps
import requests

class PhotoEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("PyShop")
        self.root.iconphoto(False, tk.PhotoImage(file='ps.png'))

        self.image = None
        self.original_image = None
        self.photo = None

        self.canvas = tk.Canvas(root, bg='grey')
        self.canvas.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.frame = ttk.Frame(root)
        self.frame.pack(padx=10, pady=10)

        self.load_button = ttk.Button(self.frame, text="Load Image", command=self.load_image)
        self.load_button.grid(row=0, column=0, padx=5, pady=5)

        self.save_button = ttk.Button(self.frame, text="Save Image", command=self.save_image)
        self.save_button.grid(row=0, column=1, padx=5, pady=5)

        self.crop_button = ttk.Button(self.frame, text="Crop Image", command=self.start_crop)
        self.crop_button.grid(row=0, column=2, padx=5, pady=5)

        self.rotate_button = ttk.Button(self.frame, text="Rotate Image", command=self.rotate_image)
        self.rotate_button.grid(row=0, column=3, padx=5, pady=5)

        self.resize_button = ttk.Button(self.frame, text="Resize Image", command=self.start_resize)
        self.resize_button.grid(row=0, column=4, padx=5, pady=5)

        self.brightness_label = ttk.Label(self.frame, text="Brightness")
        self.brightness_label.grid(row=1, column=0, padx=5, pady=5)
        self.brightness_scale = ttk.Scale(self.frame, from_=0.1, to=2.0, orient='horizontal', command=self.apply_filters)
        self.brightness_scale.set(1.0)
        self.brightness_scale.grid(row=1, column=1, padx=5, pady=5)

        self.contrast_label = ttk.Label(self.frame, text="Contrast")
        self.contrast_label.grid(row=2, column=0, padx=5, pady=5)
        self.contrast_scale = ttk.Scale(self.frame, from_=0.1, to=2.0, orient='horizontal', command=self.apply_filters)
        self.contrast_scale.set(1.0)
        self.contrast_scale.grid(row=2, column=1, padx=5, pady=5)

        self.saturation_label = ttk.Label(self.frame, text="Saturation")
        self.saturation_label.grid(row=3, column=0, padx=5, pady=5)
        self.saturation_scale = ttk.Scale(self.frame, from_=0.1, to=2.0, orient='horizontal', command=self.apply_filters)
        self.saturation_scale.set(1.0)
        self.saturation_scale.grid(row=3, column=1, padx=5, pady=5)

        self.blur_label = ttk.Label(self.frame, text="Blur")
        self.blur_label.grid(row=4, column=0, padx=5, pady=5)
        self.blur_scale = ttk.Scale(self.frame, from_=0.0, to=10.0, orient='horizontal', command=self.apply_filters)
        self.blur_scale.set(0.0)
        self.blur_scale.grid(row=4, column=1, padx=5, pady=5)

        self.edit_paint_button = ttk.Button(self.frame, text="Edit in Paint", command=self.edit_in_paint)
        self.edit_paint_button.grid(row=0, column=5, padx=5, pady=5)

        self.color_palette_button = ttk.Button(self.frame, text="Apply Color Palette", command=self.apply_color_palette)
        self.color_palette_button.grid(row=0, column=6, padx=5, pady=5)

        self.generate_image_button = ttk.Button(self.frame, text="Just find photos", command=self.generate_image)
        self.generate_image_button.grid(row=0, column=7, padx=5, pady=5)

        self.rect = None
        self.start_x = None
        self.start_y = None
        self.active_tool = None

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.original_image = Image.open(file_path)
            self.image = self.original_image.copy()

            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()

            img_width, img_height = self.image.size
            if img_width > screen_width or img_height > screen_height:
                scale_factor = min(screen_width / img_width, screen_height / img_height)
                new_size = (int(img_width * scale_factor), int(img_height * scale_factor))
                self.image = self.image.resize(new_size, Image.LANCZOS)
                self.original_image = self.image.copy()
            
            self.display_image(self.image)
            self.brightness_scale.set(1.0)
            self.contrast_scale.set(1.0)
            self.saturation_scale.set(1.0)
            self.blur_scale.set(0.0)

    def save_image(self):
        if self.image:
            file_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                     filetypes=[("JPEG files", "*.jpg"),
                                                                ("PNG files", "*.png"),
                                                                ("All files", "*.*")])
            if file_path:
                self.image.save(file_path)

    def apply_filters(self, _=None):
        if self.original_image:
            self.image = self.original_image.copy()

            brightness_enhancer = ImageEnhance.Brightness(self.image)
            self.image = brightness_enhancer.enhance(self.brightness_scale.get())

            contrast_enhancer = ImageEnhance.Contrast(self.image)
            self.image = contrast_enhancer.enhance(self.contrast_scale.get())

            saturation_enhancer = ImageEnhance.Color(self.image)
            self.image = saturation_enhancer.enhance(self.saturation_scale.get())

            blur_value = self.blur_scale.get()
            if blur_value > 0:
                self.image = self.image.filter(ImageFilter.GaussianBlur(blur_value))

            self.display_image(self.image)

    def start_crop(self):
        self.active_tool = "crop"
        self.canvas.config(cursor="cross")

    def start_resize(self):
        self.active_tool = "resize"
        self.canvas.config(cursor="cross")

    def on_button_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')

    def on_mouse_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        if self.active_tool == "crop":
            self.crop_image(event)
        elif self.active_tool == "resize":
            self.resize_image_interactive(event)
        self.active_tool = None

    def crop_image(self, _):
        if self.rect:
            x1, y1, x2, y2 = map(int, self.canvas.coords(self.rect))
            self.image = self.image.crop((x1, y1, x2, y2))
            self.original_image = self.image.copy()
            self.display_image(self.image)
            self.canvas.delete(self.rect)
            self.rect = None
            self.canvas.config(cursor="arrow")

    def resize_image_interactive(self, _):
        if self.rect:
            x1, y1, x2, y2 = map(int, self.canvas.coords(self.rect))
            new_width = abs(x2 - x1)
            new_height = abs(y2 - y1)
            self.image = self.image.resize((new_width, new_height), Image.LANCZOS)
            self.original_image = self.image.copy()
            self.display_image(self.image)
            self.canvas.delete(self.rect)
            self.rect = None
            self.canvas.config(cursor="arrow")

    def rotate_image(self):
        if self.image:
            angle = simpledialog.askfloat("Rotate", "Enter angle in degrees:", minvalue=0, maxvalue=360)
            if angle is not None:
                self.image = self.image.rotate(angle, expand=True)
                self.original_image = self.image.copy()
                self.display_image(self.image)

    def edit_in_paint(self):
        if self.image:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file_path = temp_file.name
                self.image.save(temp_file_path)

            os.system(f'mspaint "{temp_file_path}"')

            self.image = Image.open(temp_file_path)
            self.original_image = self.image.copy()
            self.display_image(self.image)

            os.remove(temp_file_path)

    def apply_color_palette(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.image = ImageOps.colorize(ImageOps.grayscale(self.image), black="black", white=color)
            self.original_image = self.image.copy()
            self.display_image(self.image)

    def generate_image(self):
        prompt = simpledialog.askstring("Generate Image", "Enter a prompt for the image:")
        if prompt:
            access_key = 'get your own'
            search_url = f"https://api.unsplash.com/search/photos?query={prompt.replace(' ', '%20')}&client_id={access_key}"
            
            response = requests.get(search_url)
            
            if response.status_code == 200:
                data = response.json()
                if data['results']:
                    img_url = data['results'][0]['urls']['regular']
                    #print("Image URL:", img_url)

                    img_response = requests.get(img_url)
                    if img_response.status_code == 200:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                            temp_file_path = temp_file.name
                            temp_file.write(img_response.content)
                            temp_file.close()

                            image = Image.open(temp_file_path)
                            self.image = image.copy()
                            self.display_image(image)

                            os.remove(temp_file_path)

                    else:
                        print(f"Failed to download image. Status code: {img_response.status_code}")
                else:
                    print("No images found.")
            else:
                print(f"Failed at all. Status code: {response.status_code}")

    def display_image(self, image):
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

if __name__ == "__main__":
    root = tk.Tk()
    editor = PhotoEditor(root)
    root.mainloop()
