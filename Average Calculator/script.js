document.getElementById('calcForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const numberId = document.getElementById('numberId').value;
    const response = await fetch(`https://your-flask-app-url/numbers/${numberId}`);
    const data = await response.json();

    document.getElementById('prevState').innerText = `Previous State: ${data.windowPrevState}`;
    document.getElementById('currState').innerText = `Current State: ${data.windowCurrState}`;
    document.getElementById('numbers').innerText = `Numbers: ${data.numbers}`;
    document.getElementById('average').innerText = `Average: ${data.avg}`;
});
