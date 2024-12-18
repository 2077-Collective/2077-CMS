document.addEventListener('DOMContentLoaded', function() {
    // Wait for TinyMCE to initialize
    if (typeof tinymce !== 'undefined') {
        const gptSummaryContainer = document.getElementById('gpt_summary_richtext_field');
        if (gptSummaryContainer) {
            const buttonContainer = document.createElement('div');
            buttonContainer.id = 'generate-summary-container-btn';

            const button = document.createElement('button');
            button.type = 'button';
            button.id = 'generate-summary-btn';
            button.className = 'generate-summary-btn';
            button.textContent = 'Generate Summary';

            const statusSpan = document.createElement('p');
            statusSpan.className = 'summary-status';
            statusSpan.id = 'summary-status';

            buttonContainer.appendChild(button);
            buttonContainer.appendChild(statusSpan);

            gptSummaryContainer.parentNode.insertBefore(buttonContainer, gptSummaryContainer.nextSibling);
            button.parentNode.insertBefore(statusSpan, button.nextSibling);

            button.addEventListener('click', function() {
                const contentEditor = tinymce.get('content_richtext_field');
                const gptSummaryContainer = document.getElementById('gpt_summary_richtext_field');
                statusSpan.textContent = ' Generating summary...';
                
                if (contentEditor && gptSummaryContainer) {
                    const content = contentEditor.getContent();
                    if (!content.trim()) {
                        alert('Please enter some content before generating a summary.');
                        return;
                    }

                    // Call the GPT API
                    generateSummary(content)
                        .then(() => {
                            statusSpan.textContent = ' Summary generated successfully!';
                        })
                        .catch(error => {
                            statusSpan.textContent = ' Error generating summary. Please try again.';
                        })
                        .finally(() => {
                            // Re-enable editors and button
                            contentEditor.setMode('design');
                            gptSummaryEditor.setMode('design');
                            button.disabled = false;
                        });
                }
            });
        }
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
            const summaryEditor = tinymce.get('gpt_summary_richtext_field');
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