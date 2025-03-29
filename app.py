import gradio as gr
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from dotenv import load_dotenv

# Laad omgevingsvariabelen
load_dotenv()

# API-endpoint configuratie - standaard URLs die kunnen worden aangepast
DEFAULT_API_URL = "https://rwsos-dataservices-ont.avi.deltares.nl/iwp/FewsWebServices/rest/fewspiservice/v1"

# Bekende API-endpoints en hun mappings
API_ENDPOINT_MAPPINGS = {
    "https://ffws2.savagis.org/FewsWebServices": {
        "rest_endpoint": "/rest/fewspiservice/v1",  # REST API endpoint
        "locations_endpoint": "/rest/fewspiservice/v1/locations",
        "parameters_endpoint": "/rest/fewspiservice/v1/parameters",
        "timeseries_endpoint": "/rest/fewspiservice/v1/timeseries"
    },
    "https://rwsos-dataservices-ont.avi.deltares.nl/iwp/FewsWebServices": {
        "rest_endpoint": "/rest/fewspiservice/v1",
        "locations_endpoint": "/rest/fewspiservice/v1/locations",
        "parameters_endpoint": "/rest/fewspiservice/v1/parameters",
        "timeseries_endpoint": "/rest/fewspiservice/v1/timeseries"
    }
}

# Deltares/FEWS huisstijl kleuren
DELTARES_BLUE = "#0079C2"  # Primaire Deltares kleur
DELTARES_DARK_BLUE = "#003D5F"
DELTARES_LIGHT_BLUE = "#E4F2F7"
DELTARES_WHITE = "#FFFFFF"
DELTARES_BLACK = "#000000"
DELTARES_LIGHT_GREY = "#F0F0F0"
DELTARES_DARK_GREY = "#606060"

# Functie om de juiste endpoints te bepalen voor de gegeven API URL
def get_endpoints(api_url):
    # Verwijder eventuele slash aan het einde
    if api_url.endswith('/'):
        api_url = api_url[:-1]
    
    # Controleer of dit een bekende basis URL is
    for base_url, endpoints in API_ENDPOINT_MAPPINGS.items():
        if api_url.startswith(base_url):
            return {
                "base_url": base_url,
                "rest_endpoint": endpoints["rest_endpoint"],
                "locations_endpoint": endpoints["locations_endpoint"],
                "parameters_endpoint": endpoints["parameters_endpoint"],
                "timeseries_endpoint": endpoints["timeseries_endpoint"]
            }
    
    # Als het geen bekende URL is, probeer dan de standaard patronen
    if "/rest/fewspiservice/v1" in api_url:
        base_url = api_url.split("/rest/fewspiservice/v1")[0]
        return {
            "base_url": base_url,
            "rest_endpoint": "/rest/fewspiservice/v1",
            "locations_endpoint": "/rest/fewspiservice/v1/locations",
            "parameters_endpoint": "/rest/fewspiservice/v1/parameters",
            "timeseries_endpoint": "/rest/fewspiservice/v1/timeseries"
        }
    
    # Als laatste optie, neem aan dat de gegeven URL de basis URL is
    return {
        "base_url": api_url,
        "rest_endpoint": "/rest/fewspiservice/v1",
        "locations_endpoint": "/rest/fewspiservice/v1/locations",
        "parameters_endpoint": "/rest/fewspiservice/v1/parameters",
        "timeseries_endpoint": "/rest/fewspiservice/v1/timeseries"
    }

# Functies voor het ophalen van data
def get_locations(api_url):
    try:
        endpoints = get_endpoints(api_url)
        url = f"{endpoints['base_url']}{endpoints['locations_endpoint']}?documentFormat=PI_JSON"
        print(f"Request URL: {url}")
        response = requests.get(url)
        
        # Debug informatie
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response tekst: {response.text[:1000]}...") # Eerste 1000 tekens
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request fout: {str(e)}")
        return {"error": f"Request fout: {str(e)}"}
    except json.JSONDecodeError as e:
        print(f"JSON decode fout: {str(e)}, response: {response.text[:500]}...")
        return {"error": f"JSON decodering mislukt: {str(e)}"}
    except Exception as e:
        print(f"Algemene fout: {str(e)}")
        return {"error": str(e)}

