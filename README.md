---
title: FEWS Webservices Explorer
emoji: 🌊
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 5.16.0
app_file: app.py
pinned: false
---

# FEWS Webservices Explorer

Deze Gradio-applicatie stelt gebruikers in staat om data op te vragen van een FEWS webservice. De app ondersteunt het opvragen van locaties, parameters en tijdseries.

## Hugging Face Space

Deze applicatie is ook beschikbaar als Hugging Face Space:
[https://huggingface.co/spaces/tberends/fewswsexplorer](https://huggingface.co/spaces/tberends/fewswsexplorer)

## Functionaliteiten

- **Locaties ophalen**: Bekijk alle beschikbare locaties in de FEWS webservice.
- **Parameters ophalen**: Bekijk alle beschikbare parameters in de FEWS webservice.
- **Tijdseries ophalen**: Vraag tijdseriedata op basis van locatie-ID's, parameter-ID's en tijdperiode.
- **Visualisatie**: Bekijk de opgevraagde tijdseriedata in een interactieve grafiek.
- **Flexibele API URL**: Ondersteunt verschillende FEWS webservice URL formaten, waaronder:
  - `https://ffws2.savagis.org/FewsWebServices`
  - `https://rwsos-dataservices-ont.avi.deltares.nl/iwp/FewsWebServices/rest/fewspiservice/v1`

## Bestanden

- `src/app.py`: Het hoofdbestand van de Gradio-applicatie. Bevat de logica voor het ophalen en weergeven van data uit de FEWS webservice.
- `requirements.txt`: Bevat de benodigde Python-pakketten voor de applicatie.
- `.env`: Configuratiebestand voor het instellen van API-endpoints.
- `Procfile`: Configuratie voor deployment op Hugging Face Spaces.

## Installatie

1. Zorg dat Python 3.8+ is geïnstalleerd:
   ```
   python --version
   ```

2. (Optioneel) Maak een nieuwe virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # Op Unix/macOS
   # OF
   venv\Scripts\activate  # Op Windows
   ```

3. Clone de repository:
   ```
   git clone <repository-url>
   cd fewswsexplorer
   ```

4. Installeer de vereiste pakketten:
   ```
   pip install -r requirements.txt
   ```

5. Configureer de `.env` file (optioneel):
   ```
   API_URL=https://rwsos-dataservices-ont.avi.deltares.nl/iwp/FewsWebServices
   ```

## Gebruik

Om de applicatie lokaal te starten:
```
python src/app.py
```

Of als je de src directory gebruikt:
```
cd src
python app.py
```

De applicatie zal draaien op `http://localhost:7860`.

## API URL Formaten

De applicatie ondersteunt verschillende URL formaten voor FEWS webservices:

1. Basis URL (wordt automatisch aangevuld met de juiste endpoints):
   ```
   https://ffws2.savagis.org/FewsWebServices
   ```

2. Volledig pad naar de REST API:
   ```
   https://rwsos-dataservices-ont.avi.deltares.nl/iwp/FewsWebServices/rest/fewspiservice/v1
   ```

De app detecteert automatisch welke URL structuur wordt gebruikt en past de juiste endpoints toe.

## Deployen op Hugging Face

Volg deze stappen om de applicatie te deployen op Hugging Face:

1. Maak een account aan op Hugging Face en log in.
2. Maak een nieuwe Space aan met het Gradio SDK.
3. Upload de volgende bestanden naar je Space:
   - `src/app.py` (kopieer dit naar de root als `app.py`)
   - `requirements.txt`
   - `README.md`
   - `Procfile`

## API Documentatie

De applicatie gebruikt de FEWS REST API v1 met de volgende endpoints:
- `/rest/fewspiservice/v1/locations`: Voor het ophalen van locatiegegevens (PI_JSON formaat)
- `/rest/fewspiservice/v1/parameters`: Voor het ophalen van parametergegevens (PI_JSON formaat)
- `/rest/fewspiservice/v1/timeseries`: Voor het ophalen van tijdseriegegevens (DD_JSON formaat)

Meer informatie over de FEWS API is beschikbaar op:
https://publicwiki.deltares.nl/display/FEWSDOC/FEWS+Web+Services

## Licentie

Dit project is gelicentieerd onder de MIT-licentie.
