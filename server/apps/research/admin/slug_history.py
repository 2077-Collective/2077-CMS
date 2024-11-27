from django.utils.html import format_html

def get_slug_history_table(histories):
    """Return the HTML table for the slug history."""
    html = []
    html.append('<table style="width: 100%; border-collapse: collapse;">')
    html.append('<tr style="background-color: #f5f5f5;">')
    html.append('<th style="padding: 8px; border: 1px solid #ddd;">Old Slug</th>')
    html.append('<th style="padding: 8px; border: 1px solid #ddd;">Changed At</th>')
    html.append('</tr>')
    for history in histories:
        html.append('<tr>')
        html.append(f'<td style="padding: 8px; border: 1px solid #ddd;">{history.old_slug}</td>')
        html.append(f'<td style="padding: 8px; border: 1px solid #ddd;">{history.created_at}</td>')
        html.append('</tr>')
    html.append('</table>')
    return ''.join(html)

def get_slug_history_html(obj):
    """Return the HTML for the slug history."""
    histories = obj.slug_history.all().order_by('-created_at')
    if not histories:
        return "No slug changes recorded"
    html = ['<div class="slug-history">']
    html.append(get_slug_history_table(histories))
    html.append('</div>')
    return format_html(''.join(html))

def current_slug_history(obj):
    """Display the history of URL changes for the article."""
    return get_slug_history_html(obj)