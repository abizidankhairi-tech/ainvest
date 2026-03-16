import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Register page layout
register_layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Div([
                    html.I(className="fas fa-chart-line fa-3x text-primary mb-3"),
                ], className="text-center"),
                html.H1("InvestAI", className="text-center mb-2",
                       style={"fontWeight": "700", "color": "#1a1a2e"}),
                html.P(
                    "Create your account and start managing your portfolio",
                    className="text-center text-muted mb-5"
                )
            ]),
            
            dbc.Card([
                dbc.CardHeader([
                    html.H4("Create Account", className="mb-0")
                ], className="bg-success text-white"),
                dbc.CardBody([
                    dbc.Input(
                        id="register-name",
                        type="text",
                        placeholder="Full Name",
                        className="mb-3",
                        size="lg"
                    ),
                    dbc.Input(
                        id="register-email",
                        type="email",
                        placeholder="Email address",
                        className="mb-3",
                        size="lg"
                    ),
                    dbc.Input(
                        id="register-password",
                        type="password",
                        placeholder="Password (min 8 characters)",
                        className="mb-3",
                        size="lg"
                    ),
                    dbc.Input(
                        id="register-password-confirm",
                        type="password",
                        placeholder="Confirm Password",
                        className="mb-4",
                        size="lg"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-user-plus me-2"), "Create Account"],
                        id="register-btn",
                        color="success",
                        className="w-100 mb-3",
                        size="lg"
                    ),
                    html.Div(id="register-error", className="text-danger text-center"),
                    html.Div(id="register-success", className="text-success text-center"),
                    html.Hr(className="my-4"),
                    html.P([
                        "Already have an account? ",
                        dcc.Link("Login here", href="/login", className="text-success fw-bold")
                    ], className="text-center mb-0")
                ])
            ], className="shadow", style={"maxWidth": "450px", "margin": "auto", "borderRadius": "10px"})
        ], width=12, lg=6, className="mx-auto")
    ], className="min-vh-100 d-flex align-items-center justify-content-center",
       style={"background": "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)"})
], fluid=True, className="p-0")


@callback(
    [Output("url", "pathname", allow_duplicate=True),
     Output("register-error", "children"),
     Output("register-success", "children")],
    Input("register-btn", "n_clicks"),
    [State("register-name", "value"),
     State("register-email", "value"),
     State("register-password", "value"),
     State("register-password-confirm", "value")],
    prevent_initial_call=True
)
def handle_register(n_clicks, name, email, password, password_confirm):
    """Handle registration form submission"""
    if not n_clicks:
        return dash.no_update, "", ""
    
    # Validation
    if not all([name, email, password, password_confirm]):
        return dash.no_update, "Please fill all fields", ""
    
    if len(password) < 8:
        return dash.no_update, "Password must be at least 8 characters", ""
    
    if password != password_confirm:
        return dash.no_update, "Passwords do not match", ""
    
    try:
        # Call backend API
        response = requests.post(
            f"{BACKEND_URL}/api/auth/register",
            json={
                "email": email,
                "password": password,
                "full_name": name
            },
            timeout=10
        )
        
        if response.status_code == 201:
            return "/login", "", "Account created successfully! Please login."
        else:
            error_detail = response.json().get('detail', 'Registration failed')
            return dash.no_update, error_detail, ""
            
    except requests.exceptions.ConnectionError:
        return dash.no_update, "Cannot connect to server. Please try again.", ""
    except Exception as e:
        return dash.no_update, f"Error: {str(e)}", ""
