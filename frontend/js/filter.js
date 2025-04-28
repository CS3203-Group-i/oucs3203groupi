document.addEventListener("DOMContentLoaded", function () {
    function checkAndRunFilter() {
        document.getElementById('loadingBarContainer').style.display = 'block';

        fetch('/check-upload-status')
            .then(response => response.json())
            .then(data => {
                if (data.pdf_uploaded) {
                    alert('PDF uploaded successfully. Filter is running!');
                    displayFilteredCourses(data.filtered_courses);
                } else {
                    alert('PDF not uploaded!');
                }

                if (data.user_input_uploaded) {
                    displayUserInput(data.user_input_lines);
                }

                document.getElementById('loadingBarContainer').style.display = 'none';
            })
            .catch(error => {
                console.error('Error:', error);
                alert('There was an error checking the upload status');
                document.getElementById('loadingBarContainer').style.display = 'none';
            });
    }

    function displayFilteredCourses(courses) {
        const coursesList = document.getElementById('coursesList');
        const coursesContainer = document.getElementById('coursesContainer');

        if (courses.length > 0) {
            coursesList.innerHTML = '';

            courses.forEach(course => {
                const li = document.createElement('li');
                li.textContent = course.trim();
                coursesList.appendChild(li);
            });

            coursesContainer.style.display = 'block';
        } else {
            alert('No filtered courses found.');
        }
    }

    function displayUserInput(lines) {
        const userInputContainer = document.getElementById('userInputContainer');
        if (userInputContainer) {
            userInputContainer.innerHTML = '';

            lines.forEach(line => {
                const p = document.createElement('p');
                p.textContent = line.trim();
                userInputContainer.appendChild(p);
            });

            userInputContainer.style.display = 'block';
        }
    }

    function runAIModel() {
        const generateButton = document.getElementById('generateScheduleButton');
        const loadingBarContainer = document.getElementById('loadingBarContainer');
    
        if (generateButton) {
            generateButton.disabled = true;
            generateButton.textContent = 'Generating...';
        }
    
        loadingBarContainer.style.display = 'block';
    
        // Check if the checkboxes are selected
        const usePdf = document.getElementById('usePDF').checked;
        const useManual = document.getElementById('useManualInput').checked;
    
        const requestBody = {
            use_pdf: usePdf,
            use_manual: useManual
        };
    
        fetch('/run-ai-model', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        })
        .then(response => response.json())
        .then(data => {
            console.log("AI Result Data:", data); // Log the response to see the structure
            if (data.ai_result) {
                displayAIResult(data.ai_result);
                console.log('Hi')
            } else {
                alert('Failed to run AI model.');
            }
        })
        .catch(error => {
            console.error('Error running AI model:', error);
            alert('Error running AI model.');
        })
        .finally(() => {
            if (generateButton) {
                generateButton.disabled = false;
                generateButton.textContent = 'Generate Schedule with AI';
            }
            loadingBarContainer.style.display = 'none';
        });
    }
    
    

    function displayAIResult(aiResult) {
        const aiResultContainer = document.getElementById('aiResultContainer');
        const scheduleContainer = document.getElementById('scheduleContainer');

        scheduleContainer.innerHTML = '';

        const courses = aiResult
            .replace(/[\[\]]/g, '')
            .split(/\n|,/)
            .map(course => course.trim())
            .filter(course => course.length > 0);

        const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
        const schedule = {
            Monday: [],
            Tuesday: [],
            Wednesday: [],
            Thursday: [],
            Friday: []
        };

        const dayMap = {
            M: 'Monday',
            T: 'Tuesday',
            W: 'Wednesday',
            R: 'Thursday',
            F: 'Friday'
        };

        courses.forEach(course => {
            const match = course.match(/Days\s+([A-Z\/]+)/i);
            if (match) {
                const rawDays = match[1];
                const tokens = new Set();

                if (rawDays.includes('/')) {
                    rawDays.split('/').forEach(part => {
                        if (part === 'TR') {
                            tokens.add('T');
                            tokens.add('R');
                        } else {
                            part.split('').forEach(ch => tokens.add(ch));
                        }
                    });
                } else if (rawDays === 'TR') {
                    tokens.add('T');
                    tokens.add('R');
                } else {
                    rawDays.split('').forEach(ch => {
                        tokens.add(ch);
                    });
                }

                tokens.forEach(token => {
                    const dayName = dayMap[token];
                    if (dayName) {
                        schedule[dayName].push(course);
                    }
                });
            }
        });

        daysOfWeek.forEach(day => {
            const dayContainer = document.createElement('div');
            dayContainer.classList.add('day-container');

            const dayTitle = document.createElement('h4');
            dayTitle.textContent = day;

            const courseList = document.createElement('ul');
            schedule[day].forEach(course => {
                const listItem = document.createElement('li');
                listItem.textContent = course;
                courseList.appendChild(listItem);
            });

            dayContainer.appendChild(dayTitle);
            dayContainer.appendChild(courseList);
            scheduleContainer.appendChild(dayContainer);
        });

        aiResultContainer.style.display = 'block';
    }

    // Auto-check when page loads
    checkAndRunFilter();

    // Hook up the AI model generation button
    const generateButton = document.getElementById('generateScheduleButton');
    if (generateButton) {
        generateButton.addEventListener('click', runAIModel);
    }
});
