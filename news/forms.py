from django import forms

class NewsForm(forms.Form):
    article = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 12,
            'cols': 80,
            'class': 'form-control',
            'placeholder': 'Paste your news article content here...\n\nExample: Copy and paste the full text of a news article you want to verify. Include headlines, body text, and any relevant details for the most accurate analysis.',
            'id': 'article-input',
            'style': 'min-height: 300px; font-size: 1rem; line-height: 1.6;'
        }),
        required=True,
        label='News Article Content',
        help_text='Paste the complete news article text for the most accurate analysis results.'
    )