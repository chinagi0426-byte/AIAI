import streamlit as st
import requests
import base64
import io
from PIL import Image

st.set_page_config(page_title="AI画像加工アプリ")

st.title("🎨 AI画像加工・生成スタジオ")

# APIキー入力欄
api_key = st.sidebar.text_input("Stability AI API Key", type="password")

def call_stability_api(prompt, init_image=None, mask_image=None, mode="text-to-image"):
    if not api_key:
        st.error("APIキーを入力してください")
        return None

    host = "https://api.stability.ai"
    engine_id = "stable-diffusion-xl-1024-v1-0"
    url = f"{host}/v1/generation/{engine_id}/{mode}"
    
    headers = {"Accept": "application/json", "Authorization": f"Bearer {api_key}"}
    data = {"text_prompts": [{"text": prompt}], "cfg_scale": 7, "steps": 30}
    files = {}

    if mode == "image-to-image" and init_image:
        img_byte_arr = io.BytesIO()
        init_image.save(img_byte_arr, format='PNG')
        files["init_image"] = img_byte_arr.getvalue()
        data["image_strength"] = 0.35
    
    # API送信
    response = requests.post(url, headers=headers, files=files, data=data)
    if response.status_code == 200:
        image_data = response.json()["artifacts"][0]["base64"]
        return Image.open(io.BytesIO(base64.b64decode(image_data)))
    else:
        st.error(f"エラー: {response.text}")
        return None

# メインメニュー
tab1, tab2 = st.tabs(["画像生成", "スタイル変換"])

with tab1:
    prompt = st.text_input("どんな画像を作りたい？")
    if st.button("生成"):
        result = call_stability_api(prompt, mode="text-to-image")
        if result:
            st.image(result)

with tab2:
    uploaded_file = st.file_view("画像をアップロード")
    style_prompt = st.text_input("スタイルの指示（例: Anime style）")
    if uploaded_file and st.button("変換"):
        img = Image.open(uploaded_file)
        result = call_stability_api(style_prompt, init_image=img, mode="image-to-image")
        if result:
            st.image(result)
