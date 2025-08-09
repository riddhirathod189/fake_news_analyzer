import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import NewsForm, ImageUploadForm
import pytesseract
from .ml_model import classify_article
from .nlp_utils import summarize_text, get_readability, analyze_sentiment
from .pdf_utils import generate_pdf
from PIL import Image
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

# Set Tesseract path if needed
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def ocr_upload(request):
    if request.method == 'POST' and request.FILES.get('image'):
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = form.cleaned_data['image']
            save_path = os.path.join(settings.MEDIA_ROOT, 'uploads', image_file.name)

            # Save the image
            with open(save_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)

            # Open image and run Tesseract OCR
            try:
                image = Image.open(save_path)
                extracted_text = pytesseract.image_to_string(image)
            except Exception as e:
                return render(request, 'news/home.html', {
                    'form': NewsForm(),
                    'ocr_error': f"OCR failed: {str(e)}"
                })

            # === BERT Prediction ===
            bert_result = bert_classifier.predict(extracted_text)
            classification = bert_result["label"]
            confidence = bert_result["confidence"]

            # === NLP Analysis ===
            summary = summarize_text(extracted_text)
            readability = get_readability(extracted_text)
            sentiment = analyze_sentiment(extracted_text)

            # === Context to render result page ===
            context = {
                'article': extracted_text,
                'classification': classification,
                'summary': summary,
                'confidence': confidence,
                'readability': readability,
                'sentiment': sentiment,
            }

            # === Save to session for PDF download ===
            request.session['report_data'] = {
                "Original Article": extracted_text,
                "Classification": classification,
                "Summary": summary,
                "Confidence": confidence,
                "Readability (Flesch Score)": readability,
                "Sentiment": sentiment,
            }

            return render(request, 'news/result.html', context)
    
    # If GET request or no image, show home page again
    return redirect('home')

# def ocr_upload_view(request):
#     text = None
#     image_url = None
#     if request.method == 'POST' and request.FILES.get('image'):
#         form = ImageUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             img = form.cleaned_data['image']
#             img_path = os.path.join(settings.MEDIA_ROOT, 'uploads', img.name)
#             with open(img_path, 'wb+') as destination:
#                 for chunk in img.chunks():
#                     destination.write(chunk)
#             image_url = os.path.join(settings.MEDIA_URL, 'uploads', img.name)
#             try:
#                 image = Image.open(img_path)
#                 text = pytesseract.image_to_string(image)
#             except Exception as e:
#                 text = f"OCR Error: {str(e)}"
#     else:
#         form = ImageUploadForm()
#     context = {'form': form, 'ocr_text': text, 'image_url': image_url}
#     return render(request, 'news/ocr_upload.html', context)
