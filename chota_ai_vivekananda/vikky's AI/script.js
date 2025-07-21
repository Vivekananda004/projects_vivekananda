const input = document.getElementById('inp');
const btn = document.getElementById('askBtn');
const convsDiv = document.getElementById('convs');
const historyList = document.getElementById('history-list');
let convs = [];

// Auto-grow textarea
input.addEventListener('input', () => {
  input.style.height = 'auto';
  input.style.height = input.scrollHeight + 'px';
});

btn.addEventListener('click', () => {
  const userText = input.value.trim();
  if (!userText) return;

  fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=AIzaSyCYlK_K7PUuNoVfLOlgpt16BwBEBbQW5XU`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [
          {
            parts: [
              {
                text:
                  "You are a sarcastic and funny assistant. Always give wrong and humorous answers with easy words. Question: " +
                  userText,
              },
            ],
          },
        ],
      }),
    }
  )
    .then((res) => res.json())
    .then((data) => {
      const answer = data.candidates[0]?.content?.parts[0]?.text || "Oops! Try again.";
      const obj = { myQue: userText, AIresponse: answer };
      convs.push(obj);
      displayData(convs);
      updateHistory(userText);
    })
    .catch((err) => console.error(err));
});

function displayData(arr) {
  convsDiv.innerHTML = '';
  arr.forEach((e) => {
    const q = document.createElement('p');
    q.textContent = "🧑‍💻 You: " + e.myQue;
    const a = document.createElement('p');
    a.textContent = "🤖 Vikky AI: " + e.AIresponse;
    convsDiv.append(q, a);
  });
  input.value = '';
  input.style.height = 'auto';
}

function updateHistory(question) {
  const li = document.createElement('li');
  li.textContent = question;
  historyList.prepend(li);
}
