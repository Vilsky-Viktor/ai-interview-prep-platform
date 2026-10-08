# The FAQ in fr; the {placeholders} are filled in by helpers/help.py (faq_values) with
# billing's prices and the number of languages. Questions not translated yet show in English
# (constants/faq/__init__.py).
FAQ = [
    {
        "key": "what",
        "question": "Qu'est-ce que prepza ?",
        "answer": "Un entretien chronométré créé à partir de votre fiche de poste, pour n'importe quel poste. Utilisez-le pour présélectionner les candidats avant de les rencontrer, ou comme une étape à part entière du recrutement : dans les deux cas, vous voyez qui maîtrise vraiment le poste.",
    },
    {
        "key": "roles",
        "question": "Pour quels postes puis-je recruter ?",
        "answer": "Tout poste où les connaissances comptent : support, vente, finance, santé, métiers manuels, ingénierie, marketing et plus encore. Si vous pouvez décrire le poste, prepza peut créer un entretien pour lui.",
    },
    {
        "key": "hiring",
        "question": "Comment ça marche ?",
        "answer": "Collez une fiche de poste sur la page d'accueil, indiquez le nom de votre entreprise et vérifiez les thèmes que propose prepza. Invitez ensuite des candidats : saisissez leurs e-mails, collez une liste ou importez un fichier. Les candidats qui n'ont pas commencé après quelques jours reçoivent un rappel. Chaque candidat reçoit ses propres questions, chacune chronométrée, et vous voyez son score et chaque réponse dès qu'il a terminé.",
    },
    {
        "key": "link",
        "question": "Puis-je mettre un entretien dans une offre d'emploi ?",
        "answer": "Oui. Activez le lien de partage de l'entretien dans son onglet Candidats et collez-le dans votre offre. Toute personne qui l'ouvre se connecte et passe l'entretien, et chacune est facturée comme un candidat invité. Le lien se désactive quand vous marquez l'entretien comme recruté.",
    },
    {
        "key": "preview",
        "question": "Puis-je essayer un entretien avant d'inviter qui que ce soit ?",
        "answer": "Oui. Ouvrez votre entretien en tant que candidat depuis sa page, gratuitement : les aperçus n'apparaissent ni parmi vos candidats ni dans les statistiques des questions. Vous pouvez aussi passer n'importe lequel des entretiens d'entraînement gratuits.",
    },
    {
        "key": "cheating",
        "question": "Les candidats peuvent-ils utiliser une IA ou chercher les réponses ?",
        "answer": "Chaque candidat reçoit ses propres questions aléatoires, dans son propre ordre, avec un minuteur sur chaque question contrôlé par notre serveur, il a donc peu de temps pour chercher les réponses ou demander à une IA. Les résultats montrent aussi quand un candidat a quitté la page, copié du texte ou répondu trop vite pour avoir lu la question.",
    },
    {
        "key": "cost",
        "question": "Combien ça coûte ?",
        "answer": "La génération d'entretiens est gratuite. Chaque candidat qui répond à au moins une question coûte {candidate} crédits ({candidate_dollars} $), et moins avec les crédits de recharges plus importantes, jusqu'à 1 $. Votre première entreprise reçoit {company} crédits gratuits, de quoi couvrir ses {company_candidates} premiers candidats. La page des tarifs indique tous les prix.",
    },
    {
        "key": "charged",
        "question": "Quand un candidat est-il facturé ?",
        "answer": "Seulement quand il termine l'entretien après avoir répondu à au moins une question. Ses crédits sont réservés quand vous l'invitez et vous reviennent si vous révoquez l'invitation, s'il ne commence jamais ou s'il ne répond à rien.",
    },
    {
        "key": "compare_hiring",
        "question": "Comment le prix se compare-t-il à celui d'autres outils d'évaluation ?",
        "answer": "Beaucoup d'outils d'évaluation sont vendus sous forme d'abonnement mensuel ou annuel, payé même si vous n'évaluez personne. Avec prepza, vous payez uniquement par candidat : {candidate} crédits ({candidate_dollars} $), sans contrat, sans frais par utilisateur et sans rien à payer pour générer un entretien. Une entreprise qui invite {example_candidates} candidats par mois paie environ {example_year_dollars} $ par an. Si vous évaluez beaucoup de candidats chaque mois, un abonnement peut coûter moins cher : comparez avec vos propres chiffres.",
    },
    {
        "key": "expire",
        "question": "Les crédits expirent-ils ?",
        "answer": "Non. Les crédits n'expirent jamais, et il n'y a ni abonnement ni renouvellement.",
    },
    {
        "key": "refunds",
        "question": "Puis-je être remboursé ?",
        "answer": "Oui, pour les crédits achetés au cours des 14 derniers jours et non dépensés : via Paddle ou en nous écrivant. Les crédits offerts, comme le cadeau de bienvenue, ne sont pas remboursés. Les conditions donnent les détails.",
    },
    {
        "key": "scorecards",
        "question": "Que montrent les fiches d'évaluation des candidats ?",
        "answer": "Chaque réponse, si elle était juste et le temps qu'elle a pris. Les notes s'affichent en vert ou en rouge par rapport au seuil de réussite que vous avez fixé pour l'entretien. Les fiches signalent aussi les réponses trop rapides pour avoir lu la question, les sorties de la page et les tentatives de copie.",
    },
    {
        "key": "reports",
        "question": "Puis-je partager les résultats avec un responsable du recrutement ?",
        "answer": "Oui. Téléchargez un rapport PDF pour un candidat ou pour tous les candidats d'un entretien, envoyez-le par e-mail directement depuis prepza, ou envoyez un court résumé sur WhatsApp, Telegram, Viber ou LINE.",
    },
    {
        "key": "integrations",
        "question": "prepza fonctionne-t-il avec mon ATS ou d'autres outils ?",
        "answer": "Oui, sans frais supplémentaires. Connectez Workable, Greenhouse, Teamtailor, Recruitee ou Breezy HR dans l'onglet Intégrations de votre entreprise : les candidats que vous déplacez vers une étape reçoivent l'entretien, et leurs résultats reviennent dans l'ATS. Slack peut publier les notifications de votre entreprise dans un canal, et l'API permet à votre propre plateforme d'inviter des candidats et de recevoir leurs résultats ; consultez la Documentation de l'API.",
    },
    {
        "key": "candidates",
        "question": "Que voient les candidats ?",
        "answer": "Le nom et le logo de votre entreprise, ce qui les attend avant de commencer, puis une question chronométrée à la fois. Ils ne voient jamais leur score ni si une réponse était juste.",
    },
    {
        "key": "verified",
        "question": "Que signifie la coche de vérification ?",
        "answer": "Qu'un propriétaire ou un administrateur de l'entreprise s'est connecté avec un e-mail professionnel sur le site de l'entreprise, comme vous@acme.com, puis que notre équipe a examiné l'entreprise. Ajoutez le site avec Vérifier dans l'en-tête de votre entreprise ; les services d'e-mail gratuits ne comptent pas. Tant que l'examen est en attente, votre équipe voit une horloge à côté du nom, et renommer l'entreprise la renvoie en examen. La coche s'affiche à côté du nom de votre entreprise, y compris dans les invitations.",
    },
    {
        "key": "languages",
        "question": "Quelles langues sont prises en charge ?",
        "answer": "{count} langues, pour le site, les entretiens et les e-mails. Choisissez la langue dans laquelle un entretien est rédigé, quelle que soit la langue de la fiche de poste.",
    },
    {
        "key": "privacy",
        "question": "Que deviennent les fiches de poste et les réponses ?",
        "answer": "Les fiches de poste servent à créer vos entretiens, et les réponses des candidats à les noter, uniquement pour votre entreprise. La politique de confidentialité explique ce que nous conservons, pendant combien de temps, et les droits de chacun.",
    },
    {
        "key": "delete",
        "question": "Puis-je supprimer mon compte ?",
        "answer": "Oui, dans les Paramètres. Votre compte et vos données sont supprimés, et vous pouvez d'abord télécharger une copie de vos données.",
    },
]
