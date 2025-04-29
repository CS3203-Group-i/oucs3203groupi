// File: frontend/js/flowchartUpload.js

document.addEventListener("DOMContentLoaded", function () {
    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("fileElem");

    // Click to trigger file picker
    dropZone.addEventListener("click", () => fileInput.click());

    // Highlight drop zone on drag
    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("dragover");
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("dragover");
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("dragover");
        if (e.dataTransfer.files.length) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });

    // File picker fallback
    fileInput.addEventListener("change", () => {
        if (fileInput.files.length) {
            handleFileUpload(fileInput.files[0]);
        }
    });

    function handleFileUpload(file) {
        if (file.type !== "application/pdf") {
            alert("Please upload a PDF file.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        fetch("http://127.0.0.1:5000/upload_pdf", {
            method: "POST",
            body: formData,
        })
            .then((response) => {
                if (!response.ok) {
                    return response.text();  // Get response as text if not JSON
                }
                return response.json();  // Return JSON if successful
            })
            .then((data) => {
                if (typeof data === 'string') {
                    console.error("Error response:", data);  // If text, log it
                    alert("Upload failed (1). " + data);
                } else {
                    alert("Upload successful: " + data.filename);
                }
            })
            .catch((err) => {
                console.error(err);
                alert("Upload failed (2).");
            });
        
    }
});
