# Image Detection Project

This project uses the Gemini API to detect objects in an image and draw bounding boxes around them.

## Installation

1.  Clone the repository.
2.  Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```
    
    (Note: if you don't have a requirements.txt file, you can create one by running `pip freeze > requirements.txt`)

3.  Create a `.env` file in the project root directory and add your Gemini API key, model name, and prompt:

    ```env
    GEMINI_API_KEY="YOUR_API_KEY"
    GEMINI_MODEL_NAME="gemini-1.5-pro-latest"
    ```

## Running the project

To run the image detection script, use the following command:

```bash
python image_detection.py <image_path>
```

Replace `<image_path>` with the path to the image you want to process.

## Testing

To run the tests, use the following command:

```bash
pytest
```

