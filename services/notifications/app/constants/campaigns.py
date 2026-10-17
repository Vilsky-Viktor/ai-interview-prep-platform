# Campaigns (the admin zone's Campaigns tab): product updates and offers to the users who chose
# them, sent through the bulk sender.

# A campaign made from a news post: its button's text and the page it opens.
NEWS_BUTTON = "Read the news"
NEWS_LINK = "/news#{news_id}"

# How many campaigns of each kind may go out a day is the CAMPAIGNS_PER_KIND_DAY limit.
ONE_A_DAY = (
    "Today's limit of campaigns of this kind ({limit}) is reached. Send the next one tomorrow."
)
ALREADY_SENT = "This campaign was already sent, so it can't be changed."
NOT_SENT = "This campaign hasn't been sent."
LINK_NOT_ON_SITE = "The button's link must be a page on prepza, starting with /."
NO_BUTTON_TEXT = "Give the button a text, or leave its link empty too."
