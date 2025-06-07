// 주간 감정 데이터 불러오기
// Fetch weekly emotion data
async function fetchData() {
    const userId = sessionStorage.getItem("user_id");
    if (!userId) {
        alert("Login required."); // 로그인 필요
        window.location.href = "/static/html/login.html";
        return;
    }

    const res = await fetch(`/weekly_emotions?user_id=${userId}`);
    return await res.json();
}

// 차트 렌더링
// Render the bar chart
function renderChart(labels, scores) {
    const ctx = document.getElementById("emotionChart").getContext("2d");

    // 감정 점수에 따라 색상 설정
    // Assign background colors based on emotion score
    const backgroundColors = scores.map(score => {
        if (score === 2) return "#2ecc71";    // 매우 긍정적 very positive
        if (score === 1) return "#f1c40f";    // 긍정 positive
        if (score === 0) return "#95a5a6";    // 중립 neutral
        if (score === -1) return "#e67e22";   // 부정 negative
        if (score === -2) return "#e74c3c";   // 매우 부정 very negative
        return "#bdc3c7";                     // 기타 others
    });

    new Chart(ctx, {
        type: 'bar', // 막대그래프 bar chart
        data: {
            labels: labels, // 날짜 등 라벨 label
            datasets: [{
                label: "Emotion Score", // 데이터 레이블 label
                data: scores,           // 감정 점수 data
                backgroundColor: backgroundColors // 배경색 background color
            }]
        },
        options: {
            responsive: true, // 반응형 대응 enable responsiveness
            maintainAspectRatio: false, // 비율 고정 해제 do not maintain aspect ratio
            scales: {
                y: {
                    min: -2,
                    max: 2,
                    ticks: {
                        stepSize: 1,
                        // 점수에 따라 이모지 표시
                        // Show emoji based on score
                        callback: val => ({
                            "-2": "😢",
                            "-1": "😟",
                            "0": "😐",
                            "1": "🙂",
                            "2": "😄"
                        }[val] || val)
                    }
                }
            },
            plugins: {
                legend: { display: false } // 범례 제거 hide legend
            }
        }
    });
}

// 초기 실행 함수
// Initialize chart and emotion text on page load
async function init() {
    const { labels, scores, message } = await fetchData();
    renderChart(labels, scores);
    document.getElementById("emotion-comment").textContent = message; // 메시지 표시 show message
}

init(); // 실행 start
