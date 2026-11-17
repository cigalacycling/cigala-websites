"""Contact form on Marine's WordPress site: Contact Form 7, form 349. Emails marine@vivifysports.com, reply-to the sender.
The contact page embeds it with [contact-form-7 id="349" html_class="form panel"] (tools/build_vivify_wp.py).
  python3 -I tools/vivify_contact_form.py
"""
import json, subprocess
F = 'https://basic-darkslategray-cod-55.hostingersite.com/wp-json/contact-form-7/v1/contact-forms/349'   # created 17 Nov; context=save is required or CF7 only dry-runs
form = ('<span class="eyebrow" style="margin:0">Send a message</span>\n'
        '<div class="two"><div><label for="f-n">Name</label>[text* your-name id:f-n autocomplete:name]</div>'
        '<div><label for="f-e">Email</label>[email* your-email id:f-e autocomplete:email]</div></div>\n'
        '<div><label for="f-s">I\'m interested in</label>[select your-service id:f-s "Nutrition coaching" "Fuelling plan" "Workshops & talks" "Yoga" "E-book" "Something else"]</div>\n'
        '<div><label for="f-m">Message</label>[textarea* your-message id:f-m placeholder "Your sport, your goals and any upcoming events"]</div>\n'
        '[submit class:btn class:btn-primary "Send message"]')
mail = {'active': True, 'recipient': 'marine@vivifysports.com', 'sender': '[_site_title] <wordpress@[_site_domain]>',
        'subject': 'Website enquiry: [your-service] from [your-name]',
        'body': 'From: [your-name] <[your-email]>\nInterested in: [your-service]\n\n[your-message]\n\n--\nSent from the contact form on [_site_url]',
        'additional_headers': 'Reply-To: [your-email]', 'attachments': '', 'use_html': False, 'exclude_blank': False}
body = {'title': 'Contact', 'locale': 'en_GB', 'form': form, 'mail': mail,
        'messages': {'mail_sent_ok': 'Thank you! Marine will get back to you soon.'}}
# CF7's REST update ignores a JSON body here; send the same fields form-encoded
args = ['curl', '-sS', '-X', 'POST', F, '--data-urlencode', 'context=save', '--data-urlencode', 'title=Contact', '--data-urlencode', 'locale=en_GB', '--data-urlencode', 'form=' + form]
for k, v in mail.items():
    args += ['--data-urlencode', f'mail[{k}]=' + (('1' if v else '') if isinstance(v, bool) else v)]
args += ['--data-urlencode', 'messages[mail_sent_ok]=Thank you! Marine will get back to you soon.']
out = subprocess.run(args, capture_output=True, text=True).stdout
d = json.loads(out); print(d.get('id'), d.get('title'), d.get('properties', {}).get('mail', {}).get('recipient'), repr(d.get('properties', {}).get('form', {}).get('content', ''))[:80], d.get('code'), d.get('message'))
