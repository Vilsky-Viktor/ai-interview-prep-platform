# The FAQ in es; the {placeholders} are filled in by helpers/help.py (faq_values) with
# billing's prices and the number of languages. Questions not translated yet show in English
# (constants/faq/__init__.py).
FAQ = [
    {
        "key": "what",
        "question": "¿Qué es prepza?",
        "answer": "Una entrevista cronometrada creada a partir de tu descripción del puesto, para cualquier puesto. Úsala para filtrar candidatos antes de conocerlos o como un paso más de la contratación: en ambos casos ves quién domina de verdad el trabajo.",
    },
    {
        "key": "roles",
        "question": "¿Para qué puestos puedo contratar?",
        "answer": "Cualquier puesto en el que importen los conocimientos: soporte, ventas, finanzas, salud, oficios, ingeniería, marketing y más. Si puedes describir el trabajo, prepza puede crear una entrevista para él.",
    },
    {
        "key": "hiring",
        "question": "¿Cómo funciona?",
        "answer": "Pega una descripción del puesto en la página de inicio, pon el nombre de tu empresa y revisa los temas que propone prepza. Después invita a candidatos: escribe sus correos, pega una lista o sube un archivo. Los candidatos que no hayan empezado tras unos días reciben un recordatorio. Cada candidato recibe sus propias preguntas, cada una con su temporizador, y ves su puntuación y cada respuesta en cuanto termina.",
    },
    {
        "key": "link",
        "question": "¿Puedo poner una entrevista en una oferta de empleo?",
        "answer": "Sí. Activa el enlace para compartir de la entrevista en su pestaña Candidatos y pégalo en tu oferta. Cualquiera que lo abra inicia sesión y hace la entrevista, y cada persona cuesta lo mismo que un candidato invitado. El enlace se desactiva cuando marcas el puesto de la entrevista como cubierto.",
    },
    {
        "key": "preview",
        "question": "¿Puedo probar una entrevista antes de invitar a nadie?",
        "answer": "Sí. Abre tu entrevista como candidato desde su página, sin coste: las vistas previas no aparecen entre tus candidatos ni en las estadísticas de preguntas. También puedes hacer cualquiera de las entrevistas de práctica gratuitas.",
    },
    {
        "key": "cheating",
        "question": "¿Pueden los candidatos usar IA o buscar las respuestas?",
        "answer": "Cada candidato recibe sus propias preguntas aleatorias en su propio orden, con un temporizador en cada pregunta que controla nuestro servidor, así que hay poco tiempo para buscar las respuestas o preguntar a una IA. Las fichas de evaluación también muestran cuándo un candidato salió de la página, copió texto o respondió demasiado rápido para haber leído la pregunta.",
    },
    {
        "key": "cost",
        "question": "¿Cuánto cuesta?",
        "answer": "Generar entrevistas es gratis. Cada candidato que responde al menos una pregunta cuesta {candidate} créditos ({candidate_dollars} $), y menos con créditos de recargas más grandes, hasta 1 $. Tu primera empresa recibe {company} créditos gratis, suficientes para sus primeros {company_candidates} candidatos. La página de precios muestra todos los precios.",
    },
    {
        "key": "charged",
        "question": "¿Cuándo se cobra por un candidato?",
        "answer": "Solo cuando termina la entrevista habiendo respondido al menos una pregunta. Sus créditos se reservan cuando lo invitas y se te devuelven si revocas la invitación, si nunca empieza o si no responde nada.",
    },
    {
        "key": "compare_hiring",
        "question": "¿Cómo se compara el precio con otras herramientas de evaluación?",
        "answer": "Muchas herramientas de evaluación se venden como suscripción mensual o anual, que pagas aunque no evalúes a nadie. Con prepza pagas solo por candidato: {candidate} créditos ({candidate_dollars} $), sin contrato, sin cuotas por usuario y sin pagar por generar una entrevista. Una empresa que invita a {example_candidates} candidatos al mes paga unos {example_year_dollars} $ al año. Si evalúas a muchos candidatos cada mes, una suscripción puede salir más barata, así que compara con tus propias cifras.",
    },
    {
        "key": "expire",
        "question": "¿Caducan los créditos?",
        "answer": "No. Los créditos nunca caducan y no hay suscripciones ni renovaciones.",
    },
    {
        "key": "refunds",
        "question": "¿Puedo obtener un reembolso?",
        "answer": "Sí, de los créditos que compraste en los últimos 14 días y no has gastado: a través de Paddle o escribiéndonos. Los créditos gratis, como el regalo de bienvenida, no se reembolsan. Los términos tienen los detalles.",
    },
    {
        "key": "scorecards",
        "question": "¿Qué muestran las fichas de evaluación?",
        "answer": "Cada respuesta, si fue correcta y cuánto tardó. Las notas se ven en verde o rojo según la nota de aprobado que fijaste para la entrevista. Las fichas también señalan respuestas demasiado rápidas para haber leído la pregunta, las veces que el candidato salió de la página y los intentos de copiar.",
    },
    {
        "key": "reports",
        "question": "¿Puedo compartir los resultados con un responsable de contratación?",
        "answer": "Sí. Descarga un informe PDF de un candidato o de todos los candidatos de una entrevista, envíalo por correo directamente desde prepza o manda un breve resumen por WhatsApp o Telegram.",
    },
    {
        "key": "candidates",
        "question": "¿Qué ven los candidatos?",
        "answer": "El nombre y el logo de tu empresa, qué esperar antes de empezar y luego una pregunta cronometrada cada vez. Nunca ven su puntuación ni si una respuesta fue correcta.",
    },
    {
        "key": "verified",
        "question": "¿Qué significa la marca de verificación?",
        "answer": "Que un propietario o administrador de la empresa inició sesión con un correo de trabajo del sitio web de la empresa, como tu@acme.com, y que después nuestro equipo revisó la empresa. Añade el sitio web con Verificar en la cabecera de tu empresa; los servicios de correo gratuitos no cuentan. Mientras la revisión está pendiente, tu equipo ve un reloj junto al nombre, y cambiar el nombre de la empresa la envía de nuevo a revisión. La marca aparece junto al nombre de tu empresa, también en las invitaciones.",
    },
    {
        "key": "languages",
        "question": "¿Qué idiomas se admiten?",
        "answer": "{count} idiomas, para el sitio, las entrevistas y los correos. Elige el idioma en que se escribe una entrevista, sea cual sea el idioma de la descripción del puesto.",
    },
    {
        "key": "privacy",
        "question": "¿Qué pasa con las descripciones de puesto y las respuestas?",
        "answer": "Las descripciones de puesto se usan para crear tus entrevistas, y las respuestas de los candidatos para puntuarlas, solo para tu empresa. La política de privacidad explica qué guardamos, durante cuánto tiempo y los derechos de cada persona.",
    },
    {
        "key": "delete",
        "question": "¿Puedo eliminar mi cuenta?",
        "answer": "Sí, en Ajustes. Tu cuenta y tus datos se eliminan, y antes puedes descargar una copia de tus datos.",
    },
]
