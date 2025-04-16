from django.shortcuts import render, redirect
from django.http import FileResponse
from pytube import YouTube
from io import BytesIO
import re

def validate_url(url):
    regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    return re.match(regex, url)

def get_video_stream(url):
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(
            progressive=True,
            file_extension='mp4'
        ).order_by('resolution').desc().first()
        
        if not stream:
            stream = yt.streams.get_highest_resolution()
            
        return stream, yt.title
    except Exception as e:
        raise Exception(f"Error fetching video: {str(e)}")

def home(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        if not validate_url(url):
            return render(request, 'core/error.html', {'error': 'Invalid YouTube URL'})
        
        try:
            buffer = BytesIO()
            stream, title = get_video_stream(url)
            stream.stream_to_buffer(buffer)
            buffer.seek(0)
            
            response = FileResponse(buffer, content_type='video/mp4')
            response['Content-Disposition'] = f'attachment; filename="{title[:50]}.mp4"'
            return response
        except Exception as e:
            return render(request, 'core/error.html', {'error': str(e)})
    
    return render(request, 'core/index.html')

def error_handler(request, exception=None):
    return render(request, 'core/error.html', status=500)