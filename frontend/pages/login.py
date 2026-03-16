import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Login page layout
login_layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            # Logo and title
            html.Div([
                html.Div([
                    html.I(className="fas fa-chart-line fa-3x text-primary mb-3"),
                ], className="text-center"),
                html.H1("InvestAI", className="text-center mb-2", 
                       style={"fontWeight": "700", "color": "#1a1a2e"}),
                html.P(
                    "AI-Powered Portfolio Manager for Indonesian Stocks",
                    className="text-center text-muted mb-5"
                )
            ]),
            
            # Login card
            dbc.Card([
                dbc.CardHeader([
                    html.H4("Login to Your Account", className="mb-0")
                ], className="bg-primary text-white"),
                dbc.CardBody([
                    dbc.Input(
                        id="login-email",
                        type="email",
                        placeholder="Email address",
                        className="mb-3",
                        size="lg"
                    ),
                    dbc.Input(
                        id="login-password",
                        type="password",
                        placeholder="Password",
                        className="mb-4",
                        size="lg"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-sign-in-alt me-2"), "Login"],
                        id="login-btn",
                        color="primary",
                        className="w-100 mb-3",
                        size="lg"
                    ),
                    html.Div(id="login-error", className="text-danger text-center"),
                    html.Hr(className="my-4"),
                    html.P([
                        "Don't have an account? ",
                        dcc.Link("Sign up here", href="/register", className="text-primary fw-bold")
                    ], className="text-center mb-0")
                ])
            ], className="shadow", style={"maxWidth": "450px", "margin": "auto", "borderRadius": "10px"})
        ], width=12, lg=6, className="mx-auto")
    ], className="min-vh-100 d-flex align-items-center justify-content-center",
       style={"background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"})
], fluid=True, className="p-0")


@callback(
    [Output("url", "pathname", allow_duplicate=True),
     Output("login-error", "children"),
     Output("user-session", "data", allow_duplicate=True)],
    Input("login-btn", "n_clicks"),
    [State("login-email", "value"),
     State("login-password", "value")],
    prevent_initial_call=True
)
def handle_login(n_clicks, email, password):
    """Handle login form submission"""
    if not n_clicks:
        return dash.no_update, "", dash.no_update
    
    if not email or not password:
        return dash.no_update, "Please enter email and password", dash.no_update
    
    try:
        # Call backend API
        response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            data={"username": email, "password": password},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data['access_token']
            
            # Store in session
            session_data = {"token": token, "email": email}
            
            return "/dashboard", "", session_data
        else:
            error_msg = "Invalid email or password"
            try:
                error_detail = response.json().get('detail', error_msg)
                error_msg = error_detail
            except:
                pass
            return dash.no_update, error_msg, dash.no_update
            
    except requests.exceptions.ConnectionError:
        return dash.no_update, "Cannot connect to server. Please try again.", dash.no_update
    except Exception as e:
        return dash.no_update, f"Error: {str(e)}", dash.no_update
