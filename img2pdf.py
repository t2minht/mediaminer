from PIL import Image
import os

def img2pdf(path, page_count, pdf_name, format):
    # path = input("Enter the file path: ")
    try:
        path = str(path)
        images = []

        # for file_name in os.listdir(path):
        for i in range(1, page_count):
            # print(i)
            file_name = str(i) + format
            # print(file_name)
            if(file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))==False):
                continue
            # print(path + "\\" + file_name)
            img = Image.open(os.path.join(path + "\\", file_name))
            images.append(img)

        # file_name = path.split('\\')[-1]
        
        new_path = '\\'.join(path.split('\\')[:-2]) + "\\" + pdf_name + ".pdf"
        print(new_path)
        images[0].save(new_path.strip(), "PDF", resolution=100.0, save_all=True, append_images=images[1:])
    except ValueError:
        print("Invalid Path")
