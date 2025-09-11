// Chart initialization function
function initChart() {
    const canvas = document.getElementById('citizenDeveloperChart');
    if (!canvas) {
        return;
    }
    const ctx = canvas.getContext('2d');
    
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [
                ['Aug', '2020'], ['Feb', '2021'], ['Aug', '2021'], ['Feb', '2022'], 
                ['Aug', '2022'], ['Feb', '2023'], ['Aug', '2023'], ['Feb', '2024'], 
                ['Aug', '2024'], ['May', '2025'], ['Aug', '2025']
            ],
            datasets: [{
                label: 'Search Interest',
                data: [10, 8, 13, 16, 20, 25, 20, 22, 18, 32, 100],
                borderColor: '#888',
                backgroundColor: 'rgba(136, 136, 136, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.3,
                pointBackgroundColor: '#888',
                pointBorderColor: '#888',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'The Rise of Citizen Developers',
                    color: '#ffffff',
                    font: { size: 22, weight: '600' },
                    padding: 20
                },
                subtitle: {
                    display: true,
                    text: 'Google Trends: "citizen developer" search popularity',
                    color: '#999999',
                    font: { size: 12 },
                    padding: 10
                },
                legend: { display: false }
            },
            scales: {
                x: {
                    title: { display: true, text: 'Time Period', color: '#999999' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { 
                        color: '#cccccc',
                        maxRotation: 0,
                        minRotation: 0,
                        font: { size: 11 }
                    }
                },
                y: {
                    beginAtZero: true,
                    max: 105,
                    title: { display: true, text: 'Search Interest (0-100)', color: '#999999' },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { 
                        color: '#cccccc', 
                        stepSize: 20, 
                        font: { size: 12 },
                        callback: function(value, index, values) {
                            return [0, 20, 40, 60, 80, 100].includes(value) ? value : '';
                        }
                    }
                }
            },
            animation: { duration: 2000, easing: 'easeInOutQuart' }
        }
    });
}

// Make function globally available
window.addEventListener('load', async () => {    
    setTimeout(() => {
        initChart();
    }, 100);
});
