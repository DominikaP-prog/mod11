import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import pandas as pd
import dash
from dash import html, dcc, Input, Output
import plotly.express as px

# 🔽 Ścieżki do plików CSV — ZMIEŃ jeśli potrzebujesz
transactions_path = r"C:\Users\dpiekutowska\OneDrive - OSGE\Pulpit\Kodilla DoPi\11_projekt\Kanały sprzedaży\db\transactions\transactions.csv"
customers_path = r"C:\Users\dpiekutowska\OneDrive - OSGE\Pulpit\Kodilla DoPi\11_projekt\Kanały sprzedaży\db\transactions\customers.csv"

# 🔽 Wczytanie danych
transactions = pd.read_csv(transactions_path)
customers = pd.read_csv(customers_path)

# 🔽 Konwersja daty
transactions['tran_date'] = pd.to_datetime(transactions['tran_date'], dayfirst=True, errors='coerce')
customers['DOB'] = pd.to_datetime(customers['DOB'], dayfirst=True, errors='coerce')
customers['age'] = 2025 - customers['DOB'].dt.year

# 🔽 Połączenie danych
data = transactions.merge(customers, left_on='cust_id', right_on='customer_Id', how='left')
data['weekday'] = data['tran_date'].dt.day_name()

# 🔽 Tworzenie aplikacji Dash
app = dash.Dash(__name__)
app.title = "Kanały sprzedaży – Dashboard"

# 🔽 Layout aplikacji
app.layout = html.Div([
    html.H2("📊 Analiza kanałów sprzedaży", style={"textAlign": "center"}),

    html.Div([
        html.Label("Wybierz kanał sprzedaży:"),
        dcc.Dropdown(
            id='store-dropdown',
            options=[{'label': s, 'value': s} for s in sorted(data['Store_type'].dropna().unique())],
            value=sorted(data['Store_type'].dropna().unique())[0],
            style={"width": "50%"}
        )
    ], style={"padding": "20px"}),

    dcc.Graph(id='weekday-sales-graph'),

    html.Div([
        dcc.Graph(id='gender-pie'),
        dcc.Graph(id='age-histogram')
    ], style={"display": "flex", "justifyContent": "space-around"})
])

# 🔽 Callback do aktualizacji wykresów
@app.callback(
    Output('weekday-sales-graph', 'figure'),
    Output('gender-pie', 'figure'),
    Output('age-histogram', 'figure'),
    Input('store-dropdown', 'value')
)
def update_dashboard(store_type):
    df = data[data['Store_type'] == store_type]

    # Sprzedaż wg dnia tygodnia
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    sales_by_day = df.groupby('weekday')['total_amt'].sum().reindex(weekday_order)
    fig_sales = px.bar(
        x=sales_by_day.index, y=sales_by_day.values,
        labels={'x': 'Dzień tygodnia', 'y': 'Suma sprzedaży'},
        title='🗓️ Sprzedaż wg dnia tygodnia'
    )

    # Rozkład płci
    gender_counts = df['Gender'].value_counts()
    fig_gender = px.pie(
        names=gender_counts.index, values=gender_counts.values,
        title='👤 Płeć klientów'
    )

    # Rozkład wieku
    fig_age = px.histogram(
        df, x='age', nbins=20,
        title='🎂 Rozkład wieku klientów',
        labels={'age': 'Wiek'}
    )

    return fig_sales, fig_gender, fig_age

# 🔽 Uruchomienie aplikacji
if __name__ == '__main__':
    app.run_server(debug=True)