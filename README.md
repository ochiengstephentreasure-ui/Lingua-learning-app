# Lingua — Full Language Learning App

Lingua is a Flask-powered language-learning and translation app with a mobile-app-style interface.

## Learning system
- Structured CEFR-style course paths: A1, A2, B1 and B2.
- Starter curricula for Spanish, French, Kiswahili, German and Italian.
- Bite-sized units with phrase teaching and quick checks.
- Vocabulary decks with spaced-review scheduling.
- Again / Hard / Good / Easy review actions.
- Daily learning goals: 10, 15, 20 or 30 minutes.
- XP, levels, streaks, activity history and vocabulary mastery.
- Speaking studio using browser speech recognition when supported.
- Pronunciation score is a speech-to-text similarity estimate, not a phoneme-level accent assessment.
- Pronunciation engine: optional bundled/licensed course recordings first, then the best matching browser TTS voice, with a clear fallback message.
- Translation can feed directly into vocabulary and speaking practice.
- Dark mode and PWA install groundwork.

## Run
```bash
python -m pip install -r requirements.txt
python app.py
```
Then open `http://127.0.0.1:5000`.

For Render/production, use `gunicorn app:app` as the Start Command.

## Translation provider
Set `TRANSLATION_API_URL` to a compatible translation POST endpoint. Optionally set `TRANSLATION_API_KEY`. The browser never receives the key.

## AI helper
The existing Flask `/assist` endpoint remains available. Configure `AI_API_URL` on the server to connect an AI provider.

## Data
Learning progress, vocabulary, settings and activity are stored locally in the browser using localStorage. No account or database is required for the learning system.

## Expanded language support
The translation backend accepts the expanded language list from the earlier Lingua version, while the built-in course curriculum currently focuses on Spanish, French, Kiswahili, German and Italian.

## Pronunciation audio
The V4 engine is ready for licensed course recordings. Add recordings under `audio/<language>/...` and register their paths in the `COURSE_AUDIO` map in `index.html`. If no recording exists, Lingua automatically falls back to browser TTS. No copyrighted recordings are bundled.

## Course progression
A1 is available immediately. A2 unlocks at 80% A1 mastery, B1 at 80% A2 mastery, and B2 at 80% B1 mastery. The learner can also choose an exact unit and phrase from the “Choose where to start” selector.

## PWA
Serve Lingua over HTTPS when deploying publicly so browsers can offer installation as an app.


## V4.4 pronunciation reliability
The browser TTS engine now waits for asynchronous voice loading, listens for `voiceschanged`, retries without a selected voice when needed, reports the actual browser error, and includes a timeout so the UI cannot remain stuck.


## V4.4 audio engine
The pronunciation system now exposes detected voices, automatically ranks Natural/Online and Microsoft voices, allows manual voice selection, and provides an explicit browser fallback test. Licensed course recordings remain optional and are never copied from third-party copyrighted sources.
