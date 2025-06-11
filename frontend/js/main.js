
const form = document.getElementById('diary-form');
const textarea = document.getElementById('diary-text');
const dateInput = document.getElementById('entry-date');
const resultBox = document.getElementById('analysis-result');
const sentimentSpan = document.getElementById('result-sentiment');
const adviceSpan = document.getElementById('result-advice');
const recommendationSpan = document.getElementById('result-recommendation');

form.addEventListener('submit', async function(event) {
    event.preventDefault();
    const text = textarea.value.trim();
    const date = dateInput.value;
    const userId = sessionStorage.getItem("user_id") || "anonymous";

    if (!text || !date) return;

    try {
    const response = await fetch("/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
        text: text,
        entry_date: date,
        user_id: userId
        })
    });

    const result = await response.json();

    if (response.status === 409) {
        sentimentSpan.textContent = result.emotion || "-";
        adviceSpan.textContent = result.message || "-";
        alert("⚠️ You've already analyzed this input for today.\nWe're showing the existing result.");
    } else if (response.ok) {
        sentimentSpan.textContent = result.emotion || "-";
        adviceSpan.textContent = result.message || "-";
        recommendationSpan.textContent = result.recommendation || "-";
    } else {
        alert("Emotion analysis failed. Please try again.");
    }

    resultBox.style.display = "block";

    } catch (error) {
    console.error("Emotion analysis failed:", error);
    alert("Failed to analyze emotion. Please try again.");
    }
});
