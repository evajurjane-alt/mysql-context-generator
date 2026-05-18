# MySQL konteksta ģenerators

Rīks kas izveido savienojumu ar MySQL serveri, izgūst datubāzes shēmu un izmanto Gemini AI lai atbildētu uz jautājumiem par datiem.

## Uzstādīšana

```bash
pip install -r requirements.txt
```

## Konfigurācija

Nokopē `.env.example` uz `.env` un aizpildi:

```
DB_HOST=87.110.123.151
DB_PORT=3306
DB_USER=fita
DB_PASSWORD=<parole>
DB_NAME=<datubāzes nosaukums>

GEMINI_API_KEY=<tavs gemini api key>
```

## Palaišana

```bash
python main.py
```

## Struktūra

```
├── main.py                  # Galvenais skripts
├── src/
│   ├── db_explorer.py       # MySQL shēmas izgūšana
│   ├── context_builder.py   # Konteksta veidošana
│   └── gemini_client.py     # Gemini API
├── .env                     # Privātie dati (nav GitHub!)
├── .env.example             # Piemērs
└── requirements.txt
```