def get_parameters(api_url):
    try:
        endpoints = get_endpoints(api_url)
        url = f"{endpoints['base_url']}{endpoints['parameters_endpoint']}?documentFormat=PI_JSON"
        print(f"Request URL: {url}")
        response = requests.get(url)
        print(f"Status code: {response.status_code}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request fout: {str(e)}")
        return {"error": f"Request fout: {str(e)}"}
    except json.JSONDecodeError as e:
        print(f"JSON decode fout: {str(e)}")
        return {"error": f"JSON decodering mislukt: {str(e)}"}
    except Exception as e:
        print(f"Algemene fout: {str(e)}")
        return {"error": str(e)}

def get_timeseries(api_url, location_ids, parameter_ids, start_date=None, end_date=None):
    # Converteer enkele strings naar lijsten indien nodig
    if isinstance(location_ids, str):
        location_ids = [location_ids.strip()]
    if isinstance(parameter_ids, str):
        parameter_ids = [parameter_ids.strip()]
    
    params = {
        "locationIds": ",".join(location_ids),
        "parameterIds": ",".join(parameter_ids),
        "documentFormat": "DD_JSON",
        "omitMissing": "true"
    }
    
    if start_date:
        params["startTime"] = start_date
    if end_date:
        params["endTime"] = end_date
    
    try:
        endpoints = get_endpoints(api_url)
        request_url = f"{endpoints['base_url']}{endpoints['timeseries_endpoint']}"
        print(f"Request URL: {request_url}")
        print(f"Request parameters: {params}")
        response = requests.get(request_url, params=params)
        print(f"Status code: {response.status_code}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request fout: {str(e)}")
        return {"error": f"Request fout: {str(e)}"}
    except json.JSONDecodeError as e:
        print(f"JSON decode fout: {str(e)}")
        return {"error": f"JSON decodering mislukt: {str(e)}"}
    except Exception as e:
        print(f"Algemene fout: {str(e)}")
        return {"error": str(e)}

# UI functies
def fetch_locations(api_url):
    if not api_url:
        return "Vul eerst een geldige API URL in", None, []
    
    data = get_locations(api_url)
    if "error" in data:
        return f"Fout bij het ophalen van locaties: {data['error']}", None, []
    
    # Verwerk de PI_JSON formaat van locaties
    locations = []
    location_options = []
    unique_ids = set()  # Set voor het bijhouden van unieke IDs
    
    # Controleer of we het verwachte formaat hebben
    if "locations" in data:
        for location in data.get("locations", []):
            # Haal ID op
            location_id = location.get("locationId", "Onbekend")
            location_name = location.get("description", location.get("shortName", "Onbekend"))
            
            # Alle beschikbare velden uit de locatie toevoegen
            location_data = {
                "id": location_id,
                "name": location_name,
                "shortName": location.get("shortName", ""),
                "lat": location.get("lat", ""),
                "lon": location.get("lon", ""),
                "x": location.get("x", ""),
                "y": location.get("y", ""),
                "z": location.get("z", "")
            }
            
            # Attributen toevoegen als die beschikbaar zijn
            if "attributes" in location and location["attributes"]:
                for i, attr in enumerate(location["attributes"]):
                    if "id" in attr and "text" in attr:
                        location_data[f"attr_{attr['id']}"] = attr["text"]
            
            locations.append(location_data)
            unique_ids.add(location_id)
            
            # Voeg alleen ID toe aan dropdown-opties (zonder naam)
            location_options.append(location_id)
    
    if not locations:
        return "Geen locaties gevonden", None, []
    
    # Beperk tot eerste 5 opties
    limited_location_options = location_options[:5]
    
    locations_df = pd.DataFrame(locations)
    return f"{len(unique_ids)} unieke locaties gevonden uit {len(locations)} items (eerste 5 getoond)", locations_df, limited_location_options

