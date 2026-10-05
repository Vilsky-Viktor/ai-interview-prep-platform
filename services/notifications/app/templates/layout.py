# Layouts every email is rendered into. The HTML follows email-client rules: tables for layout,
# inline styles only, a 560px column, a hidden preview line, and a button that stays a plain link.

TEXT_LAYOUT = """\
{heading}.

{lines}

{button}: {link}

--
{footer}

prepza.
"""

# Who sent the invite, in the body: bold, so it stands out.
# The inviting company's logo, at the top of the card, when it has one.
HTML_LOGO = (
    '<img src="{url}" alt="{alt}" height="40" style="display:block;height:40px;width:auto;'
    'max-width:200px;margin:0 0 24px;border:0;">'
)
HTML_NAME = '<strong style="font-weight:600;color:#0a0a0a;">{name}</strong>'

HTML_PARAGRAPH = (
    '<p style="margin:0 0 16px;font-size:16px;line-height:24px;color:#404040;">{text}</p>'
)

# Pads the preview line, so clients don't fill the rest of it with the email's text.
PREHEADER_PADDING = "&#8199;&#65279;&#847; " * 40

HTML_LAYOUT = """\
<!doctype html>
<html lang="{language}" dir="{direction}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<meta name="supported-color-schemes" content="light">
<title>{subject}</title>
</head>
<body style="margin:0;padding:0;background-color:#f5f5f5;">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;mso-hide:all;">\
{preheader}{padding}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" \
style="background-color:#f5f5f5;">
<tr><td align="center" style="padding:40px 16px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" \
dir="{direction}" style="max-width:560px;text-align:{align};">
<tr><td dir="ltr" style="padding:0 8px 24px;font-family:Poppins,-apple-system,BlinkMacSystemFont,\
'Segoe UI',Helvetica,Arial,sans-serif;font-size:26px;line-height:32px;font-weight:600;\
letter-spacing:-0.5px;color:#0a0a0a;">prepza<span style="color:#0071e0;">.</span></td></tr>
<tr><td style="padding:40px 32px;background-color:#ffffff;border:1px solid #e5e5e5;\
border-radius:16px;text-align:{align};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,\
sans-serif;">
{logo}<h1 style="margin:0 0 24px;font-size:24px;line-height:32px;font-weight:600;color:#0a0a0a;">\
{heading}<span style="color:#0071e0;">.</span></h1>
{lines}
<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:8px 0 32px;">
<tr><td style="border-radius:10px;background-color:#0071e0;">\
<a href="{link}" target="_blank" style="display:inline-block;padding:14px 28px;\
font-size:16px;line-height:20px;font-weight:600;color:#ffffff;text-decoration:none;\
border-radius:10px;">{button}</a></td></tr>
</table>
<p style="margin:0;font-size:14px;line-height:20px;color:#737373;">\
{paste_link}:<br>\
<a href="{link}" target="_blank" style="color:#0071e0;word-break:break-all;">{link}</a></p>
</td></tr>
<tr><td style="padding:24px 8px 0;text-align:{align};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',\
Helvetica,Arial,sans-serif;font-size:13px;line-height:20px;color:#737373;">{footer}</td></tr>
</table>
</td></tr>
</table>
</body>
</html>
"""
