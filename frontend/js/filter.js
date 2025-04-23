document.addEventListener("DOMContentLoaded", function () {
    // Function to check if the PDF exists and run the filter
    function checkAndRunFilter() {
        // Show loading bar
        document.getElementById('loadingBarContainer').style.display = 'block';

        // Make the AJAX request to check if the PDF exists
        fetch('/check-upload-status')
            .then(response => response.json())
            .then(data => {
                if (data.uploaded) {
                    alert('PDF uploaded successfully. Filter is running!');
                    // Display the filtered courses (from filtered_courses.txt)
                    displayFilteredCourses(data.filtered_courses);
                    // Display AI result as a schedule for the weekdays (MWF, T/TR)
                    displayAIResult(data.ai_result);
                } else {
                    alert('PDF not uploaded!');
                }
                // Hide loading bar after the response
                document.getElementById('loadingBarContainer').style.display = 'none';
            })
            .catch(error => {
                console.error('Error:', error);
                alert('There was an error checking the upload status');
                // Hide loading bar in case of error
                document.getElementById('loadingBarContainer').style.display = 'none';
            });
    }

    // Function to display filtered courses on the page
    function displayFilteredCourses(courses) {
        const coursesList = document.getElementById('coursesList');
        const coursesContainer = document.getElementById('coursesContainer');

        if (courses.length > 0) {
            coursesList.innerHTML = '';  // Clear previous courses

            courses.forEach(course => {
                const li = document.createElement('li');
                li.textContent = course.trim();  // Remove extra spaces or newlines
                coursesList.appendChild(li);
            });

            // Show the course container
            coursesContainer.style.display = 'block';
        } else {
            alert('No filtered courses found.');
        }
    }

    function displayAIResult(aiResult) {
        const aiResultContainer = document.getElementById('aiResultContainer');
        const scheduleContainer = document.getElementById('scheduleContainer');
    
        // Clear previous content
        scheduleContainer.innerHTML = '';
        console.log('Raw AI Result:', aiResult);
    
        // Clean up and split courses
        const courses = aiResult
            .replace(/[\[\]]/g, '') // remove [ and ]
            .split(/\n|,/)
            .map(course => course.trim())
            .filter(course => course.length > 0);
    
        console.log('Parsed Courses:', courses);
    
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
                console.log(`Course "${course}" has rawDays: ${rawDays}`);
    
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
                    rawDays.split('').forEach(ch => tokens.add(ch));
                }
    
                tokens.forEach(token => {
                    const dayName = dayMap[token];
                    if (dayName) {
                        schedule[dayName].push(course);
                    }
                });
            } else {
                console.warn(`No days found in course string: ${course}`);
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
    

    // Auto-check the PDF and run the filter when the page loads
    checkAndRunFilter();
});
