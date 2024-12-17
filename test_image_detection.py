import pytest
from PIL import Image
from image_detection import draw_boxes, detect_objects
import json
import os
from unittest.mock import patch
import google.generativeai as genai


@pytest.fixture
def mock_image():
    return Image.new("RGB", (1000, 1000), color="red")


@pytest.fixture
def mock_detections():
    return [
        {
            "box_2d": {"xmin": 100, "ymin": 100, "xmax": 200, "ymax": 200},
            "label": "chair",
        },
        {
            "box_2d": {"xmin": 300, "ymin": 300, "xmax": 400, "ymax": 400},
            "label": "table",
        },
    ]


def test_draw_boxes(mock_image, mock_detections):
    scale_x = 1
    scale_y = 1
    draw_boxes(mock_image, mock_detections, scale_x, scale_y)
    # Add assertions to check if the boxes are drawn correctly
    # For example, you could check if the image has been modified


def test_detect_objects(mock_image, mock_detections, mocker):
    api_key = "test_api_key"
    image_path = "test_image.jpg"

    # Mock the Gemini API response
    mock_response = mocker.MagicMock()
    mock_response.text = json.dumps(mock_detections)

    mock_model = mocker.MagicMock()
    mock_model.generate_content.return_value = mock_response

    mocker.patch("google.generativeai.GenerativeModel", return_value=mock_model)
    mocker.patch("PIL.Image.open", return_value=mock_image)

    with patch.dict(
        os.environ,
        {
            "GEMINI_API_KEY": api_key,
            "GEMINI_MODEL_NAME": "gemini-1.5-pro-latest",
            "GEMINI_PROMPT": "test prompt",
        },
    ):
        detect_objects(image_path, api_key)
    # Add assertions to check if the function runs without errors
