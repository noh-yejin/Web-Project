
async function fetchData() {
    const userId = sessionStorage.getItem("user_id");
    if (!userId) {
    alert("Login required.");
    window.location.href = "/static/html/login.html";
    return;
    }

    const res = await fetch(`/weekly_emotions?user_id=${userId}`);
    return await res.json();
}

function renderChart(labels, scores) {
    const ctx = document.getElementById("emotionChart").getContext("2d");

    const backgroundColors = scores.map(score => {
    if (score === 2) return "#2ecc71";
    if (score === 1) return "#f1c40f";
    if (score === 0) return "#95a5a6";
    if (score === -1) return "#e67e22";
    if (score === -2) return "#e74c3c";
    return "#bdc3c7";
    });

    new Chart(ctx, {
    type: 'bar',
    data: {
        labels: labels,
        datasets: [{
        label: "Emotion Score",
        data: scores,
        backgroundColor: backgroundColors,
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
        y: {
            min: -2,
            max: 2,
            ticks: {
            stepSize: 1,
            callback: val => ({ "-2": "😢", "-1": "😟", "0": "😐", "1": "🙂", "2": "😄" }[val] || val)
            }
        }
        },
        plugins: {
        legend: { display: false }
        }
    }
    });
}

async function init() {
    const { labels, scores, message } = await fetchData();
    renderChart(labels, scores);
    document.getElementById("emotion-comment").textContent = message;
}

init();
