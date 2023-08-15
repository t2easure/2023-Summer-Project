import streamlit as st
import pandas as pd
from io import BytesIO
from api.AI import AIAPI
from urllib import request
import io
from api.base import HaiAPI
from PIL import Image, ImageDraw, ImageFont
from api.secret import OPENAI_API_KEY, NCLOUD_OCR_API_KEY
from PIL import Image, ImageDraw, ImageFont
import time, uuid, requests, json
import openai

openai.api_key = OPENAI_API_KEY
ocr_secret = NCLOUD_OCR_API_KEY

st.title("책 읽어주는 인공지능")

def get_text_ocr_result(file):
    ocr_url = "https://cxl3q4nzrt.apigw.ntruss.com/custom/v1/23717/d7931b0cf28602762bbfd6fcfd3e42b141bd7a4c5c0bad5dbec4ca350644ac01/general"

    request_json = {
        'images': [
            {
                'format': 'png',
                'name': 'demo'
            }
        ],
        'requestId': str(uuid.uuid4()),
        'version': 'V2',
        'timestamp': int(round(time.time() * 1000))
    }

    payload = {'message': json.dumps(request_json).encode('UTF-8')}
    files = [('file', file)]
    headers = {'X-OCR-SECRET': ocr_secret}

    response = requests.request("POST", ocr_url, headers=headers, data=payload, files=files)
    rescode = response.status_code
    if rescode == 200:
        ocr_result = json.loads(response.text)
        extracted_text = ""

        # Extract text from the OCR result (adjust this based on the actual response structure)
        for item in ocr_result.get('images', []):
            for field in item.get('fields', []):
                if 'inferText' in field:
                    extracted_text += field['inferText'] + '\n'

        return extracted_text
    else:
        print("Error : " + response.text)
        return None

def get_summarization_result(input_text):
    # add prompt to input
    prompt = f"""다음 OCR 결과에 적절한 제목을 붙이고 4줄 이내로 요약하세요.
    항상 한국어로 답변해 주세요.

    ### OCR 결과:

    {input_text}
    제목: 다음에 본문의 제목을, 한 줄 띄어쓰기 하고
    요약 :
    \n다음에 요약 결과를 입력하세요. 요약 결과의 각 줄은 1. 2. 3. 과 같이 숫자로 시작해야 합니다.
    
    """

    # create a chat completion
    chat_completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", temperature=0,
        messages=[{"role": "user", "content": prompt}], 
        )

    # return the chat completion
    return chat_completion.choices[0].message.content
    
# File upload widget
uploaded_file = st.file_uploader("책 이미지 입력", type=["jpg", "png", "jpeg"])

# Check if a file was uploaded
if uploaded_file is not None:
    # Read the uploaded file as bytes
    img_bytes = uploaded_file.read()

    # Convert bytes to PIL Image
    img = Image.open(io.BytesIO(img_bytes))

    # Display the image using Streamlit
    st.image(img, caption="Uploaded Image", use_column_width=True)

    st.header("OCR 결과")

    extracted_text = get_text_ocr_result(img_bytes)
    if extracted_text:
        st.write(extracted_text)
    else:
        st.write("OCR failed or no text extracted.")

    st.header("요약 결과")
    st.write(get_summarization_result(extracted_text))