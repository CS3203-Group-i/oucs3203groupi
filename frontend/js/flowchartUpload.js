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
        const isPDF = file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf");

        if (!isPDF) {
            alert("Invalid file type. Please upload a PDF document.");
            return;
        }

         //Added for security to make sure file is of the type pdf
        if (file.type !== "application/pdf") {
            alert("Please upload a PDF file.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        fetch("/upload_pdf", {
            method: "POST",
            body: formData,
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Upload failed.");
                }
                return response.json();
            })
            .then((data) => {
                alert("Upload successful: " + data.filename);
            })
            .catch((err) => {
                console.error(err);
                alert("Upload failed.");
            });
    }
});
