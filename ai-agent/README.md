# ObstaRace Race Day Briefing Agent

Jednostavan AI agent (Python + LangChain) razvijen za potrebe URIZ seminarskog rada
(zahtev #16). Tema je direktno vezana za glavni projekat: agent generiše **"Race Day
Briefing"** — kratak, strukturisan izveštaj za organizatora trke, na osnovu stvarnih
podataka o trci i vremenskoj prognozi.

## Šta radi

1. Korisnik unese ID trke preko komandne linije (`--race-id`).
2. Agent povlači stvarne podatke o toj trci direktno iz **RaceService PostgreSQL
   baze** (kapacitet, broj prijava po statusu plaćanja).
3. Agent povlači vremensku prognozu za lokaciju i datum trke preko **Open-Meteo**
   API-ja (isti eksterni servis koji koristi i glavna ObstaRace aplikacija).
4. Ti podaci se šalju LLM modelu (OpenAI ili Ollama, po izboru) kroz strukturisan
   prompt koji definiše ulogu modela, zadatak, i tačan format izlaza.
5. Model generiše Markdown izveštaj sa četiri sekcije: **Summary**, **Capacity
   Status**, **Weather Advisory**, **Recommended Actions**.
6. Izveštaj se ispisuje u terminalu i čuva kao `.md` fajl.

## Arhitektura / struktura projekta

```
ai-agent/
├── main.py                   — ulazna tačka (CLI)
├── config.py                  — čita .env (LLM provajder, API ključevi, DB URL)
├── data/
│   └── race_data.py            — modul za rad sa podacima: SQL upiti nad race_db
├── weather/
│   └── weather_client.py       — drugi eksterni izvor podataka: Open-Meteo API
├── agent/
│   ├── prompts.py                — strukturisan prompt (uloga, zadatak, format izlaza)
│   └── briefing_agent.py         — AI logika: LangChain lanac (prompt | LLM | parser)
├── output/
│   └── formatter.py               — formatira i čuva strukturisan Markdown izlaz
├── requirements.txt
├── .env.example
└── README.md
```

Ovo zadovoljava zahtev za modularnost: `main.py` je jedina ulazna tačka, `data/` je
zaseban modul za podatke, `agent/` je zaseban modul za AI logiku.

## Eksterni podaci koje agent koristi

- **RaceService PostgreSQL baza** (`race_db`) — ista baza koju koristi glavni
  ObstaRace projekat; agent čita stvarne, već postojeće podatke o trkama i
  prijavama, ne sintetičke primere.
- **Open-Meteo API** (geocoding + forecast) — isti eksterni servis integrisan i u
  glavnoj aplikaciji (RaceService), ovde korišćen kao samostalan, sinhron klijent.

## Napredna obrada podataka

- Agregacija broja prijava po statusu plaćanja (SQL `GROUP BY`) pre slanja modelu.
- Izračunavanje procenta popunjenosti kapaciteta (`capacity_utilization_percent`).
- Pretvaranje sirovih vremenskih kodova (WMO weather code) u čitljiv opis pre
  ubacivanja u prompt.

## Podrška za više LLM provajdera

Provajder se bira preko `.env` promenljive `LLM_PROVIDER`:

- `LLM_PROVIDER=openai` — koristi OpenAI (`langchain-openai`), potreban je
  `OPENAI_API_KEY`.
- `LLM_PROVIDER=ollama` — koristi lokalno pokrenut Ollama server
  (`langchain-ollama`), ne zahteva API ključ, ali zahteva instaliran Ollama i
  preuzet model (`ollama pull llama3.2`).

## Obrada grešaka

Aplikacija hvata i jasno prijavljuje (bez pada, exit kod 1):

- Nepostojeći ID trke (`RaceNotFoundError`).
- Nedostupnu bazu podataka.
- Nedostupnu ili van-opsega vremensku prognozu (agent nastavlja dalje sa porukom
  "Not available", ne prekida rad).
- Nepodržan LLM provajder u `.env`.
- Greške LLM poziva (npr. netačan API ključ, Ollama server nije pokrenut, timeout).

## Instalacija i pokretanje

```bash
cd ai-agent
python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash) / .venv\Scripts\activate.bat (cmd)
pip install -r requirements.txt

cp .env.example .env
# upiši svoj OPENAI_API_KEY (ili podesi LLM_PROVIDER=ollama)
```

**Preduslov za podatke:** glavni ObstaRace `docker compose` stack mora biti
pokrenut (bar `race-db` servis), pošto agent čita stvarne podatke odatle:

```bash
cd ..
docker compose up -d race-db
```

**Pokretanje agenta:**

```bash
cd ai-agent
python main.py --race-id 3
```

## Primer korišćenja (stvarno testirano)

Podaci ispod su stvarno povučeni iz baze i sa Open-Meteo API-ja tokom razvoja
(LLM poziv nije izvršen jer zahteva pravi API ključ koji nije deo repozitorijuma):

```
$ python main.py --race-id 3

# race podaci povučeni iz race_db:
name=Weather Test Race, location=Belgrade, max_participants=10,
completed=0, pending=0, failed=0, capacity_utilization_percent=0.0

# vremenska prognoza povučena sa Open-Meteo:
Overcast, 21.1-31.0C, 6% chance of precipitation

# (LLM generiše Markdown briefing na osnovu ovih podataka i čuva ga u
#  output/reports/race-3-Weather-Test-Race-<timestamp>.md)
```

Očekivan format LLM izlaza (struktura, ne pravi model output):

```markdown
## Summary
Weather Test Race in Belgrade currently has 0 confirmed registrations out of a
10-person capacity.

## Capacity Status
No capacity risk — 0% utilization.

## Weather Advisory
Overcast conditions, 21-31C, low (6%) chance of precipitation. No weather risk.

## Recommended Actions
- Promote the race to increase registrations, as capacity is currently unused.
- Monitor registrations as the date approaches.
```

## Napomena o testiranju

Modul za podatke (`data/race_data.py`) i vremenski klijent (`weather/weather_client.py`)
su testirani uživo protiv stvarne baze i stvarnog Open-Meteo API-ja. Sam LLM poziv
(OpenAI/Ollama) zahteva pravi API ključ odnosno lokalno pokrenut Ollama server, koji
nisu deo ovog repozitorijuma — potrebno je popuniti `.env` pravim vrednostima pre
demonstracije na odbrani.
