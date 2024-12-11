document.addEventListener('DOMContentLoaded', function() {
    // Add generate summary button after the content field
    const contentField = document.getElementById('content_richtext_field');
    const summaryField = document.getElementById('summary_richtext_field');
    if (contentField) {
        const button = document.createElement('button');
        button.type = 'button';
        button.id = 'generate-summary-btn';
        button.className = 'generate-summary-btn';
        button.textContent = 'Generate Summary';
        button.style.height = 'min-content';

        const statusSpan = document.createElement('span');
        statusSpan.className = 'summary-status';
        statusSpan.id = 'summary-status';

        summaryField.parentNode.insertBefore(button, summaryField.nextSibling);
        button.parentNode.insertBefore(statusSpan, button.nextSibling);

        // Add click event listener to the button
        button.addEventListener('click', function() {
            const editor = tinymce.get('content_richtext_field');
            const summaryEditor = tinymce.get('summary_richtext_field');
            
            if (editor && summaryEditor) {
                const content = editor.getContent();
                if (!content.trim()) {
                    alert('Please enter some content before generating a summary.');
                    return;
                }

                // Disable both editors and the button
                editor.setMode('readonly');
                summaryEditor.setMode('readonly');
                button.disabled = true;
                statusSpan.textContent = ' Generating summary...';

                // Call the GPT API
                generateSummary(content)
                    .then(() => {
                        statusSpan.textContent = ' Summary generated successfully!';
                    })
                    .catch(error => {
                        console.error('Error generating summary:', error);
                        statusSpan.textContent = ' Error generating summary. Please try again.';
                    })
                    .finally(() => {
                        // Re-enable both editors and the button
                        editor.setMode('design');
                        summaryEditor.setMode('design');
                        button.disabled = false;
                    });
            }
        });
    }
});

async function generateSummary(content) {
    try {
        const response = await fetch('/admin/research/article/generate-summary/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: 'content=' + encodeURIComponent(content)
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        
        // Update the summary field
        if (typeof tinymce !== 'undefined') {
            const summaryEditor = tinymce.get('summary_richtext_field');
            if (summaryEditor) {
                summaryEditor.setContent(data.summary);
            }
        }
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
} 