def fetch_parameters(api_url):
    if not api_url:
        return "Vul eerst een geldige API URL in", None, []
    
    data = get_parameters(api_url)
    if "error" in data:
        return f"Fout bij het ophalen van parameters: {data['error']}", None, []
    
    # Verwerk de PI_JSON formaat van parameters
    parameters = []
    parameter_options = []
    unique_ids = set()  # Set voor het bijhouden van unieke IDs
    
    # Controleer of we het verwachte formaat hebben
    if "timeSeriesParameters" in data:
        for parameter in data.get("timeSeriesParameters", []):
            # Haal ID op
            parameter_id = parameter.get("id", "Onbekend")
            parameter_name = parameter.get("name", "Onbekend")
            
            # Alle beschikbare velden uit de parameter toevoegen
            param_data = {
                "id": parameter_id,
                "name": parameter_name,
                "shortName": parameter.get("shortName", ""),
                "unit": parameter.get("unit", ""),
                "displayUnit": parameter.get("displayUnit", ""),
                "parameterType": parameter.get("parameterType", ""),
                "parameterGroup": parameter.get("parameterGroup", ""),
                "parameterGroupName": parameter.get("parameterGroupName", ""),
                "usesDatum": parameter.get("usesDatum", "")
            }
            parameters.append(param_data)
            unique_ids.add(parameter_id)
            
            # Voeg alleen ID toe aan dropdown-opties (zonder naam)
            parameter_options.append(parameter_id)
    
    if not parameters:
        return "Geen parameters gevonden", None, []
    
    # Beperk tot eerste 5 opties
    limited_parameter_options = parameter_options[:5]
    
    params_df = pd.DataFrame(parameters)
    return f"{len(unique_ids)} unieke parameters gevonden uit {len(parameters)} items (eerste 5 getoond)", params_df, limited_parameter_options

def fetch_timeseries(api_url, location_ids, parameter_ids, start_date, end_date):
    if not api_url:
        return "Vul eerst een geldige API URL in", None, None
        
    if not location_ids or not parameter_ids:
        return "Selecteer tenminste één locatie en parameter", None, None
    
    # Formateer datums correct
    if start_date:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            return f"Ongeldige startdatum format: {start_date}. Gebruik YYYY-MM-DD.", None, None
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            return f"Ongeldige einddatum format: {end_date}. Gebruik YYYY-MM-DD.", None, None
    
    data = get_timeseries(api_url, location_ids, parameter_ids, start_date, end_date)
    
    if "error" in data:
        return f"Fout bij het ophalen van tijdseries: {data['error']}", None, None
    
    # Verwerk de DD_JSON formaat van tijdseries
    all_series = []
    
    # Controleer of we het verwachte formaat hebben
    if "results" in data:
        for result in data.get("results", []):
            if "events" not in result:
                continue
                
            # Haal locatie en parameter informatie op
            location_id = "Onbekend"
            parameter_id = "Onbekend"
            
            if "location" in result and "properties" in result["location"]:
                location_id = result["location"]["properties"].get("locationId", "Onbekend")
                
            if "observationType" in result:
                parameter_id = result["observationType"].get("parameterCode", "Onbekend")
            
            # Verwerk events
            for event in result.get("events", []):
                all_series.append({
                    "locationId": location_id,
                    "parameterId": parameter_id,
                    "timestamp": event.get("timeStamp", ""),
                    "value": event.get("value", None)
                })
    
    if not all_series:
        return "Geen gegevens gevonden in de tijdseries", None, None
    
    df = pd.DataFrame(all_series)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    
    # Sorteer de data chronologisch op timestamp
    df = df.sort_values(by="timestamp")
    
    # Maak een unieke legenda-identifier per combinatie van locatie en parameter
    df["series_id"] = df["locationId"] + " - " + df["parameterId"]
    
    # Deltares kleurenpalet voor de plot
    deltares_colors = [
        DELTARES_BLUE, DELTARES_DARK_BLUE, DELTARES_LIGHT_BLUE, 
        "#5DACDB", "#8ABCDB", "#B9D9ED"  # Extra lichtblauwe tinten
    ]
    
    # Maak één enkele plot met aparte lijnen voor elke unieke combinatie
    fig = px.line(df, x="timestamp", y="value", color="series_id", 
                 title=f"Tijdseries voor alle locatie-parameter combinaties",
                 color_discrete_sequence=deltares_colors)
    
    # Voeg markers toe voor elke meting
    fig.update_traces(mode='lines+markers', marker=dict(size=6))
    
    # Update layout
    fig.update_layout(
        xaxis_title="Datum",
        yaxis_title="Waarde",
        legend_title="Locatie - Parameter",
        hovermode="x unified",  # Alle waardes tonen bij hover op dezelfde x-positie
        font=dict(family="Roboto, Arial, sans-serif"),
        plot_bgcolor=DELTARES_WHITE,
        paper_bgcolor=DELTARES_WHITE,
        title_font=dict(size=18, color=DELTARES_BLACK),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02,
            title_font=dict(size=12),
            font=dict(size=10)
        ),
        margin=dict(l=50, r=150, t=80, b=50)
    )
    
    # Update axes
    fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='rgba(0,0,0,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='rgba(0,0,0,0.1)')
    
    return f"Tijdseries gevonden voor de geselecteerde criteria", df, fig

