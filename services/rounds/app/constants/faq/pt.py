# The FAQ in pt; the {placeholders} are filled in by helpers/help.py (faq_values) with
# billing's prices and the number of languages. Questions not translated yet show in English
# (constants/faq/__init__.py).
FAQ = [
    {
        "key": "what",
        "question": "O que é o prepza?",
        "answer": "Uma entrevista cronometrada criada a partir da sua descrição de vaga, para qualquer função. Use-a para fazer a triagem de candidatos antes de conhecê-los ou como uma etapa da própria contratação: de qualquer forma, você vê quem realmente conhece o trabalho.",
    },
    {
        "key": "roles",
        "question": "Para quais funções posso contratar?",
        "answer": "Qualquer função em que o conhecimento importa: suporte, vendas, finanças, saúde, ofícios técnicos, engenharia, marketing e muito mais. Se você consegue descrever o trabalho, o prepza consegue criar uma entrevista para ele.",
    },
    {
        "key": "hiring",
        "question": "Como funciona?",
        "answer": "Cole uma descrição de vaga na página inicial, informe o nome da sua empresa e confira os tópicos que o prepza propõe. Depois, convide candidatos: digite os e-mails, cole uma lista ou envie um arquivo. Candidatos que não começaram depois de alguns dias recebem um lembrete. Cada candidato recebe suas próprias questões, com um cronômetro em cada uma, e você vê a pontuação e todas as respostas assim que ele termina.",
    },
    {
        "key": "link",
        "question": "Posso colocar uma entrevista em um anúncio de vaga?",
        "answer": "Sim. Ative o link compartilhável da entrevista na aba de candidatos e cole-o no seu anúncio. Quem o abre entra na conta e faz a entrevista, e cada pessoa é cobrada como um candidato convidado. O link é desativado quando você marca a entrevista como contratado.",
    },
    {
        "key": "preview",
        "question": "Posso experimentar uma entrevista antes de convidar alguém?",
        "answer": "Sim. Abra sua entrevista como candidato na página dela, sem custo: as prévias não aparecem entre seus candidatos nem nas estatísticas das questões. Você também pode fazer qualquer uma das entrevistas de prática gratuitas.",
    },
    {
        "key": "cheating",
        "question": "Os candidatos podem usar IA ou procurar as respostas?",
        "answer": "Cada candidato recebe suas próprias questões aleatórias, em sua própria ordem, com um cronômetro em cada questão controlado pelo nosso servidor, então sobra pouco tempo para procurar respostas ou perguntar a uma IA. Os resultados também mostram quando um candidato saiu da página, copiou texto ou respondeu rápido demais para ter lido a questão.",
    },
    {
        "key": "cost",
        "question": "Quanto custa?",
        "answer": "Gerar entrevistas é grátis. Cada candidato que responde pelo menos uma questão custa {candidate} créditos (US$ {candidate_dollars}), e menos com créditos de recargas maiores, até US$ 1. Sua primeira empresa recebe {company} créditos grátis, o suficiente para os primeiros {company_candidates} candidatos. A página de preços lista todos os valores.",
    },
    {
        "key": "charged",
        "question": "Quando um candidato é cobrado?",
        "answer": "Só quando ele termina a entrevista tendo respondido pelo menos uma questão. Os créditos dele são reservados quando você o convida e voltam se você revogar o convite, se ele nunca começar ou se não responder nada.",
    },
    {
        "key": "compare_hiring",
        "question": "Como o preço se compara a outras ferramentas de avaliação?",
        "answer": "Muitas ferramentas de avaliação são vendidas como assinatura mensal ou anual, paga mesmo que você não avalie ninguém. No prepza você paga só por candidato: {candidate} créditos (US$ {candidate_dollars}), sem contrato, sem taxa por usuário e sem pagar para gerar uma entrevista. Uma empresa que convida {example_candidates} candidatos por mês paga cerca de US$ {example_year_dollars} por ano. Se você avalia muitos candidatos todo mês, uma assinatura pode custar menos, então compare com os seus números.",
    },
    {
        "key": "expire",
        "question": "Os créditos expiram?",
        "answer": "Não. Os créditos nunca expiram, e não há assinaturas nem renovações.",
    },
    {
        "key": "refunds",
        "question": "Posso pedir reembolso?",
        "answer": "Sim, dos créditos que você comprou nos últimos 14 dias e ainda não gastou: pelo Paddle ou escrevendo para nós. Créditos grátis, como o presente de boas-vindas, não são reembolsados. Os termos têm os detalhes.",
    },
    {
        "key": "scorecards",
        "question": "O que os resultados dos candidatos mostram?",
        "answer": "Cada resposta, se estava certa e quanto tempo levou. As notas aparecem em verde ou vermelho de acordo com a nota de aprovação que você definiu para a entrevista. Os resultados também sinalizam respostas rápidas demais para a questão ter sido lida, as vezes que o candidato saiu da página e tentativas de cópia.",
    },
    {
        "key": "reports",
        "question": "Posso compartilhar os resultados com um gestor de contratação?",
        "answer": "Sim. Baixe um relatório em PDF de um candidato ou de todos os candidatos de uma entrevista, envie-o por e-mail direto do prepza ou mande um resumo curto pelo WhatsApp ou Telegram.",
    },
    {
        "key": "candidates",
        "question": "O que os candidatos veem?",
        "answer": "O nome e o logotipo da sua empresa, o que esperar antes de começar e depois uma questão cronometrada por vez. Eles nunca veem sua pontuação nem se uma resposta estava certa.",
    },
    {
        "key": "verified",
        "question": "O que significa o selo de verificação?",
        "answer": "Que um dono ou administrador da empresa entrou com um e-mail corporativo do site da empresa, como you@acme.com, e que depois a nossa equipe analisou a empresa. Adicione o site em Verificar, no cabeçalho da sua empresa; serviços de e-mail gratuitos não contam. Enquanto a análise está pendente, sua equipe vê um relógio ao lado do nome, e mudar o nome da empresa a envia para análise de novo. O selo aparece ao lado do nome da sua empresa, inclusive nos convites.",
    },
    {
        "key": "languages",
        "question": "Quais idiomas são suportados?",
        "answer": "{count} idiomas, para o site, as entrevistas e os e-mails. Escolha o idioma em que uma entrevista é escrita, seja qual for o idioma da descrição da vaga.",
    },
    {
        "key": "privacy",
        "question": "O que acontece com as descrições de vaga e as respostas?",
        "answer": "As descrições de vaga são usadas para criar suas entrevistas, e as respostas dos candidatos para avaliá-las, apenas para a sua empresa. A política de privacidade explica o que guardamos, por quanto tempo e os direitos de cada pessoa.",
    },
    {
        "key": "delete",
        "question": "Posso excluir minha conta?",
        "answer": "Sim, nas Configurações. Sua conta e seus dados são excluídos, e antes você pode baixar uma cópia dos seus dados.",
    },
]
