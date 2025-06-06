const yearSelect = document.getElementById("year-select");
const monthSelect = document.getElementById("month-select");
const calendarGrid = document.getElementById("calendar-grid");

const emojiMap = {
  "-2": "😢",
  "-1": "😟",
  "0": "😐",
  "1": "🙂",
  "2": "😄"
};

const currentDate = new Date();

// 연도 & 월 선택 박스 초기화
for (let y = 2020; y <= currentDate.getFullYear() + 1; y++) {
  const option = document.createElement("option");
  option.value = y;
  option.textContent = y;
  yearSelect.appendChild(option);
}

for (let m = 1; m <= 12; m++) {
  const option = document.createElement("option");
  option.value = m;
  option.textContent = m;
  monthSelect.appendChild(option);
}

yearSelect.value = currentDate.getFullYear();
monthSelect.value = currentDate.getMonth() + 1;

// 사용자 감정 데이터 불러오기
async function fetchEmotionData(year, month) {
  const userId = sessionStorage.getItem("user_id");
  if (!userId) {
    alert("You must be logged in.");
    window.location.href = "/static/html/login.html";
    return [];
  }

  try {
    const res = await fetch(`/calendar_data?user_id=${userId}&year=${year}&month=${month}`);
    return await res.json();
  } catch (err) {
    console.error("Error fetching calendar data:", err);
    return [];
  }
}

// 점수에 따른 CSS 클래스
function getClassFromScore(score) {
  return {
    "2": "very-positive",
    "1": "positive",
    "0": "neutral",
    "-1": "negative",
    "-2": "very-negative"
  }[String(score)] || "";
}

// 달력 렌더링
function renderCalendar(year, month, emotionData) {
  const firstDay = new Date(year, month - 1, 1).getDay();
  const daysInMonth = new Date(year, month, 0).getDate();
  calendarGrid.innerHTML = "";

  // 빈 셀 추가 (월 시작 요일에 맞게)
  for (let i = 0; i < firstDay; i++) {
    const empty = document.createElement("div");
    empty.className = "calendar-cell";
    calendarGrid.appendChild(empty);
  }

  for (let day = 1; day <= daysInMonth; day++) {
    const info = emotionData.find(e => e.day === day);
    const score = info ? info.score : null;
    const emotion = info ? info.emotion : "";

    const cell = document.createElement("div");
    cell.className = `calendar-cell ${getClassFromScore(score)}`;
    cell.innerHTML = `<strong>${day}</strong><br>${emotion || ""}`;

    if (score !== null) {
      const emoji = document.createElement("div");
      emoji.className = "emoji";
      emoji.textContent = emojiMap[score] || "";
      cell.appendChild(emoji);
    }

    calendarGrid.appendChild(cell);
  }
}

// 달력 업데이트
async function updateCalendar() {
  const year = parseInt(yearSelect.value);
  const month = parseInt(monthSelect.value);
  const data = await fetchEmotionData(year, month);
  renderCalendar(year, month, data);
}

yearSelect.addEventListener("change", updateCalendar);
monthSelect.addEventListener("change", updateCalendar);

// 페이지 로딩 시 오늘 기준 렌더링
updateCalendar();
