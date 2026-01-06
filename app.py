import streamlit as st
import requests
import base64
import io
from PIL import Image

# 1. ページの設定
st.set_page_config(page_title="AI画像加工アプリ")
st.title("🎨 AI画像生成・加工スタジオ")

# 2. 左側のメニューにAPIキー入力欄を作る
with st.sidebar:
    st.header("設定")
    api_key = st.text_input("Stability AI APIキーを入力", type="password")
    st.markdown("[キーの取得はこちら](https://dreamstudio.ai/account/keys)")

# 3. AIを呼び出す関数
def call_stability_api(prompt, init_image=None):
    if not api_key:
        st.error("APIキーを入力してください")
        return None

    # 画像がある場合は加工モード、ない場合は生成モード
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
        # 画像をAPI用に変換
        img = init_image.convert("RGB").resize((1024, 1024))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        files["init_image"] = buf.getvalue()
        data["image_strength"] = 0.35 # 元画像の残し具合

    with st.spinner("AIが作成中..."):
        res = requests.post(url, headers=headers, files=files, data=data)
        
    if res.status_code == 200:
        img_b64 = res.json()["artifacts"][0]["base64"]
        return Image.open(io.BytesIO(base64.b64decode(img_b64)))
    else:
        st.error(f"エラー: {res.text}")
        return None

# 4. 画面のメイン操作
tab1, tab2 = st.tabs(["🖼 画像生成", "👗 写真加工・着せ替え"])

with tab1:
    prompt = st.text_input("どんな画像を作る？(英語)", placeholder="A fantasy castle")
    if st.button("生成する"):
        result = call_stability_api(prompt)
        if result: st.image(result)

with tab2:
    img_file = st.file_uploader("写真をアップロード", type=["jpg", "png", "jpeg"])
    style_instr = st.text_input("どう変えたい？(英語)", placeholder="wearing a red dress")
    if img_file and st.button("加工する"):
        result = call_stability_api(style_instr, init_image=Image.open(img_file))
        if result: st.image(result)
