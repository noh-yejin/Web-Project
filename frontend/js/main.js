const form = document.getElementById('diary-form');
const textarea = document.getElementById('diary-text');
const dateInput = document.getElementById('entry-date');
const resultBox = document.getElementById('analysis-result');
const sentimentSpan = document.getElementById('result-sentiment');
const keywordsSpan = document.getElementById('result-keywords');
const adviceSpan = document.getElementById('result-advice');

form.addEventListener('submit', function(event) {
  event.preventDefault();
  const text = textarea.value.trim();
  const date = dateInput.value;
  if (!text || !date) return;

  const keywords = text.split(/\s+/).filter(word => word.length >= 2).slice(0, 3);
  const sentiments = ['Positive', 'Negative', 'Neutral'];
  const sentiment = sentiments[Math.floor(Math.random() * 3)];

  const adviceMap = {
    'Positive': 'Keep up the great energy! 😊',
    'Negative': 'Take a break and be kind to yourself today.',
    'Neutral': 'Even calm days are meaningful. Appreciate yourself!'
  };

  sentimentSpan.textContent = sentiment;
  keywordsSpan.textContent = keywords.join(', ');
  adviceSpan.textContent = adviceMap[sentiment] || '-';
});
