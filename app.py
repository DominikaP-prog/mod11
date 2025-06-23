import dash
from dash import html, dcc, Input, Output
import tab1
import tab2
import tab3
import db

# Wczytaj dane
df = db.DB()

# Inicjalizacja aplikacji
app = dash.Dash(__name__)
app.title = "Dashboard Sprzedaży"

# Layout
app.layout = html.Div([
    html.H1("Dashboard sprzedaży", style={'text-align': 'center'}),

    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='Sprzedaż globalna', value='tab-1'),
        dcc.Tab(label='Produkty', value='tab-2'),
        dcc.Tab(label='Kanały sprzedaży', value='tab-3')
    ]),
    html.Div(id='tabs-content')
])

# Callback dla przełączania zakładek
@app.callback(Output('tabs-content', 'children'), Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return tab1.render_tab(df.merged)
    elif tab == 'tab-2':
        return tab2.render_tab(df.merged)
    elif tab == 'tab-3':
        return tab3.render_tab(df.merged)

# Callback dla zakładki 3
@app.callback(
    Output('weekday-sales', 'figure'),
    Output('gender-pie', 'figure'),
    Output('age-hist', 'figure'),
    Input('store-dropdown', 'value')
)
def update_store(store_type):
    data = df.merged[df.merged['Store_type'] == store_type]

    # Sprzedaż wg dni tygodnia
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    sales_by_day = data.groupby('weekday')['total_amt'].sum().reindex(weekday_order)
    fig_weekday = go.Figure([go.Bar(x=sales_by_day.index, y=sales_by_day.values)])
    fig_weekday.update_layout(title="Sprzedaż wg dnia tygodnia")

    # Płeć
    gender_counts = data['Gender'].value_counts()
    fig_gender = go.Figure([go.Pie(labels=gender_counts.index, values=gender_counts.values)])
    fig_gender.update_layout(title="Płeć klientów")

    # Wiek
    fig_age = go.Figure([go.Histogram(x=data['age'], nbinsx=20)])
    fig_age.update_layout(title="Wiek klientów")

    return fig_weekday, fig_gender, fig_age

# Uruchomienie aplikacji
if __name__ == '__main__':
    app.run(debug=True)