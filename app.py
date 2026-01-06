import streamlit as st
import requests
import base64
import io
from PIL import Image

# ページの基本設定
st.set_page_config(page_title="AI画像編集ツール", layout="wide")

st.title("🎨 AI画像生成・加工スタジオ")

# --- 🔑 APIキー入力欄 ---
st.sidebar.header("設定")
api_key = st.sidebar.text_input("Stability AI APIキーを入力", type="password")
st.sidebar.markdown("[キーの取得はこちら](https://dreamstudio.ai/account/keys)")

# --- 🚀 API呼び出し関数 ---
def call_stability_api(prompt, init_image=None, mode="text-to-image"):
    if not api_key:
        st.error("左側のメニューにAPIキーを入力してください！")
        return None

    host = "https://api.stability.ai"
    engine_id = "stable-diffusion-xl-1024-v1-0"
    url = f"{host}/v1/generation/{engine_id}/{mode}"
    
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
        # 画像をAPIが読み込める形式に変換
        img_byte_arr = io.BytesIO()
        init_image.save(img_byte_arr, format='PNG')
        files["init_image"] = img_byte_arr.getvalue()
        data["image_strength"] = 0.35 # スタイル変換の強さ

    with st.spinner("AIが考え中..."):
        response = requests.post(url, headers=headers, files=files, data=data)

    if response.status_code == 200:
        image_data = response.json()["artifacts"][0]["base64"]
        return Image.open(io.BytesIO(base64.b64decode(image_data)))
    else:
        st.error(f"エラーが発生しました: {response.text}")
        return None

# --- 🎨 画面のメニュー ---
tab1, tab2, tab3 = st.tabs(["🖼 画像生成", "👗 服・スタイル変換", "✨ 使いかた"])

# 1. 画像生成タブ
with tab1:
    st.subheader("言葉から画像を作る")
    gen_prompt = st.text_input("どんな画像を作りたい？（英語）", placeholder="A cute cat in a space suit")
    if st.button("画像を生成"):
        result = call_stability_api(gen_prompt, mode="text-to-image")
        if result:
            st.image(result, caption="生成された画像")

# 2. スタイル変換・着せ替えタブ
with tab2:
    st.subheader("写真の服や雰囲気を変える")
    st.info("※服を変えたい場合は、下の欄に「Blue dress」などと入力してください。")
    uploaded_file = st.file_uploader("加工したい写真をアップロード", type=["jpg", "png", "jpeg"])
    style_prompt = st.text_input("どんな風に変えたい？", placeholder="Wearing a red leather jacket")
    
    if uploaded_file and st.button("写真を加工"):
        img = Image.open(uploaded_file)
        result = call_stability_api(style_prompt, init_image=img, mode="image-to-image")
        if result:
            st.image(result, caption="加工後の画像")

# 3. 使いかた
with tab3:
    st.markdown("""
    ### 使いかたガイド
    1. **APIキーを準備**: [Stability AI](https://dreamstudio.ai/account/keys) でキーを取得します。
    2. **キーを入力**: 左側の黒いメニューにある入力欄に貼り付けます。
    3. **実行**: 
        - **画像生成**: 英語で説明を入力してボタンを押すだけ！
        - **服・加工**: 写真をアップし、変えたい内容（例：`Wearing a suit`）を入力してボタンを押します。
    """)
