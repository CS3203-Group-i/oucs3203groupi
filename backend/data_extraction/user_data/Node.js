const express = require('express');
const fs = require('fs');
const app = express();
const path = require('path');

app.use(express.json());

app.post('/save', (req, res) => {
    const filePath = path.join(__dirname, 'saved_files', 'courseData.txt');

    fs.appendFile(filePath, req.body.content, (err) => {
        if (err) {
            console.error(err);
            res.status(500).send("Error saving file");
        } else {
            res.send("File saved successfully");
        }
    });
});

app.listen(5000, () => console.log('Server running on port 5000'));
