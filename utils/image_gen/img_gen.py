from gradio_client import Client
from PIL import Image
import os
from utils.gemini.gemini_ai import get_convert_image_prompt
from utils.classes.database import get_database_path
#os.environ["HF_Token"]='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'
client =Client("black-forest-labs/FLUX.1-schnell")
def convert_webp_to_jpg(input_file, output_file, quality=85):
    try:
        # Check if input file exists
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file '{input_file}' does not exist.")

        # Open the WebP image
        with Image.open(input_file) as img:
            # Convert to RGB mode if necessary
            if img.mode == 'CMYK':
                img = img.convert('RGB')

            # Save as JPG with quality control
            img.save(output_file.replace("\\","\\\\"), 'JPEG', quality=quality)

        print(f"Conversion successful! Image saved to: {output_file}")

    except (FileNotFoundError, IOError) as e:
        print(f"Error converting image: {e}")
        

def image_generator(context):
    prompt = get_convert_image_prompt(context)
    # just have me prompt to generat the image 
    res = client.predict(prompt=prompt,seed=0,randomize_seed=True,
    height=1000,
    width=1000,
    num_inference_steps=4,
    api_name="/infer")
    ress = str(res[0])
    ress = ress[:-4]+"jpg"
    # output_image = photo_path
    # print("output : ",output_image)
    print("res 0 : ",ress)
    print("______________________________")
    convert_webp_to_jpg(res[0], ress)

    return ress.replace("\\","\\\\")

