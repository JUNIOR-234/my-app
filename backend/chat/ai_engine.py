{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "text": text[:200], # Clamp parameter constraint limit to save free tier allocation bytes
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            # Create a static media folder if it doesn't exist
            audio_dir = os.path.join(settings.BASE_DIR, 'static', 'audio')
            os.makedirs(audio_dir, exist_ok=True)
            
            audio_file = os.path.join(audio_dir, 'latest_voice.mp3')
            with open(audio_file, 'wb') as f:
                f.write(response.content)
                
            # Returns the web accessible absolute url parameter mapping to your server root
            return "/static/audio/latest_voice.mp3"
        else:
            print(f"🔴 ElevenLabs returned status code: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"🔴 Voice synthesis network pipeline failure: {e}")
        
    return None
