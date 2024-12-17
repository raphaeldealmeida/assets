import google.generativeai as genai
import sys
import os
from PIL import Image, ImageDraw
import json
from dotenv import load_dotenv
from typing import List, Dict, Any, Tuple, Optional
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

IMAGE_SCALE = 1000


def draw_boxes(
    image: Image.Image, detections: List[Dict[str, Any]], scale_x: float, scale_y: float
) -> None:
    draw = ImageDraw.Draw(image)
    for detection in detections:
        box = detection.get("box_2d")
        label = detection.get("label")
        if box and label:
            xmin = box.get("xmin")
            ymin = box.get("ymin")
            xmax = box.get("xmax")
            ymax = box.get("ymax")
            if (
                xmin is not None
                and ymin is not None
                and xmax is not None
                and ymax is not None
            ):
                x1 = int(float(xmin) * scale_x)
                y1 = int(float(ymin) * scale_y)
                x2 = int(float(xmax) * scale_x)
                y2 = int(float(ymax) * scale_y)
                logging.info(f"draw box: ({x1}, {y1}), ({x2}, {y2})")
                draw.rectangle([(x1, y1), (x2, y2)], outline="red", width=5)
                draw.text((x1, y1 - 10), label, fill="red")


def _get_gemini_response(
    model: genai.GenerativeModel, prompt: str, image: Image.Image
) -> Optional[str]:
    try:
        response = model.generate_content([prompt, image], stream=False)
        if response and response.text:
            return response.text
        else:
            logging.error("Error: Gemini API returned an empty response.")
            return None
    except Exception as e:
        logging.error(f"Error during API call: {e}")
        return None


def detect_objects(image_path: str, api_key: str) -> None:
    genai.configure(api_key=api_key)
    generation_config = {
        "temperature": 1,
        "response_mime_type": "application/json",
    }

    model_name = os.getenv("GEMINI_MODEL_NAME")
    if not model_name:
        logging.error(
            "Error: GEMINI_MODEL_NAME not found in environment variables or .env file."
        )
        sys.exit(1)

    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
    )

    try:
        image = Image.open(image_path)
    except FileNotFoundError:
        logging.error(f"Error: Image file not found at {image_path}")
        return
    except Exception as e:
        logging.error(f"Error opening image: {e}")
        return

    prompt = 'Detect up to 5 furnitures in the image. Provide the bounding box coordinates. The answer should follow the json format: [{"box_2d": {"xmax": <xmax>, "ymax": <ymax>,"xmin": <xmin>,"ymin": <ymin>}, "label": <label> }, ...]. Considere 0-1000 scale.'

    response_text = _get_gemini_response(model, prompt, image)
    if not response_text:
        return

    try:
        if isinstance(response_text, str):
            detections = json.loads(response_text)
        else:
            detections = response_text
        logging.info(detections)
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON response: {e}")
        return
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return

    image_width, image_height = image.size
    scale_x = image_width / IMAGE_SCALE
    scale_y = image_height / IMAGE_SCALE

    draw_boxes(image, detections, scale_x, scale_y)

    output_path = os.path.splitext(image_path)[0] + "_detected.jpg"
    image.save(output_path)
    logging.info(f"Image with bounding boxes saved to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        logging.error("Usage: python image_detection.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logging.error(
            "Error: GEMINI_API_KEY not found in environment variables or .env file."
        )
        sys.exit(1)
    detect_objects(image_path, api_key)
