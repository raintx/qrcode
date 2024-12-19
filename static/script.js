async function generateQRCode() {
    const formData = new FormData(document.getElementById("qrForm"));
    const previewDiv = document.getElementById("qrCodeImage");
    const downloadButton = document.getElementById("downloadButton");

    previewDiv.innerHTML = `<p>Gerando QR Code...</p>`;
    downloadButton.style.display = "none";

    try {
        const response = await fetch("/generate", {
            method: "POST",
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            const qrImageUrl = data.qr_image_url;
            previewDiv.innerHTML = `<img src="${qrImageUrl}" alt="QR Code">`;

            // Atualiza o botão de download
            downloadButton.style.display = "block";
            downloadButton.onclick = () => {
                const link = document.createElement("a");
                link.href = qrImageUrl;
                link.download = "QRCode.png";
                link.click();
            };
        } else {
            previewDiv.innerHTML = `<p>Erro ao gerar QR Code.</p>`;
        }
    } catch (error) {
        previewDiv.innerHTML = `<p>Erro de conexão. Tente novamente mais tarde.</p>`;
    }
}

let timer;
document.getElementById("qrForm").addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(() => {
        generateQRCode();
    }, 500);
});

document.getElementById("logo").addEventListener("change", (event) => {
    const file = event.target.files[0];
    if (file && !file.type.startsWith("image/png")) {
        alert("Por favor, envie apenas arquivos PNG.");
        event.target.value = "";
    } else {
        generateQRCode();
    }
});
