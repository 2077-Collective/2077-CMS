from django.utils.html import format_html, escape
from django.utils.safestring import mark_safe

def get_slug_history_table(histories):
    """Return the HTML table for the slug history."""
    html = []
    html.append('<table class="slug-history-table" role="grid">')
    html.append('<caption class="sr-only">Slug History Table</caption>')
    html.append('<thead><tr>') 
    html.append('<th scope="col">Old Slug</th>')
    html.append('<th scope="col">Changed At</th>')
    html.append('</tr>')
    html.append('</thead><tbody>')
    for history in histories:
        html.append('<tr>')
        html.append(f'<td>{escape(history.old_slug)}</td>')
        html.append(f'<td>{history.created_at}</td>')
        html.append('</tr>')
    html.append('</tbody>')
    html.append('</table>')
    return mark_safe(''.join(html))

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