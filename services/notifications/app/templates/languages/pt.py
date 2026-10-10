# Email texts in Portuguese. Values are filled in with str.format; the HTML version escapes them.

# The footer of reminders to a company's owners and admins.
MEMBER_FOOTER = (
    "Este e-mail foi enviado para {email} porque você é proprietário ou administrador de "
    "uma empresa no prepza."
)

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
    "member": {
        "subject": "{inviter} convida você para a equipe de {company} na prepza",
        "preheader": (
            "Faça parte da equipe de {company} como {role}. Entre com {email} para aceitar."
        ),
        "heading": "Convite para a equipe",
        "lines": [
            "{inviter} convida você para fazer parte da equipe de {company} na prepza como {role}.",
            "Entre com {email} para aceitar. Só este endereço pode aceitar o convite.",
        ],
        "button": "Abrir o convite",
        # The role's name as the lines use it.
        "roles": {"admin": "administrador", "viewer": "visualizador"},
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
    "digest": {
        "subject": "Seu resumo de atividades no prepza",
        "preheader": "O que aconteceu nas suas empresas nas últimas 24 horas.",
        "heading": "Seu resumo de atividades",
        "lines": [
            "Veja o que aconteceu nas suas empresas no prepza nas últimas 24 horas.",
        ],
        "rows": {
            "candidate_finished": "Candidatos que concluíram: {count} · “{title}”",
            "invite_undelivered": "Convites não entregues: {count} · “{title}”",
            "ats_not_invited": "Candidatos do ATS não convidados: {count}",
            "interview_ready": "Entrevista pronta: “{title}”",
        },
        "button": "Abrir o prepza",
        "footer": (
            "Este e-mail foi enviado para {email} porque você é membro de uma empresa no "
            "prepza e recebe o resumo de atividades dela."
        ),
    },
    "low_credits": {
        "subject": "Seus créditos estão acabando",
        "preheader": "Recarregue para continuar convidando candidatos.",
        "heading": "Os créditos estão acabando",
        "lines": [
            (
                "Estas empresas não têm créditos suficientes para convidar outro candidato."
                " Recarregue para continuar convidando candidatos."
            ),
        ],
        "rows": {
            "company": "{company} · créditos disponíveis: {available}",
        },
        "button": "Recarregar",
        "footer": MEMBER_FOOTER,
    },
    "no_candidates": {
        "subject": "Aguardando candidatos",
        "preheader": "Convide candidatos por e-mail ou compartilhe o link da entrevista.",
        "heading": "Aguardando candidatos",
        "lines": [
            (
                "Estas entrevistas estão prontas há alguns dias, mas ninguém foi convidado "
                "ainda. Convide candidatos por e-mail ou compartilhe o link da entrevista."
            ),
        ],
        "rows": {
            "interview": "“{title}” · {company}",
        },
        "button": "Convidar candidatos",
        "footer": MEMBER_FOOTER,
    },
    "review_waiting": {
        "subject": "Seus tópicos estão aguardando revisão",
        "preheader": "Confirme os tópicos e as perguntas serão geradas.",
        "heading": "Revise seus tópicos",
        "lines": [
            (
                "Os tópicos das entrevistas que você iniciou estão aguardando sua revisão. "
                "Assim que você os confirmar, as perguntas serão geradas. Uma revisão "
                "deixada aberta por 14 dias é cancelada."
            ),
        ],
        "rows": {
            "interview": "{company} · dias aguardando: {days}",
        },
        "button": "Revisar os tópicos",
        "footer": MEMBER_FOOTER,
    },
    "top_up_failed": {
        "subject": "A recarga automática de {company} falhou",
        "preheader": (
            "Não foi possível cobrar o cartão. Recarregue para continuar convidando candidatos."
        ),
        "heading": "A recarga automática falhou",
        "lines": [
            (
                "A recarga automática não conseguiu cobrar o cartão de {company}, então "
                "nenhum crédito foi adicionado."
            ),
            (
                "Recarregue para continuar convidando candidatos. A recarga automática "
                "tentará cobrar o cartão de novo mais tarde."
            ),
        ],
        "button": "Recarregar",
        "footer": (
            "Este e-mail foi enviado para {email} porque você é proprietário ou "
            "administrador de {company} no prepza. Ele trata do faturamento da sua empresa,"
            " por isso é enviado independentemente das suas configurações de e-mail."
        ),
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
