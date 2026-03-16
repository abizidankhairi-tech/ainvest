import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import os

# Initialize app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.FONT_AWESOME,
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
    ],
    suppress_callback_exceptions=True,
    title="InvestAI - Portfolio Manager",
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"},
        {"name": "theme-color", "content": "#212529"},
        {"name": "apple-mobile-web-app-capable", "content": "yes"},
        {"name": "apple-mobile-web-app-status-bar-style", "content": "black-translucent"}
    ]
)

server = app.server

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# App layout with routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='user-session', storage_type='session'),  # Store JWT token
    dcc.Store(id='user-data', storage_type='session'),     # Store user info
    html.Div(id='page-content')
], style={"fontFamily": "'Inter', sans-serif"})


# Import page layouts
from pages.login import login_layout
from pages.register import register_layout
from pages.dashboard import dashboard_layout
from pages.portfolio import portfolio_layout
from pages.ai_chat import ai_chat_layout
from pages.strategies import strategies_layout
from pages.alerts import alerts_layout
from pages.import_portfolio import import_layout


# Routing callback
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('user-session', 'data')
)
def display_page(pathname, session):
    """Route to the appropriate page based on URL"""
    is_authenticated = session and 'token' in session
    
    # Public routes
    if pathname == '/login':
        if is_authenticated:
            return dcc.Location(pathname='/dashboard', id='redirect-to-dashboard')
        return login_layout
    
    elif pathname == '/register':
        if is_authenticated:
            return dcc.Location(pathname='/dashboard', id='redirect-to-dashboard')
        return register_layout
    
    # Protected routes
    elif pathname == '/' or pathname == '/dashboard':
        if is_authenticated:
            return dashboard_layout
        return dcc.Location(pathname='/login', id='redirect-to-login')
    
    elif pathname == '/portfolio':
        if is_authenticated:
            return portfolio_layout
        return dcc.Location(pathname='/login', id='redirect-to-login')
    
    elif pathname == '/ai':
        if is_authenticated:
            return ai_chat_layout
        return dcc.Location(pathname='/login', id='redirect-to-login')
    
    elif pathname == '/strategies':
        if is_authenticated:
            return strategies_layout
        return dcc.Location(pathname='/login', id='redirect-to-login')
    
    elif pathname == '/alerts':
        if is_authenticated:
            return alerts_layout
        return dcc.Location(pathname='/login', id='redirect-to-login')
    
    elif pathname == '/import':
        if is_authenticated:
            return import_layout
        return dcc.Location(pathname='/login', id='redirect-to-login')
    
    # Default - redirect based on auth status
    else:
        if is_authenticated:
            return dashboard_layout
        return dcc.Location(pathname='/login', id='redirect-to-login')


# Import callbacks
from pages import login, register, dashboard, portfolio, ai_chat, strategies, alerts, import_portfolio


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8050))
    debug = os.getenv('ENVIRONMENT', 'development') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)
