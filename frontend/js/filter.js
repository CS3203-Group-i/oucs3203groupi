document.addEventListener("DOMContentLoaded", function() {
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

    // Auto-check the PDF and run the filter when the page loads
    checkAndRunFilter();
});
