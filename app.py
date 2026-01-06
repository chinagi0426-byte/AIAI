import streamlit as st
import requests
import base64
import io
from PIL import Image

# 1. ページの設定
st.set_page_config(page_title="AI画像加工くん", layout="centered")

st.title("🎨 AI画像生成・加工スタジオ")
st.write("GitHub + Streamlit Cloud で動いています")

# 2. APIキー入力（画面の横に出るメニュー）
with st.sidebar:
    st.header("設定")
    api_key = st.text_input("Stability AI APIキー", type="password")
    st.markdown("[キーの取得はこちら](https://dreamstudio.ai/account/keys)")

# 3. AIを呼び出す関数
def call_ai(prompt, init_image=None):
    if not api_key:
        st.warning("左のメニューにAPIキーを入力してね！")
        return None
    
    # 画像生成か加工かでURLを変える
    mode = "image-to-image" if init_image else "text-to-image"
    url = f"https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/{mode}"
    
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 7,
        "steps": 30,
    }
    
    files = {}
    if init_image:
        # 画像をリサイズしてAPIに送る準備
        img = init_image.convert("RGB").resize((1024, 1024))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        files["init_image"] = buf.getvalue()
        data["image_strength"] = 0.35

    with st.spinner("AIが作っています..."):
        res = requests.post(url, headers=headers, files=files, data=data)
        
    if res.status_code == 200:
        img_b64 = res.json()["artifacts"][0]["base64"]
        return Image.open(io.BytesIO(base64.b64decode(img_b64)))
    else:
        st.error(f"エラー: {res.text}")
        return None

# 4. メイン画面のメニュー
menu = st.tabs(["🖼 ゼロから生成", "👗 写真を加工（着せ替え）"])

with menu[0]:
    prompt = st.text_input("どんな画像を作る？ (英語で)", placeholder="A cute shiba inu in space")
    if st.button("画像を生成する"):
        result = call_ai(prompt)
        if result:
            st.image(result)

with menu[1]:
    st.write("写真をアップして、指示（服を変えるなど）を入力してください")
    img_file = st.file_uploader("写真をアップロード", type=["jpg", "png", "jpeg"])
    style_instr = st.text_input("どう変える？", placeholder="wearing a red tuxedo")
    if img_file and st.button("写真を加工する"):
        result = call_ai(style_instr, init_image=Image.open(img_file))
        if result:
            st.image(result)
