# ObstaRace — mikroservisna platforma za prijavu na trke

ObstaRace je sistem za prijavu učesnika na trke, razvijen kao mikroservisna aplikacija.

## Arhitektura sistema

| Servis          | Opis                                                  | Baza       | Port  |
| --------------- | ----------------------------------------------------- | ---------- | ----- |
| User Service    | Registracija, prijava korisnika i upravljanje ulogama | PostgreSQL | 8000  |
| Race Service    | Upravljanje trkama i prijavama                        | PostgreSQL | 8001  |
| Payment Service | Obrada plaćanja putem Stripe-a                        | PostgreSQL | 8002  |
| Nginx           | API Gateway                                           | -          | 80    |
| Kafka           | Message broker                                        | -          | 29092 |
| Frontend        | React aplikacija                                      | -          | 5173  |

Svaki servis poseduje sopstvenu bazu i ne pristupa direktno podacima drugih servisa.

## Kafka komunikacija

| Topic                  | Producer        | Consumer        |
| ---------------------- | --------------- | --------------- |
| `registration_created` | Race Service    | Payment Service |
| `registration_deleted` | Race Service    | Payment Service |
| `payment_completed`    | Payment Service | Race Service    |
| `payment_failed`       | Payment Service | Race Service    |

## Tok registracije

1. Korisnik kreira prijavu za trku.
2. Race Service proverava uslove i kreira registraciju sa statusom `pending`.
3. Nakon uspešnog upisa emituje se događaj `registration_created`.
4. Payment Service kreira Stripe checkout sesiju.
5. Nakon plaćanja Stripe šalje webhook.
6. Payment Service emituje događaj o uspešnom ili neuspešnom plaćanju.
7. Race Service ažurira status prijave i šalje odgovarajući mejl korisniku.

## Primenjeni obrasci

Implementiran je koreografski **Saga pattern**. Konzistentnost sistema održava se pomoću lokalnih transakcija i Kafka događaja između servisa.

## Bezbednost

* XSS zaštita pomoću CSP i sigurnosnih HTTP zaglavlja.
* JWT tokeni u `httpOnly` kolačićima.
* Provera vlasništva nad resursima radi sprečavanja IDOR napada.
* Ograničen CORS pristup samo frontend aplikaciji.
* SQLAlchemy ORM i parametrizovani upiti za zaštitu od SQL Injection napada.

## Monitoring

Svaki servis izlaže `/metrics` endpoint. Prometheus prikuplja metrike, a Grafana omogućava njihov prikaz kroz dashboard-e.

## Preduslovi

* Docker
* Docker Compose
* Git

## Pokretanje sistema

1. Klonirati repozitorijum.
2. Kopirati `.env.example` u `.env` i popuniti potrebne vrednosti.
3. Pokrenuti sistem:

```bash
docker compose up --build
```

4. Pristup aplikacijama:

* API Gateway: http://localhost
* Frontend: http://localhost:5173
* Prometheus: http://localhost:9090
* Grafana: http://localhost:3001

5. Nakon prvog pokretanja preuzeti webhook secret iz logova `stripe-cli` kontejnera i upisati ga u promenljivu `PAYMENT_WEBHOOK_SECRET`, zatim restartovati Payment Service.

## Eksterni servisi

* Stripe — obrada plaćanja
* Mailtrap — slanje test mejlova
