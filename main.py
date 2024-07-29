from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import os
import shikisai
import requests
from flask_caching import Cache

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

UPLOAD_FOLDER = "C:\\Users\\User\\Documents\\GitHub\\emotabi\\web\\uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Google Maps APIキーをここに追加
GOOGLE_MAPS_API_KEY = 'AIzaSyD89WBZRW7eZL92PMwhah1FLcJcjFE9JOk'

@cache.memoize(timeout=300)  # キャッシュのタイムアウトを5分に設定
def search_google_maps(region, purpose, emotion_words):
    search_query = f"{region} {purpose} {' '.join(emotion_words)}"
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={search_query}&language=ja&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    results = response.json().get('results', [])
    top_three_results = results[:3]

    for place in top_three_results:
        place_id = place['place_id']
        place_details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&language=ja&key={GOOGLE_MAPS_API_KEY}"
        place_details_response = requests.get(place_details_url)
        place_details = place_details_response.json().get('result', {})

        if 'photos' in place_details:
            photo_reference = place_details['photos'][0]['photo_reference']
            photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={GOOGLE_MAPS_API_KEY}"
            place['photo_url'] = photo_url
        else:
            place['photo_url'] = "https://via.placeholder.com/400"

        place['maps_url'] = place_details.get('url', '')

    return top_three_results

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        region = request.form['region']
        purpose = request.form['purpose']
        file = request.files['file']
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            emotions, pie_chart_filename = shikisai.process_image(filepath)
            search_results = search_google_maps(region, purpose, emotions)
            return render_template('result.html', 
                                   emotions=emotions, 
                                   image_url=url_for('uploaded_file', filename=pie_chart_filename), 
                                   search_results=search_results, 
                                   uploaded_image_url=url_for('uploaded_file', filename=filename),
                                   region=region,
                                   purpose=purpose)
    return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
