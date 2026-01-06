import gradio as gr
import requests
import base64
import io
from PIL import Image

# ==========================================
# 🚀 Stability AI API 呼び出し関数
# ==========================================

def call_stability_api(api_key, prompt, init_image=None, mask_image=None, mode="text-to-image"):
    if not api_key:
        return None, "APIキーを入力してください"

    # APIエンドポイントの設定
    host = "https://api.stability.ai"
    
    # モードに応じたエンジンの選択
    engine_id = "stable-diffusion-xl-1024-v1-0" # 最新の高品質モデル
    
    url = f"{host}/v1/generation/{engine_id}/{mode}"
    
    # リクエストヘッダー
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # パラメータ設定
    data = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 7,
        "steps": 30,
    }

    files = {}

    if mode == "image-to-image" and init_image:
        # 画像加工（全体）
        img_byte_arr = io.BytesIO()
        init_image.save(img_byte_arr, format='PNG')
        files["init_image"] = img_byte_arr.getvalue()
        data["image_strength"] = 0.35 # 元の画像をどれだけ残すか

    elif mode == "masking" and init_image and mask_image:
        # 服の着せ替え（一部変更）
        url = f"{host}/v1/generation/{engine_id}/image-to-image/masking"
        
        img_byte_arr = io.BytesIO()
        init_image.save(img_byte_arr, format='PNG')
        files["init_image"] = img_byte_arr.getvalue()
        
        mask_byte_arr = io.BytesIO()
        mask_image.save(mask_byte_arr, format='PNG')
        files["mask_image"] = mask_byte_arr.getvalue()
        
        data["mask_source"] = "MASK_IMAGE_WHITE"

    # APIリクエスト送信
    response = requests.post(url, headers=headers, files=files, data=data)

    if response.status_code != 200:
        return None, f"Error: {response.text}"

    # 結果の取り出し
    response_json = response.json()
    image_data = response_json["artifacts"][0]["base64"]
    output_image = Image.open(io.BytesIO(base64.b64decode(image_data)))
    
    return output_image, "成功！"

# ==========================================
# 🎨 Gradio 画面構成
# ==========================================

with gr.Blocks(title="AI Image Pro Tool") as demo:
    gr.Markdown("# 🛠 AI画像加工・生成スタジオ (API版)")
    
    # --- 🔑 API設定エリア ---
    with gr.Accordion("🔑 設定：APIキーを入力してください", open=True):
        api_key_input = gr.Textbox(
            label="Stability AI API Key", 
            placeholder="sk-...", 
            type="password"
        )
        gr.Markdown("[APIキーの取得はこちら](https://dreamstudio.ai/account/keys)")

    with gr.Tabs():
        # タブ1: 画像生成
        with gr.TabItem("① ゼロから生成"):
            with gr.Row():
                with gr.Column():
                    gen_prompt = gr.Textbox(label="何を描きたい？ (英語)", placeholder="A futuristic city in the style of Ghibli")
                    gen_btn = gr.Button("画像を生成する", variant="primary")
                gen_output = gr.Image(label="結果")
            
            gen_btn.click(
                fn=lambda key, prompt: call_stability_api(key, prompt, mode="text-to-image")[0],
                inputs=[api_key_input, gen_prompt],
                outputs=gen_output
            )

        # タブ2: 写真加工
        with gr.TabItem("② 写真の雰囲気を変える"):
            with gr.Row():
                with gr.Column():
                    style_img = gr.Image(type="pil", label="元の写真")
                    style_prompt = gr.Textbox(label="どんな風に変える？", placeholder="Anime style, professional photography")
                    style_btn = gr.Button("変換する", variant="primary")
                style_output = gr.Image(label="結果")
            
            style_btn.click(
                fn=lambda key, prompt, img: call_stability_api(key, prompt, init_image=img, mode="image-to-image")[0],
                inputs=[api_key_input, style_prompt, style_img],
                outputs=style_output
            )

        # タブ3: 着せ替え（インペイント）
        with gr.TabItem("③ 服を着せ替える"):
            gr.Markdown("※変えたい服の部分をブラシで白く塗ってください")
            with gr.Row():
                with gr.Column():
                    inpaint_input = gr.ImageMask(type="pil", label="服を塗る", layers=False)
                    inpaint_prompt = gr.Textbox(label="どんな服に着せ替える？", placeholder="Red business suit")
                    inpaint_btn = gr.Button("着せ替える", variant="primary")
                inpaint_output = gr.Image(label="結果")
            
            def inpaint_process(key, prompt, img_dict):
                init_img = img_dict["background"]
                mask_img = img_dict["layers"][0]
                return call_stability_api(key, prompt, init_image=init_img, mask_image=mask_img, mode="masking")[0]

            inpaint_btn.click(
                fn=inpaint_process,
                inputs=[api_key_input, inpaint_prompt, inpaint_input],
                outputs=inpaint_output
            )

# 起動
demo.launch()
