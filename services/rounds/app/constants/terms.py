from app.constants.legal import COMPANY

# The terms of use, in English only: it's a legal text, and a translation would need its own
# legal review. The FAQ page's chat answers from it too.
TERMS_INTRO = f"These terms apply when you use prepza, a service of {COMPANY['name']} (registry code {COMPANY['registry_code']}), {COMPANY['address']}. By signing in, you agree to them."

TERMS_SECTIONS = [
    {
        "heading": "Your account",
        "paragraphs": [
            "You sign in with Google and are responsible for what happens in your account. You can delete it at any time in Settings.",
        ],
    },
    {
        "heading": "The service and its limits",
        "items": [
            "Questions, answers and tutor replies are written by AI and can be wrong. We check and improve them continuously, but don't rely on them as professional advice.",
            "A prepza certificate shows that you answered every question of a topic on prepza with the required score. It is not an accredited qualification.",
        ],
    },
    {
        "heading": "Your content",
        "paragraphs": [
            "You keep the rights to what you paste and create. You let us store and process it to run prepza, including sending it to our AI provider. When you make a preparation public, anyone can see and practise with it, and its proven questions may help write new preparations.",
            "Don't paste anything you aren't allowed to share, such as someone else's confidential information.",
        ],
    },
    {
        "heading": "Fair use",
        "items": [
            "Don't use prepza to send unwanted email, to scrape it, or to overload or attack it.",
            "Don't try to get around limits, security or another user's access.",
            "In an interview, answer on your own and follow the interview's rules; the company sees how long each answer took and when you left the page.",
        ],
    },
    {
        "heading": "Companies",
        "paragraphs": [
            "A company using prepza for interviews is responsible for inviting candidates lawfully, for telling them how their results are used, and for its hiring decisions. We process candidates' data on the company's behalf; ask us for our data processing terms.",
        ],
    },
    {
        "heading": "Credits and payments",
        "items": [
            "prepza is paid with credits: 1 US dollar buys 100 credits, with a bonus on larger top-ups. What each thing costs in credits is on the pricing page and is shown before you use it.",
            "Top-ups are sold by Paddle, who acts as the reseller (merchant of record): Paddle takes the payment, charges any VAT or sales tax, and issues the receipt or invoice.",
            "Your credits are for your own use on prepza. A company's credits belong to the company and are used for its candidates; any of its admins can top them up. Credits can't be transferred between accounts or companies, sold, or paid out as money.",
            "Automatic top-up is optional and off unless you turn it on. When you turn it on, you authorise Paddle to save your card and to charge it the top-up amount you chose each time the available balance falls under the level you chose, without asking again. Paddle emails a receipt for every charge. You can change or turn it off at any time on the top-up page, which also cancels the saved card's authorisation; charges already made follow the refund rules below.",
            "Credits don't expire. Deleting your account or a company deletes its credits.",
            "Referrals: when someone who signs up through your link, or a company created through your company's link, first tops up the amount shown on the pricing page, both of you get the referral credits shown there, for up to 25 referrals a year. Referring yourself or your own companies doesn't count, and we may withhold referral credits obtained by abuse.",
            "Some credits are free: the welcome credits, top-up bonuses, referral credits and similar gifts. They are given once, as described on the pricing page, and are never refunded or paid out. Free credits are used before paid ones.",
            "Credits are only charged for what works: a prep kit that fails or is cancelled, a candidate who never starts or answers nothing, or a tutor reply that fails costs nothing, and credits set aside for them come back.",
            "Refunds: you can ask for a refund of credits you bought in the last 14 days and haven't spent, through Paddle or by writing to us. Once you start using credits you bought, you agree that the service begins at once, and spent credits can't be refunded.",
            "If a payment is refunded or reversed by your bank, the credits it bought are removed. If they were already spent, your balance can go below zero, and credits can't be used until a top-up brings it back up.",
            "We may change prices in credits or the top-up amounts. Changes apply from when they are shown on the pricing page and never take away credits you already have.",
        ],
    },
    {
        "heading": "Availability and changes",
        "paragraphs": [
            "We work to keep prepza available and safe but can't promise it will always be. We may change or stop features, and may suspend accounts that break these terms. We will tell you about significant changes to these terms before they apply.",
        ],
    },
    {
        "heading": "Liability",
        "paragraphs": [
            "prepza is provided as it is. As far as the law allows, we are not liable for indirect losses, and our total liability is limited to what you paid for credits in the last 12 months, or 100 US dollars if you paid nothing. Nothing here limits rights you have as a consumer under the law of your country.",
        ],
    },
    {
        "heading": "Law",
        "paragraphs": [
            f"Estonian law applies, without taking away the mandatory protections of the country you live in. Questions about these terms: {COMPANY['email']}.",
        ],
    },
]
