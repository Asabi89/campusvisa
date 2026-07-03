# SaveAll (Standalone Downloader)

SaveAll is an isolated Django project for downloading social videos with:

- Preview first
- Individual download
- Bulk download
- Pinterest, TikTok, Facebook, YouTube support

## Run

```bash
cd download
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Open: `http://localhost:8000/`

Downloads are saved in: `download/downloads/`

