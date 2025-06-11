// 감정 캘린더 페이지를 위한 스크립트입니다.
// Script for rendering an emotion calendar based on user data.

const yearSelect = document.getElementById("year-select"); // 연도 선택 셀렉트 / Year select element
const monthSelect = document.getElementById("month-select"); // 월 선택 셀렉트 / Month select element
const calendarGrid = document.getElementById("calendar-grid"); // 달력 셀 그리드 / Calendar grid container

// 감정 점수에 대응하는 이모지 / Emoji representation for emotion scores
const emojiMap = {
  "-2": "😢", // 매우 부정적 / Very negative
  "-1": "😟", // 부정적 / Negative
  "0": "😐",  // 중립 / Neutral
  "1": "🙂",  // 긍정적 / Positive
  "2": "😄"   // 매우 긍정적 / Very positive
};

const currentDate = new Date(); // 현재 날짜 / Current date

// 연도 선택 박스 초기화 / Initialize year dropdown
for (let y = 2020; y <= currentDate.getFullYear() + 1; y++) {
  const option = document.createElement("option");
  option.value = y;
  option.textContent = y;
  yearSelect.appendChild(option);
}

// 월 선택 박스 초기화 / Initialize month dropdown
for (let m = 1; m <= 12; m++) {
  const option = document.createElement("option");
  option.value = m;
  option.textContent = m;
  monthSelect.appendChild(option);
}

yearSelect.value = currentDate.getFullYear();      // 현재 연도 선택 / Set current year
monthSelect.value = currentDate.getMonth() + 1;    // 현재 월 선택 / Set current month

// 사용자 감정 데이터 가져오기 / Fetch emotion data for the given month/year
async function fetchEmotionData(year, month) {
  const userId = sessionStorage.getItem("user_id");
  if (!userId) {
    alert("You must be logged in."); // 로그인 필요 알림 / Alert login required
    window.location.href = "/static/html/login.html"; // 로그인 페이지로 이동 / Redirect to login
    return [];
  }

  try {
    const res = await fetch(`/calendar_data?user_id=${userId}&year=${year}&month=${month}`);
    return await res.json(); // JSON 응답 반환 / Return JSON response
  } catch (err) {
    console.error("Error fetching calendar data:", err); // 오류 출력 / Log error
    return [];
  }
}

// 감정 점수에 따라 CSS 클래스 반환 / Map emotion score to CSS class
function getClassFromScore(score) {
  return {
    "2": "very-positive",
    "1": "positive",
    "0": "neutral",
    "-1": "negative",
    "-2": "very-negative"
  }[String(score)] || "";
}

// 달력 렌더링 함수 / Render calendar with emotion data
function renderCalendar(year, month, emotionData) {
  const firstDay = new Date(year, month - 1, 1).getDay(); // 해당 월의 시작 요일 / Day of week of first date
  const daysInMonth = new Date(year, month, 0).getDate(); // 해당 월의 일 수 / Number of days in month
  calendarGrid.innerHTML = ""; // 기존 달력 초기화 / Clear previous content

  // 시작 요일 이전 빈 셀 추가 / Add empty cells for alignment
  for (let i = 0; i < firstDay; i++) {
    const empty = document.createElement("div");
    empty.className = "calendar-cell";
    calendarGrid.appendChild(empty);
  }

  // 날짜 셀 생성 및 감정 데이터 반영 / Create date cells with emotion data
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

// 달력 업데이트 트리거 / Trigger calendar rendering
async function updateCalendar() {
  const year = parseInt(yearSelect.value);
  const month = parseInt(monthSelect.value);
  const data = await fetchEmotionData(year, month);
  renderCalendar(year, month, data);
}

// 사용자 선택 이벤트 리스너 추가 / Add event listeners for dropdowns
yearSelect.addEventListener("change", updateCalendar);
monthSelect.addEventListener("change", updateCalendar);

// 초기 로딩 시 현재 날짜 기준으로 렌더링 / Initial rendering for current date
updateCalendar();