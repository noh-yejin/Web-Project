const ctx = document.getElementById('emotionChart').getContext('2d');

const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const data = [3, 2, 1, 2, 3, 2, 1];

const backgroundColors = data.map(val => {
  if (val === 1) return '#e74c3c';     // Negative
  if (val === 2) return '#f39c12';     // Neutral
  if (val === 3) return '#2ecc71';     // Positive
});

new Chart(ctx, {
  type: 'bar',
  data: {
    labels: labels,
    datasets: [{
      label: 'Emotion Level',
      data: data,
      backgroundColor: backgroundColors,
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        min: 0,
        max: 3,
        ticks: {
          stepSize: 1,
          callback: function(value) {
            return value === 1 ? 'Negative' :
                   value === 2 ? 'Neutral' :
                   value === 3 ? 'Positive' : value;
          }
        }
      }
    },
    plugins: {
      legend: { display: false }
    }
  }
});
