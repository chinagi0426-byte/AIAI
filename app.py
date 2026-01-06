import streamlit as st
import requests
import base64
import io
from PIL import Image

# 画面の設定
st.set_page_config(page_title="AI画像加工アプリ")
st.title("🎨 AI画像生成・加工スタジオ")

# APIキーの入力欄（画面左側）
api_key = st.sidebar.text_input("Stability AI API Key", type="password")

# AIを呼び出す関数
def call_api(prompt, init_image=None, mode="text-to-image"):
    if not api_key:
        st.error("APIキーを入力してください")
        return None
    
    url = f"https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/{mode}"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {api_key}"}
    data = {"text_prompts": [{"text": prompt}], "cfg_scale": 7, "steps": 30}
    files = {}

    if init_image:
        img_byte_arr = io.BytesIO()
        init_image.save(img_byte_arr, format='PNG')
        files["init_image"] = img_byte_arr.getvalue()
        data["image_strength"] = 0.35

    res = requests.post(url, headers=headers, files=files, data=data)
    if res.status_code == 200:
        img_data = res.json()["artifacts"][0]["base64"]
        return Image.open(io.BytesIO(base64.b64decode(img_data)))
    return None

# タブ分け
tab1, tab2 = st.tabs(["画像生成", "写真加工・着せ替え"])

with tab1:
    prompt = st.text_input("作りたい画像の説明（英語）")
    if st.button("生成"):
        result = call_api(prompt, mode="text-to-image")
        if result: st.image(result)

with tab2:
    uploaded = st.file_uploader("写真をアップロード")
    instr = st.text_input("どう変えたい？（例: wearing a red dress）")
    if uploaded and st.button("実行"):
        result = call_api(instr, init_image=Image.open(uploaded), mode="image-to-image")
        if result: st.image(result)
