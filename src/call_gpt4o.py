import os
import time
import base64
from PIL import Image
from io import BytesIO
from openai import OpenAI

def encode_image(image: Image.Image) -> str:
    """
    Resize the image to 512x512 and encode it to base64.

    Args:
        image (Image.Image): The input image.

    Returns:
        str: The base64 encoded string of the resized image.
    """
    resized_image = image.resize((512, 512), Image.Resampling.LANCZOS)
    buffered = BytesIO()
    resized_image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def request(
    prompt: str,
    video_inputs: list,
    timeout: int = 60
) -> str:
    """
    Send a request to the OpenAI API with a prompt and a list of video inputs.

    Args:
        prompt (str): The user's prompt.
        video_inputs (list): A list of video inputs, which can be either images or text.
        timeout (int, optional): The timeout for the API request. Defaults to 60.

    Returns:
        str: The response text from the API.
    """
    messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "You are a professional multimodal assistant. "
                        "**You will be given a list of image frames from a video, "
                        "and you need to pretend that you are watching the video.** "
                        "You **MUST** carefully follow the user's requests."
                    ),
                }
            ]
        },
        {
            "role": "user",
            "content": []
        }
    ]

    for video_input in video_inputs:
        if isinstance(video_input, str):
            messages[1]["content"].append(
                {
                    "type": "text",
                    "text": video_input,
                }
            )
        else:
            messages[1]["content"].append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encode_image(video_input)}"
                    }
                }
            )

    messages[1]["content"].append(
        {
            "type": "text",
            "text": prompt,
        }
    )

    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    response_text = ""

    try_count = 0
    while try_count < 10:
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                temperature=0.,
                messages=messages,
                max_tokens=4096,
                timeout=timeout,
            )
            response_text = response.choices[0].message.content
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)
            try_count += 1

    return response_text