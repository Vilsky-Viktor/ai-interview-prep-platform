# Email texts in Portuguese. Values are filled in with str.format; the HTML version escapes them.

TEXTS = {
    "candidate": {
        "subject": "{company} convida você para uma entrevista",
        "preheader": "Faça “{title}” na prepza. Entre com {email} para começar.",
        "heading": "Convite para entrevista",
        "lines": [
            "{company} convida você para a entrevista “{title}” na prepza.",
            (
                "Entre com {email} para começar. Só este endereço pode fazer a "
                "entrevista, e você tem uma única tentativa."
            ),
        ],
        "button": "Abrir o convite",
    },
    "reminder": {
        "subject": "Lembrete: {company} está esperando sua entrevista",
        "preheader": "“{title}” ainda está aberta. Entre com {email} para começar.",
        "heading": "Sua entrevista está esperando",
        "lines": [
            (
                "{company} convidou você para a entrevista “{title}” na prepza há alguns dias, e "
                "você ainda não começou."
            ),
            (
                "Entre com {email} para começar. Só este endereço pode fazer a entrevista, e você "
                "tem uma única tentativa. O convite expira 30 dias depois de enviado."
            ),
        ],
        "button": "Abrir o convite",
    },
    "report": {
        "subject": "Relatório do candidato: {candidate}",
        "preheader": "{candidate} fez “{title}” na {company}. O relatório está anexado.",
        "heading": "Relatório do candidato",
        "lines": [
            "{sender}, da {company}, compartilhou o relatório de {candidate} na entrevista “{title}”.",
            (
                "Ele está anexado como um PDF de uma página: a nota geral, a pontuação de cada "
                "tópico e o que o navegador do candidato registrou. Responda a este e-mail para "
                "falar com {sender}."
            ),
        ],
        "button": "Acessar a prepza",
        "footer": "Este e-mail foi enviado para {email} porque {sender} compartilhou um relatório "
        "de candidato com este endereço na prepza. Se você não esperava por ele, pode ignorá-lo.",
    },
    "candidates": {
        "subject": "Relatório de todos os candidatos: {title}",
        "preheader": "Todos os candidatos de “{title}” na {company}. O relatório está anexado.",
        "heading": "Relatório de candidatos",
        "lines": [
            "{sender}, da {company}, compartilhou o relatório de todos os candidatos da entrevista “{title}”.",
            (
                "Ele está anexado como PDF: a nota, o progresso e o que o navegador de cada candidato "
                "registrou, dos melhores para os demais. Responda a este e-mail para falar com {sender}."
            ),
        ],
        "button": "Acessar a prepza",
        "footer": "Este e-mail foi enviado para {email} porque {sender} compartilhou um relatório "
        "de candidatos com este endereço na prepza. Se você não esperava por ele, pode ignorá-lo.",
    },
    "footer": "Este e-mail foi enviado para {email} porque alguém convidou este endereço no "
    "prepza. Se você não esperava por ele, pode ignorá-lo.",
    "paste_link": "Ou cole este link no seu navegador",
    # The footer's links: optional emails' unsubscribe and settings, and a candidate's own.
    "unsubscribe": "Cancelar inscrição",
    "email_settings": "Alterar suas configurações de e-mail",
    "stop_reminders": "Não me enviar lembretes desta entrevista",
    "stop_company": "Não me enviar e-mails de {company}",
}
