// mood-chart.js - For handling mood tracking visualization

document.addEventListener('DOMContentLoaded', function() {
    const chartElement = document.getElementById('moodChart');
    
    if (chartElement) {
        // Fetch mood data from the API
        fetch('/mood/api/mood-data')
            .then(response => response.json())
            .then(data => {
                initMoodChart(chartElement, data);
            })
            .catch(error => {
                console.error('Error fetching mood data:', error);
                displayError(chartElement);
            });
    }

    // Initialize time period filters
    const timeFilters = document.querySelectorAll('.time-filter');
    timeFilters.forEach(filter => {
        filter.addEventListener('click', function(e) {
            e.preventDefault();
            const days = this.dataset.days;
            
            // Update active class
            timeFilters.forEach(f => f.classList.remove('active'));
            this.classList.add('active');
            
            // Fetch data for the selected period
            fetch(`/mood/api/mood-data?days=${days}`)
                .then(response => response.json())
                .then(data => {
                    // Update the chart
                    if (window.moodChart) {
                        window.moodChart.data.labels = data.labels;
                        window.moodChart.data.datasets[0].data = data.values;
                        window.moodChart.update();
                    }
                })
                .catch(error => {
                    console.error('Error fetching mood data:', error);
                });
        });
    });
});

function initMoodChart(element, data) {
    // Set default options
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                titleColor: '#2D3748',
                bodyColor: '#2D3748',
                borderColor: '#E2E8F0',
                borderWidth: 1,
                cornerRadius: 12,
                displayColors: false,
                callbacks: {
                    label: function(context) {
                        const score = context.raw;
                        let moodDescription = '';
                        
                        if (score >= 9) moodDescription = 'Excellent';
                        else if (score >= 7) moodDescription = 'Very Good';
                        else if (score >= 5) moodDescription = 'Good';
                        else if (score >= 3) moodDescription = 'Fair';
                        else moodDescription = 'Poor';
                        
                        return `Mood: ${score}/10 (${moodDescription})`;
                    }
                }
            }
        },
        scales: {
            y: {
                min: 0,
                max: 10,
                ticks: {
                    stepSize: 1,
                    callback: function(value) {
                        if (value === 0) return '';
                        if (value === 10) return 'Excellent';
                        if (value === 7) return 'Good';
                        if (value === 4) return 'Fair';
                        if (value === 1) return 'Poor';
                        return value;
                    }
                },
                grid: {
                    color: 'rgba(0, 0, 0, 0.05)'
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        },
        elements: {
            line: {
                tension: 0.4
            },
            point: {
                radius: 4,
                hitRadius: 8,
                hoverRadius: 6,
                borderWidth: 2,
                backgroundColor: function(context) {
                    const value = context.raw;
                    
                    if (value >= 8) return '#68D391'; // Success/green for high mood
                    if (value >= 5) return '#5B8EE6'; // Primary/blue for average mood
                    if (value >= 3) return '#FFB084'; // Accent/orange for below average
                    return '#FF6B6B'; // Warning/red for low mood
                }
            }
        }
    };

    // Create the chart
    window.moodChart = new Chart(element, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Mood Level',
                data: data.values,
                borderColor: 'rgba(91, 142, 230, 1)',
                borderWidth: 2,
                fill: true
            }]
        },
        options: options
    });

    // Add gradient background
    const ctx = element.getContext('2d');
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(91, 142, 230, 0.2)');
    gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
    
    window.moodChart.data.datasets[0].backgroundColor = gradient;
    window.moodChart.update();
}

function displayError(element) {
    // Display an error message when chart data can't be loaded
    element.style.height = '200px';
    element.style.display = 'flex';
    element.style.alignItems = 'center';
    element.style.justifyContent = 'center';
    element.style.background = '#f8f9fa';
    element.style.color = '#dc3545';
    element.style.borderRadius = '12px';
    element.style.fontSize = '16px';
    element.innerHTML = '<div><i class="bi bi-exclamation-triangle me-2"></i>Unable to load mood data. Please try again later.</div>';
}

// Export mood data to CSV
function exportMoodData() {
    fetch('/mood/api/mood-data?days=365')  // Get a full year of data
        .then(response => response.json())
        .then(data => {
            // Convert to CSV format
            const csvRows = [];
            
            // Add header row
            csvRows.push(['Date', 'Mood Score', 'Notes', 'Tags']);
            
            // Add data rows
            for (let i = 0; i < data.labels.length; i++) {
                csvRows.push([
                    data.labels[i],
                    data.values[i],
                    data.notes[i] || '',
                    data.tags[i] || ''
                ]);
            }
            
            // Convert to CSV string
            const csvContent = csvRows.map(row => row.join(',')).join('\n');
            
            // Create download link
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.setAttribute('href', url);
            link.setAttribute('download', 'mood_data.csv');
            link.style.display = 'none';
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        })
        .catch(error => {
            console.error('Error exporting mood data:', error);
            alert('Unable to export mood data. Please try again later.');
        });
}
