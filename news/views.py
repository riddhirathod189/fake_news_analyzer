from django.shortcuts import render
from django.http import HttpResponse
from .forms import NewsForm
from .ml_model import classify_article
from .nlp_utils import summarize_text, get_readability, analyze_sentiment
from .pdf_utils import generate_pdf
from .bert_utils import bert_classifier

def home(request):
    if request.method == 'POST':
        form = NewsForm(request.POST)
        if form.is_valid():
            article = form.cleaned_data['article']
            # BERT Prediction
            bert_result = bert_classifier.predict(article)
            classification = bert_result["label"]
            confidence = bert_result["confidence"]

            # classification = classify_article(article)
            
            # Your existing NLP functions
            summary = summarize_text(article)
            readability = get_readability(article)
            sentiment = analyze_sentiment(article)

            context = {
                'article': article,
                'classification': classification,
                'summary': summary,
                "confidence": confidence,
                'readability': readability,
                'sentiment': sentiment,
                'form': form,
            }

            # Save result to session for PDF
            request.session['report_data'] = {
                "Original Article": article,
                "Classification": classification,
                "Summary": summary,
                "Confidence": confidence,
                "Readability (Flesch Score)": readability,
                "Sentiment": sentiment,
            }
            return render(request, 'news/result.html', context)
    else:
        form = NewsForm()
    return render(request, 'news/home.html', {'form': form})

def download_pdf(request):
    report_data = request.session.get('report_data', {})
    buf = generate_pdf(report_data)
    response = HttpResponse(buf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    return response
