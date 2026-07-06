# ObstaRace Race Day Briefing Agent

Jednostavan AI agent (Python + LangChain) razvijen za potrebe URIZ seminarskog rada
(zahtev #16). Tema je direktno vezana za glavni projekat: agent generiše **"Race Day
Briefing"** — kratak, strukturisan izveštaj za organizatora trke, na osnovu stvarnih
podataka o trci i vremenskoj prognozi.

## Šta radi

1. Agent pita korisnika za naziv trke (interaktivno, preko terminala). Ako trka sa
   tim nazivom ne postoji u bazi, ponovo traži unos dok se ne pronađe postojeća trka.
2. Agent povlači stvarne podatke o toj trci direktno iz **RaceService PostgreSQL
   baze** (kapacitet, broj prijava po statusu plaćanja).
3. Agent povlači vremensku prognozu za lokaciju i datum trke preko **Open-Meteo**
   API-ja (isti eksterni servis koji koristi i glavna ObstaRace aplikacija).
4. Ti podaci se šalju LLM modelu (OpenAI ili Ollama, po izboru) kroz strukturisan
   prompt koji definiše ulogu modela, zadatak, i tačan format izlaza.
5. Model generiše Markdown izveštaj sa četiri sekcije: **Summary**, **Capacity
   Status**, **Weather Advisory**, **Recommended Actions**.
6. Izveštaj se ispisuje u terminalu i čuva kao `.md` fajl.

Terminalski interfejs je stilizovan (naslovni banner, kratak pozdrav agenta, obojeni
prompt/status poruke) radi jasnije prezentacije uživo.

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

- Nepostojeći naziv trke (`RaceNotFoundError`) — korisnik se samo ponovo pita za naziv,
  aplikacija se ne prekida.
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
python main.py
```

Agent će prvo pitati: `Unesite naziv trke:` — ukuca se (deo) naziva postojeće trke
(npr. `Weather Test Race`), a ako takva trka ne postoji, agent ispiše listu postojećih
trka iz baze (kao podsetnik šta se može ukucati) i ponovo postavlja isto pitanje.

## Primer korišćenja (stvarno pokrenuto, pravi izlaz)

Ispod je stvaran, neizmenjen izlaz agenta, dobijen pokretanjem protiv stvarno
pokrenute `race_db` baze i lokalno instaliranog Ollama servera (model `llama3.2`,
`LLM_PROVIDER=ollama`) — uključujući pokušaj sa nepostojećim nazivom trke:

```
$ python main.py
==================================================
  ObstaRace — Race Day Briefing Agent
==================================================
Zdravo! Ja sam Race Day Briefing Agent, AI asistent za ObstaRace.
Pomažem organizatorima trka tako što na osnovu podataka o trci i
vremenskoj prognozi generišem kratak izveštaj pred sam dan trke.

> Unesite naziv trke: Nepostojeca Trka Xyz
Trka 'Nepostojeca Trka Xyz' nije pronađena.
Postojeće trke:
  - Beogradski maraton
  - Friendship Race
  - FON RACE
  - Umljanska trka
  - Summertime Vibes Race
  - TMNT Race
  - Weather Test Race
Pokušajte ponovo.

> Unesite naziv trke: Weather Test Race
✓ Pronađena trka: Weather Test Race (#3) — Belgrade

Generišem AI izveštaj...
--------------------------------------------------
## Summary
The Weather Test Race is scheduled for July 7th, 2026, at 10:00 AM in Belgrade.

## Capacity Status
No capacity concerns as the confirmed registration count (0 completed + 0 pending) is well below the maximum capacity of 10 participants.

## Weather Advisory
No weather risk indicators are present. Temperature conditions (21.2-31.0C) and precipitation probability (2%) do not pose any significant challenges for the event.

## Recommended Actions
* Review the registration process to ensure all participants have completed payment.
* Confirm the venue's ability to accommodate the expected number of participants.
* Prepare contingency plans in case of unexpected weather conditions, although it appears unlikely.
--------------------------------------------------
✓ Sačuvano u: output\reports\race-3-Weather-Test-Race-20260706-234357.md
```

Ovo potvrđuje da ceo lanac — baza → prognoza → strukturisan prompt → LLM → formatiran
Markdown izlaz sačuvan u fajl — stvarno radi od početka do kraja, sa oba provajdera
podržana (isti primer radi identično i sa `LLM_PROVIDER=openai` uz validan
`OPENAI_API_KEY`).

## Napomena o testiranju

Ceo agent, uključujući sam LLM poziv, je testiran uživo:

- `data/race_data.py` protiv stvarne `race_db` baze (pravi podaci o trci i prijavama).
- `weather/weather_client.py` protiv stvarnog Open-Meteo API-ja.
- `agent/briefing_agent.py` protiv lokalno pokrenutog Ollama servera (`llama3.2`).

Za demonstraciju na odbrani je i dalje potrebno popuniti `.env` (kopirati iz
`.env.example`) — ili sa `OPENAI_API_KEY` ili sa `LLM_PROVIDER=ollama` i pokrenutim
Ollama serverom — pošto `.env` namerno nije deo repozitorijuma (zahtev za bezbedno
čuvanje osetljivih podataka).