# Functie om locaties en parameters op te halen na het invoeren van een URL
def update_api_url(api_url):
    if not api_url:
        api_url = DEFAULT_API_URL
    
    # Verwijder eventuele slash aan het einde
    if api_url.endswith('/'):
        api_url = api_url[:-1]
    
    # Poging om te veranderen naar een REST endpoint als het nog niet is gespecificeerd
    if not ("/rest/fewspiservice/v1" in api_url):
        endpoints = get_endpoints(api_url)
        api_url = f"{endpoints['base_url']}{endpoints['rest_endpoint']}"
    
    # Fetch locaties en parameters
    loc_status, loc_df, loc_options = fetch_locations(api_url)
    param_status, param_df, param_options = fetch_parameters(api_url)
    
    return api_url, loc_status, loc_df, loc_options, param_status, param_df, param_options

# Custom CSS voor Deltares/FEWS stijl
css = """
:root {
    --deltares-blue: #0079C2;
    --deltares-dark-blue: #003D5F;
    --deltares-light-blue: #E4F2F7;
    --deltares-white: #FFFFFF;
    --deltares-black: #000000;
    --deltares-light-grey: #F0F0F0;
    --deltares-dark-grey: #606060;
}

body, .gradio-container {
    font-family: 'Roboto', Arial, sans-serif !important;
    color: var(--deltares-black);
    background-color: var(--deltares-white);
}

h1 {
    color: var(--deltares-blue) !important;
    font-weight: 700 !important;
    margin-bottom: 10px !important;
}

h2, h3 {
    color: var(--deltares-dark-blue) !important;
    font-weight: 600 !important;
    margin-top: 20px !important;
}

.header-logo {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
    background-color: var(--deltares-white) !important;
}

.header-logo img {
    height: 70px;
    margin-right: 20px;
}

.btn-primary {
    background-color: var(--deltares-blue) !important;
    border-color: var(--deltares-blue) !important;
}

.btn-primary:hover {
    background-color: var(--deltares-dark-blue) !important;
    border-color: var(--deltares-dark-blue) !important;
}

.status-message {
    padding: 10px;
    border-radius: 4px;
    background-color: var(--deltares-light-grey);
    margin: 10px 0;
}

.tabs .tab-nav * {
    color: var(--deltares-blue) !important;
}

.footer {
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #eee;
    text-align: center;
    font-size: 0.9em;
    color: var(--deltares-dark-grey);
}
"""

# Delft-FEWS logo URL (officiële bron)
fews_logo_url = "https://oss.deltares.nl/o/deltares-fews-theme/images/logo.svg"

