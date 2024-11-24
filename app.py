from flask import Flask, render_template, request, jsonify, url_for
import qrcode
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styledpil import StyledPilImage
from PIL import Image, ImageDraw, ImageFont
import os
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
OUTPUT_FOLDER = "static/generated"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Função para limpar arquivos antigos
def cleanup_old_files(folder, max_age_hours=24):
    now = datetime.now()
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            file_age = now - datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_age > timedelta(hours=max_age_hours):
                os.remove(file_path)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_qr():
    cleanup_old_files(UPLOAD_FOLDER)  # Limpar arquivos antigos de uploads
    cleanup_old_files(OUTPUT_FOLDER)  # Limpar arquivos antigos gerados

    # Obtendo os dados do formulário
    text = request.form.get("text", "").strip()
    if not text:
        return jsonify({"error": "O texto do QR Code é obrigatório"}), 400

    front_color = request.form.get("front_color", "#000000")  # Preto padrão
    back_color = request.form.get("back_color", "#FFFFFF")  # Branco padrão
    border_color = request.form.get("border_color", "#FFFFFF")  # Cor da moldura
    label_text = request.form.get("label_text", "").strip()
    label_color = request.form.get("label_color", "#000000")  # Cor do texto

    # Verifica se há upload de logotipo
    logo = request.files.get("logo")
    logo_path = None

    if logo and logo.filename.endswith(('.png', '.jpg', '.jpeg')):
        logo_path = os.path.join(UPLOAD_FOLDER, f"logo_{uuid.uuid4().hex}.png")
        logo.save(logo_path)
    elif logo and logo.filename != "":
        return jsonify({"error": "Formato de logo inválido. Apenas PNG, JPG ou JPEG são aceitos"}), 400

    # Convertendo cores para formato RGB
    try:
        front_color = tuple(int(front_color[i:i+2], 16) for i in (1, 3, 5))
        back_color = tuple(int(back_color[i:i+2], 16) for i in (1, 3, 5))
        border_color = tuple(int(border_color[i:i+2], 16) for i in (1, 3, 5))
        label_color = tuple(int(label_color[i:i+2], 16) for i in (1, 3, 5))
    except ValueError:
        return jsonify({"error": "Cores inválidas. Use o formato hexadecimal (ex: #FFFFFF)"}), 400

    # Configurando o QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    # Gerando a imagem com cores personalizadas
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        color_mask=SolidFillColorMask(
            front_color=front_color,
            back_color=back_color
        ),
    ).convert("RGBA")

    # Adicionando logotipo, se houver
    if logo_path:
        logo_img = Image.open(logo_path).convert("RGBA")
        logo_size = (img.size[0] // 5, img.size[1] // 5)
        logo_img = logo_img.resize(logo_size, Image.LANCZOS)

        # Inserir o logo no centro do QR Code
        pos = ((img.size[0] - logo_img.size[0]) // 2, (img.size[1] - logo_img.size[1]) // 2)
        img.paste(logo_img, pos, mask=logo_img)

    # Criando um fundo ao redor do QR Code
    background_size = (img.size[0] + 40, img.size[1] + 100)
    background = Image.new("RGBA", background_size, border_color)

    # Colocando o QR Code no centro do fundo
    qr_position = ((background_size[0] - img.size[0]) // 2, 20)
    background.paste(img, qr_position, img)

    # Adicionando texto abaixo do QR Code
    if label_text:
        draw = ImageDraw.Draw(background)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), label_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_position = ((background_size[0] - text_width) // 2, img.size[1] + 40)
        draw.text(text_position, label_text, fill=label_color, font=font)

    # Salvando a imagem gerada
    output_filename = f"qrcode_{uuid.uuid4().hex}.png"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    background.save(output_path)
    qr_image_url = url_for('static', filename=f"generated/{output_filename}")

    return jsonify({'qr_image_url': qr_image_url})

if __name__ == "__main__":
    app.run(debug=True)