document.getElementById('verifyBtn').addEventListener('click', async () => {
    const newsInput = document.getElementById('newsInput').value;
    const verifyBtn = document.getElementById('verifyBtn');
    const loading = document.getElementById('loading');
    const resultCard = document.getElementById('resultCard');
    const verdictBadge = document.getElementById('verdictBadge');
    const justificationText = document.getElementById('justificationText');
    const redFlagsList = document.getElementById('redFlagsList');

    if (!newsInput.trim()) {
        alert("Please paste some text before running the analysis!");
        return;
    }

    loading.classList.remove('hidden');
    resultCard.classList.add('hidden');
    verifyBtn.disabled = true;

    try {
        const response = await fetch('/api/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ article_text: newsInput })
        });

        if (!response.ok) throw new Error("API Execution Failure");

        const data = await response.json();

        if (data.veracity_score < 0.5) {
            verdictBadge.textContent = `🔴 VERDICT: FAKE (Score: ${data.veracity_score})`;
            verdictBadge.className = "badge fake";
        } else {
            verdictBadge.textContent = `🟢 VERDICT: REAL (Score: ${data.veracity_score})`;
            verdictBadge.className = "badge real";
        }

        justificationText.textContent = data.justification;

        redFlagsList.innerHTML = "";
        if (data.red_flags && data.red_flags.length > 0) {
            data.red_flags.forEach(flag => {
                const li = document.createElement('li');
                li.textContent = flag;
                redFlagsList.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.textContent = "No standard visual or contextual red flags caught.";
            redFlagsList.appendChild(li);
        }

        resultCard.classList.remove('hidden');

    } catch (error) {
        alert("Could not reach backend framework agents. Confirm server status.");
        console.error(error);
    } finally {
        loading.classList.add('hidden');
        verifyBtn.disabled = false;
    }
});