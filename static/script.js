async function generateQRCode() {
    const formData = new FormData(document.getElementById("qrForm"));
    const previewDiv = document.getElementById("qrCodeImage");
    previewDiv.innerHTML = `<p>Gerando QR Code...</p>`;

    try {
        const response = await fetch("/generate", {
            method: "POST",
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            previewDiv.innerHTML = `<img src="${data.qr_image_url}" alt="QR Code">`;
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
