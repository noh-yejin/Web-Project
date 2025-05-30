// document.addEventListener("DOMContentLoaded", () => {
//   document.getElementById('analyzeBtn').addEventListener('click', sendMessage);
// });

// async function sendMessage() {
//   const entry = document.getElementById('message').value;

//   const response = await fetch("http://localhost:8000/analyze", {
//     method: "POST",
//     headers: {
//         "Content-Type": "application/json"
//     },
//     body: JSON.stringify({ text: entry })
// });

// if (!response.ok) {
//     const errorText = await response.text();
//     console.error("서버 오류:", errorText);
//     return;
// }

//   const result = await response.json();
//   console.log(result);
  
//   const feedbackDiv = document.getElementById('response');
//   feedbackDiv.textContent = `감정: ${result.emotion}\n조언: ${result.message}`;

//   const emotionColorMap = {
//     happiness: '#fff7b3',
//     sadness: '#b3d1ff',
//     anger: '#ffb3b3',
//     calm: '#ccffcc',
//   };

//   document.body.style.backgroundColor = emotionColorMap[result.emotion] || '#f3f3f3';
// }


// document.addEventListener("DOMContentLoaded", () => {
//   const form = document.getElementById('diary-form');
//   form.addEventListener('submit', analyzeDiary);
// });

// async function analyzeDiary(event) {
//   event.preventDefault();
  
//   const date = document.getElementById('entry-date').value;
//   const text = document.getElementById('diary-text').value.trim();
//   if (!date || !text) return;

//   // LLM에 감정 분석 요청
//   const response = await fetch("http://localhost:8000/analyze", {
//     method: "POST",
//     headers: {
//       "Content-Type": "application/json"
//     },
//     body: JSON.stringify({ text: text })
//   });

//   if (!response.ok) {
//     const errorText = await response.text();
//     console.error("서버 오류:", errorText);
//     alert("감정 분석에 실패했습니다.");
//     return;
//   }

//   const result = await response.json();
//   console.log(result);

//   // HTML에 결과 표시
//   const resultBox = document.getElementById('analysis-result');
//   const sentimentSpan = document.getElementById('result-sentiment');
//   const keywordsSpan = document.getElementById('result-keywords');
//   const advicePara = document.getElementById('result-advice');

//   // 키워드는 단순 예시로 추출 (추가적으로 LLM에서 받아올 수도 있음)
//   const keywords = text.split(/\s+/).filter(word => word.length >= 2).slice(0, 3);

//   sentimentSpan.textContent = result.emotion;
//   keywordsSpan.textContent = keywords.join(', ');
//   advicePara.textContent = result.message;
//   resultBox.style.display = 'block';
// }

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById('diary-form');
  form.addEventListener('submit', analyzeDiary);
});

async function analyzeDiary(event) {
  event.preventDefault();

  const date = document.getElementById('entry-date').value;
  const text = document.getElementById('diary-text').value.trim();
  if (!date || !text) {
    alert("날짜와 내용을 모두 입력해주세요!");
    return;
  }

  try {
    // LLM에 감정 분석 요청
    const response = await fetch("/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ text: text })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("서버 오류:", errorText);
      alert("감정 분석에 실패했습니다. 다시 시도해 주세요.");
      return;
    }

    const result = await response.json();
    console.log(result);

    // HTML에 결과 표시
    const resultBox = document.getElementById('analysis-result');
    const sentimentSpan = document.getElementById('result-sentiment');
    const keywordsSpan = document.getElementById('result-keywords');
    const advicePara = document.getElementById('result-advice');

    // 키워드는 예시로 입력된 텍스트에서 간단히 추출
    const keywords = text.split(/\s+/).filter(word => word.length >= 2).slice(0, 3);

    sentimentSpan.textContent = result.emotion;
    keywordsSpan.textContent = keywords.join(', ');
    advicePara.textContent = result.message;

    resultBox.style.display = 'block';
  } catch (error) {
    console.error("분석 요청 중 오류:", error);
    alert("오류가 발생했습니다. 잠시 후 다시 시도해 주세요.");
  }
}