# UI opbouw
with gr.Blocks(title="FEWS Webservices Explorer", css=css) as demo:
    with gr.Column():
        # Header met Delft-FEWS branding
        with gr.Row(elem_classes="header-logo"):
            gr.HTML(f"""
                <div style="background-color: white; padding: 20px; width: 100%; display: flex; align-items: center; border-bottom: 3px solid #0079C2;">
                    <img src="{fews_logo_url}" alt="Delft-FEWS Logo" style="height: 60px; margin-right: 20px;">
                    <div>
                        <h1 style="color: #0079C2; margin: 0; font-size: 28px; font-weight: bold;">FEWS Webservices Explorer</h1>
                        <p style="color: #003D5F; margin: 0;">Data explorer voor FEWS webservice endpoints</p>
                    </div>
                </div>
            """)
    
        # Introductie
        with gr.Row():
            gr.Markdown("""
                ### Over deze applicatie
                Deze applicatie maakt het mogelijk om op een gemakkelijke manier data op te vragen van een FEWS Webservice. 
                Voer een geldige FEWS webservice URL in, selecteer locaties en parameters, en visualiseer tijdseries.
            """)
        
        # API URL sectie
        with gr.Row():
            with gr.Column(scale=3):
                api_url_input = gr.Textbox(
                    label="API URL", 
                    placeholder="Voer de URL van de FEWS REST service in",
                    value=DEFAULT_API_URL,
                    info="Bijvoorbeeld: https://ffws2.savagis.org/FewsWebServices of https://rwsos-dataservices-ont.avi.deltares.nl/iwp/FewsWebServices"
                )
            with gr.Column(scale=1):
                update_api_btn = gr.Button("Verbinden en data ophalen", variant="primary", elem_classes="btn-primary")
        
        # Status berichten met modern ontwerp
        with gr.Row():
            with gr.Column():
                locations_status = gr.Textbox(label="Status Locaties", interactive=False, elem_classes="status-message")
            with gr.Column():
                parameters_status = gr.Textbox(label="Status Parameters", interactive=False, elem_classes="status-message")
        
        # Verborgen containers voor data
        locations_df = gr.DataFrame(label="Locaties", visible=False)
        parameters_df = gr.DataFrame(label="Parameters", visible=False)
        
        # Tijdseries sectie
        gr.Markdown("## Tijdseries opvragen en visualiseren")
        
        with gr.Row():
            with gr.Column(scale=3):
                with gr.Row():
                    with gr.Column(scale=2):
                        # Locatie dropdown met verbeterde styling
                        location_dropdown = gr.Dropdown(
                            label="Selecteer locatie(s)", 
                            multiselect=True,
                            interactive=True,
                            info="Selecteer één of meerdere locatie-IDs",
                            allow_custom_value=True,
                            filterable=True,
                            value=[]
                        )
                        
                        # Parameter dropdown met verbeterde styling
                        parameter_dropdown = gr.Dropdown(
                            label="Selecteer parameter(s)", 
                            multiselect=True,
                            interactive=True,
                            info="Selecteer één of meerdere parameter-IDs",
                            allow_custom_value=True,
                            filterable=True,
                            value=[]
                        )
                    
                    with gr.Column(scale=1):
                        start_date_input = gr.Textbox(
                            label="Startdatum", 
                            placeholder="YYYY-MM-DD",
                            info="Laat leeg voor alle beschikbare data"
                        )
                        end_date_input = gr.Textbox(
                            label="Einddatum", 
                            placeholder="YYYY-MM-DD",
                            info="Laat leeg voor alle beschikbare data"
                        )
                        timeseries_btn = gr.Button("Tijdseries ophalen", variant="primary", elem_classes="btn-primary")
            
        with gr.Row():
            timeseries_status = gr.Textbox(label="Status Tijdseries", interactive=False, elem_classes="status-message")
        
        # Resultaten sectie
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Resultaten")
                # Tab interface voor verschillende weergavemethoden
                with gr.Tabs():
                    with gr.TabItem("Grafiek"):
                        timeseries_plot = gr.Plot(label="Tijdseries")
                    with gr.TabItem("Tabel"):
                        timeseries_df = gr.DataFrame(label="Tijdseries Data")
        
        # Footer
        with gr.Row(elem_classes="footer"):
            gr.HTML(f"""
                <div class="footer">
                    <p>© Deltares | Ontwikkeld voor FEWS Data Exploratie</p>
                    <p><a href="https://huggingface.co/spaces/tberends/fewswsexplorer" target="_blank" style="color: #0079C2;">Hugging Face Space</a> | 
                    <a href="https://github.com/gebruikersnaam/repo-naam" target="_blank" style="color: #0079C2;">GitHub Repository</a></p>
                </div>
            """)
    
    # Update API URL actie
    update_api_btn.click(
        update_api_url,
        inputs=[api_url_input],
        outputs=[
            api_url_input,
            locations_status, 
            locations_df, 
            location_dropdown,
            parameters_status,
            parameters_df,
            parameter_dropdown
        ]
    )
    
    # Timeseries knop actie
    timeseries_btn.click(
        fetch_timeseries, 
        inputs=[api_url_input, location_dropdown, parameter_dropdown, start_date_input, end_date_input], 
        outputs=[timeseries_status, timeseries_df, timeseries_plot]
    )

# Start de app
if __name__ == "__main__":
    demo.launch()
