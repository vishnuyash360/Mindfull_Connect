// mood-tracker.js - For handling mood tracking visualization

document.addEventListener('DOMContentLoaded', function() {
    const chartElement = document.getElementById('mood-chart');
    
    if (chartElement && window.moodData) {
        const ctx = chartElement.getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: window.moodData.labels,
                datasets: [{
                    label: 'Mood Level',
                    data: window.moodData.values,
                    backgroundColor: 'rgba(91, 142, 230, 0.2)',
                    borderColor: 'rgba(91, 142, 230, 1)',
                    tension: 0.1,
                    pointBackgroundColor: 'rgba(91, 142, 230, 1)',
                    pointRadius: 5,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 10,
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            afterLabel: function(context) {
                                const index = context.dataIndex;
                                let result = [];
                                
                                if (window.moodData.notes[index]) {
                                    result.push(`Notes: ${window.moodData.notes[index]}`);
                                }
                                
                                if (window.moodData.tags[index]) {
                                    result.push(`Tags: ${window.moodData.tags[index]}`);
                                }
                                
                                return result;
                            }
                        }
                    }
                }
            }
        });
    }
});
// ===============================
// Mood Statistics
// ===============================

const statsContainer = document.getElementById("mood-statistics");

if (statsContainer && window.moodData) {

    const values = window.moodData.values;

    const average =
        values.reduce((a, b) => a + b, 0) / values.length;

    const highest = Math.max(...values);
    const lowest = Math.min(...values);

    statsContainer.innerHTML = `
        <div class="row text-center">

            <div class="col-md-4">
                <h2>${average.toFixed(1)}</h2>
                <p class="text-muted">Average Mood</p>
            </div>

            <div class="col-md-4">
                <h2>${highest}</h2>
                <p class="text-muted">Highest</p>
            </div>

            <div class="col-md-4">
                <h2>${lowest}</h2>
                <p class="text-muted">Lowest</p>
            </div>

        </div>
    `;
}