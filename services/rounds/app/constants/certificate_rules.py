from app.constants.rounds import CERTIFICATE_MIN_SCORE

_SCORE = CERTIFICATE_MIN_SCORE

# Shown to learners before they practice, by language; the pass mark comes from
# CERTIFICATE_MIN_SCORE.
CERTIFICATE_RULES = {
    "en": [
        "Answer every question of the topic.",
        "Only your latest answer to each question counts.",
        f"At least {_SCORE}% of answers must be correct.",
    ],
    "ru": [
        "Ответьте на все вопросы темы.",
        "Учитывается только последний ответ на каждый вопрос.",
        f"Не меньше {_SCORE}% ответов должны быть верными.",
    ],
    "uk": [
        "Дайте відповідь на всі питання теми.",
        "Враховується лише остання відповідь на кожне питання.",
        f"Не менше {_SCORE}% відповідей мають бути правильними.",
    ],
    "es": [
        "Responde todas las preguntas del tema.",
        "Solo cuenta tu última respuesta a cada pregunta.",
        f"Al menos el {_SCORE}% de tus respuestas deben ser correctas.",
    ],
    "pt": [
        "Responda todas as questões do tópico.",
        "Só conta sua última resposta a cada questão.",
        f"Pelo menos {_SCORE}% das suas respostas devem estar corretas.",
    ],
    "de": [
        "Beantworte jede Frage des Themas.",
        "Nur deine letzte Antwort auf jede Frage zählt.",
        f"Mindestens {_SCORE} % deiner Antworten müssen richtig sein.",
    ],
    "fr": [
        "Répondez à toutes les questions du thème.",
        "Seule votre dernière réponse à chaque question compte.",
        f"Au moins {_SCORE} % de vos réponses doivent être justes.",
    ],
    "it": [
        "Rispondi a tutte le domande dell'argomento.",
        "Conta solo la tua ultima risposta a ogni domanda.",
        f"Almeno il {_SCORE}% delle tue risposte deve essere corretto.",
    ],
    "pl": [
        "Odpowiedz na wszystkie pytania tematu.",
        "Liczy się tylko twoja ostatnia odpowiedź na każde pytanie.",
        f"Co najmniej {_SCORE}% odpowiedzi musi być poprawnych.",
    ],
    "nl": [
        "Beantwoord elke vraag van het onderwerp.",
        "Alleen je laatste antwoord op elke vraag telt.",
        f"Minstens {_SCORE}% van je antwoorden moet goed zijn.",
    ],
    "tr": [
        "Konunun tüm sorularını yanıtlayın.",
        "Her soruya verdiğiniz yalnızca son yanıt sayılır.",
        f"Yanıtlarınızın en az %{_SCORE}'i doğru olmalı.",
    ],
    "ar": [
        "أجب عن جميع أسئلة الموضوع.",
        "تُحتسب آخر إجابة لك عن كل سؤال فقط.",
        f"يجب أن تكون {_SCORE}% على الأقل من إجاباتك صحيحة.",
    ],
    "he": [
        "ענו על כל שאלות הנושא.",
        "רק התשובה האחרונה שלכם לכל שאלה נספרת.",
        f"לפחות {_SCORE}% מהתשובות שלכם צריכות להיות נכונות.",
    ],
    "fa": [
        "به همهٔ پرسش‌های موضوع پاسخ دهید.",
        "فقط آخرین پاسخ شما به هر پرسش حساب می‌شود.",
        f"دست‌کم {_SCORE}٪ پاسخ‌هایتان باید درست باشد.",
    ],
    "ja": [
        "トピックのすべての問題に答えてください。",
        "各問題の最新の回答だけが数えられます。",
        f"回答の {_SCORE}% 以上が正解である必要があります。",
    ],
    "zh": [
        "回答该主题的所有题目。",
        "每道题只计算你最近一次的答案。",
        f"至少 {_SCORE}% 的答案必须正确。",
    ],
    "ko": [
        "주제의 모든 문제에 답하세요.",
        "문제마다 가장 최근 답만 반영됩니다.",
        f"답의 {_SCORE}% 이상이 정답이어야 합니다.",
    ],
    "hi": [
        "विषय के हर सवाल का जवाब दें।",
        "हर सवाल पर सिर्फ़ आपका आखिरी जवाब गिना जाता है।",
        f"कम से कम {_SCORE}% जवाब सही होने चाहिए।",
    ],
    "id": [
        "Jawab semua soal dalam topik.",
        "Hanya jawaban terakhirmu untuk setiap soal yang dihitung.",
        f"Minimal {_SCORE}% jawabanmu harus benar.",
    ],
    "th": [
        "ตอบทุกคำถามในหัวข้อ",
        "นับเฉพาะคำตอบล่าสุดของแต่ละคำถาม",
        f"คำตอบต้องถูกอย่างน้อย {_SCORE}%",
    ],
    "vi": [
        "Trả lời mọi câu hỏi của chủ đề.",
        "Chỉ câu trả lời gần nhất cho mỗi câu hỏi được tính.",
        f"Ít nhất {_SCORE}% câu trả lời phải đúng.",
    ],
    "fil": [
        "Sagutin ang bawat tanong sa topic.",
        "Ang huling sagot mo lang sa bawat tanong ang binibilang.",
        f"Dapat tama ang hindi bababa sa {_SCORE}% ng mga sagot mo.",
    ],
    "et": [
        "Vasta teema kõigile küsimustele.",
        "Arvesse läheb ainult sinu viimane vastus igale küsimusele.",
        f"Vähemalt {_SCORE}% vastustest peavad olema õiged.",
    ],
}
