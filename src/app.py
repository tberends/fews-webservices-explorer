import gradio as gr
import requests
import json
import pandas as pd
import plotly.express as px
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
    
    # Maak één enkele plot met aparte lijnen voor elke unieke combinatie
    fig = px.line(df, x="timestamp", y="value", color="series_id", 
                 title=f"Tijdseries voor alle locatie-parameter combinaties")
    
    # Voeg markers toe voor elke meting
    fig.update_traces(mode='lines+markers', marker=dict(size=6))
    
    # Update layout
    fig.update_layout(
        xaxis_title="Datum",
        yaxis_title="Waarde",
        legend_title="Locatie - Parameter",
        hovermode="x unified",  # Alle waardes tonen bij hover op dezelfde x-positie
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02,
            title_font=dict(size=12)
        )
    )
    
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

# UI opbouw
with gr.Blocks(title="FEWS Webservices Explorer") as demo:
    gr.Markdown("# FEWS Webservices Explorer")
    gr.Markdown("Deze applicatie maakt het mogelijk om data op te vragen van een FEWS Webservice.")
    
    # API URL instelling met bekende voorbeelden
    with gr.Row():
        api_url_input = gr.Textbox(
            label="API URL", 
            placeholder="Voer de URL van de FEWS REST service in",
            value=DEFAULT_API_URL,
            info="Bijvoorbeeld: https://ffws2.savagis.org/FewsWebServices of https://rwsos-dataservices-ont.avi.deltares.nl/iwp/FewsWebServices"
        )
        update_api_btn = gr.Button("Verbinden en data ophalen")
    
    # Status berichten
    with gr.Row():
        locations_status = gr.Textbox(label="Status Locaties", interactive=False)
        parameters_status = gr.Textbox(label="Status Parameters", interactive=False)
    
    # Verborgen containers voor data
    locations_df = gr.DataFrame(label="Locaties", visible=False)
    parameters_df = gr.DataFrame(label="Parameters", visible=False)
    
    # Tijdseries sectie
    gr.Markdown("## Tijdseries ophalen")
    with gr.Row():
        with gr.Column():
            # Locatie dropdown - alleen IDs, met verbeterde instellingen
            location_dropdown = gr.Dropdown(
                label="Selecteer locatie", 
                multiselect=True,
                interactive=True,
                info="Selecteer één of meerdere locatie-IDs",
                scale=2,
                allow_custom_value=True,
                filterable=True,
                value=[]  # Lege lijst als standaardwaarde om dropdown te laten tonen
            )
            
            # Parameter dropdown - alleen IDs, met verbeterde instellingen
            parameter_dropdown = gr.Dropdown(
                label="Selecteer parameter", 
                multiselect=True,
                interactive=True,
                info="Selecteer één of meerdere parameter-IDs",
                scale=2,
                allow_custom_value=True,
                filterable=True,
                value=[]  # Lege lijst als standaardwaarde om dropdown te laten tonen
            )
        
        with gr.Column():
            start_date_input = gr.Textbox(label="Startdatum (YYYY-MM-DD)")
            end_date_input = gr.Textbox(label="Einddatum (YYYY-MM-DD)")
    
    with gr.Row():
        timeseries_btn = gr.Button("Tijdseries ophalen")
    
    with gr.Row():
        timeseries_status = gr.Textbox(label="Status Tijdseries", interactive=False)
    
    with gr.Row():
        timeseries_df = gr.DataFrame(label="Tijdseries Data")
    
    # Enkele plot voor alle tijdseries
    gr.Markdown("### Tijdseries voor alle locatie-parameter combinaties")
    with gr.Row():
        timeseries_plot = gr.Plot(label="Tijdseries")
    
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
