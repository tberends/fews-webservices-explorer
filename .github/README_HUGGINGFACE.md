# FEWS Webservices Explorer - Hugging Face Deployment

Deze repository bevat een Gradio-app voor het opvragen en visualiseren van data uit een FEWS webservice. De app ondersteunt verschillende FEWS WebService URL-formaten.

## Implementatie op Hugging Face Spaces

Volg deze stappen om de app te implementeren op Hugging Face Spaces:

1. Ga naar [Hugging Face](https://huggingface.co/) en log in of maak een account aan.
2. Klik op je profiel en selecteer "New Space".
3. Kies een naam voor je Space, bijvoorbeeld "fews-webservices-explorer".
4. Selecteer "Gradio" als SDK.
5. Klik op "Create Space".
6. Zodra de Space is aangemaakt, ga je naar het tabblad "Files" en upload je de volgende bestanden:
   - `app.py` (kopieer de inhoud van `src/app.py` naar de root van je Space)
   - `requirements.txt`
   - `README.md`
   - `Procfile`

## Ondersteunde API URL-formaten

De app is ontworpen om verschillende URL-formaten voor FEWS webservices te verwerken:

1. Basis URL (automatisch aangevuld):
   ```
   https://ffws2.savagis.org/FewsWebServices
   ```

2. Volledige URL met REST endpoint:
   ```
   https://rwsos-dataservices-ont.avi.deltares.nl/iwp/FewsWebServices/rest/fewspiservice/v1
   ```

De applicatie detecteert automatisch welk formaat wordt gebruikt en past de juiste endpoints toe.

## Configuratie (optioneel)

Als je een standaard API URL wilt instellen, kan je deze toevoegen als omgevingsvariabele:

1. Ga naar het tabblad "Settings" van je Space.
2. Scrol naar beneden naar de sectie "Repository secrets".
3. Voeg de volgende omgevingsvariabele toe:
   - `API_URL`: URL van de FEWS webservice (bijv. `https://ffws2.savagis.org/FewsWebServices`)

## Updates uitrollen

Om updates uit te rollen naar je Hugging Face Space:

1. Bewerk de bestanden lokaal.
2. Commit en push de wijzigingen naar je GitHub repository.
3. Verbind je GitHub repository met je Hugging Face Space via de "Settings" pagina.
4. Configureer automatische synchronisatie tussen GitHub en Hugging Face.

## Probleemoplossing

Als je problemen ondervindt bij het implementeren of gebruiken van de app op Hugging Face Spaces:

1. Controleer de "Build logs" op het tabblad "Settings" van je Space.
2. Controleer of de `Procfile` correct is geconfigureerd met `web: python app.py`.
3. Controleer of alle vereiste packages in `requirements.txt` zijn opgenomen.
4. Als de app niet correct verbinding maakt, klik op de "Verbinden en data ophalen" knop na het invoeren van een geldige API URL. 