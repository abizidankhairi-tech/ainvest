import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def format_currency(value):
    """Format number as Indonesian Rupiah"""
    if value is None:
        return "Rp 0"
    return f"Rp {value:,.0f}".replace(",", ".")


def format_percentage(value):
    """Format number as percentage"""
    if value is None:
        return "0.00%"
    return f"{value:+.2f}%"


def create_navbar():
    """Create the navigation bar"""
    return dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand([
                html.I(className="fas fa-chart-line me-2"),
                "InvestAI"
            ], href="/dashboard", className="fw-bold"),
            dbc.NavbarToggler(id="navbar-toggler"),
            dbc.Collapse(
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink([
                        html.I(className="fas fa-tachometer-alt me-1"),
                        "Dashboard"
                    ], href="/dashboard", active=True)),
                    dbc.NavItem(dbc.NavLink([
                        html.I(className="fas fa-briefcase me-1"),
                        "Portfolio"
                    ], href="/portfolio")),
                    dbc.NavItem(dbc.NavLink([
                        html.I(className="fas fa-upload me-1"),
                        "Import"
                    ], href="/import")),
                    dbc.NavItem(dbc.NavLink([
                        html.I(className="fas fa-robot me-1"),
                        "AI Insights"
                    ], href="/ai")),
                    dbc.NavItem(dbc.NavLink([
                        html.I(className="fas fa-crosshairs me-1"),
                        "Strategies"
                    ], href="/strategies")),
                    dbc.NavItem(dbc.NavLink([
                        html.I(className="fas fa-bell me-1"),
                        "Alerts"
                    ], href="/alerts")),
                    dbc.DropdownMenu(
                        [
                            dbc.DropdownMenuItem([
                                html.I(className="fas fa-user me-2"),
                                "Profile"
                            ], href="/profile"),
                            dbc.DropdownMenuItem([
                                html.I(className="fas fa-cog me-2"),
                                "Settings"
                            ], href="/settings"),
                            dbc.DropdownMenuItem(divider=True),
                            dbc.DropdownMenuItem([
                                html.I(className="fas fa-sign-out-alt me-2"),
                                "Logout"
                            ], id="logout-btn")
                        ],
                        label="Account",
                        nav=True,
                        in_navbar=True
                    )
                ], className="ms-auto", navbar=True),
                id="navbar-collapse",
                navbar=True
            )
        ], fluid=True),
        color="dark",
        dark=True,
        className="mb-4",
        sticky="top"
    )


# Dashboard layout
dashboard_layout = html.Div([
    create_navbar(),
    
    dbc.Container([
        # Welcome section
        dbc.Row([
            dbc.Col([
                html.H2("Dashboard", className="mb-1"),
                html.P(id="welcome-message", className="text-muted")
            ])
        ], className="mb-4"),
        
        # Statistics cards
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H6("Total Value", className="text-muted mb-1"),
                                html.H4(id="dash-total-value", className="mb-0 fw-bold text-primary")
                            ], width=8),
                            dbc.Col([
                                html.Div([
                                    html.I(className="fas fa-wallet fa-2x text-primary")
                                ], className="text-end")
                            ], width=4)
                        ])
                    ])
                ], className="shadow-sm h-100")
            ], width=12, md=6, lg=3, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H6("Gain/Loss", className="text-muted mb-1"),
                                html.H4(id="dash-gain-loss", className="mb-0 fw-bold")
                            ], width=8),
                            dbc.Col([
                                html.Div([
                                    html.I(className="fas fa-chart-line fa-2x text-success")
                                ], className="text-end")
                            ], width=4)
                        ])
                    ])
                ], className="shadow-sm h-100")
            ], width=12, md=6, lg=3, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H6("Holdings", className="text-muted mb-1"),
                                html.H4(id="dash-holdings-count", className="mb-0 fw-bold")
                            ], width=8),
                            dbc.Col([
                                html.Div([
                                    html.I(className="fas fa-layer-group fa-2x text-info")
                                ], className="text-end")
                            ], width=4)
                        ])
                    ])
                ], className="shadow-sm h-100")
            ], width=12, md=6, lg=3, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H6("Return %", className="text-muted mb-1"),
                                html.H4(id="dash-return-pct", className="mb-0 fw-bold")
                            ], width=8),
                            dbc.Col([
                                html.Div([
                                    html.I(className="fas fa-percentage fa-2x text-warning")
                                ], className="text-end")
                            ], width=4)
                        ])
                    ])
                ], className="shadow-sm h-100")
            ], width=12, md=6, lg=3, className="mb-3"),
        ]),
        
        # Quick actions
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([
                            html.I(className="fas fa-bolt me-2"),
                            "Quick Actions"
                        ], className="mb-0")
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Button([
                                    html.I(className="fas fa-camera me-2"),
                                    "Import from Screenshot"
                                ], color="primary", className="w-100 mb-2", href="/import")
                            ], width=12, md=4),
                            dbc.Col([
                                dbc.Button([
                                    html.I(className="fas fa-plus me-2"),
                                    "Add Holding"
                                ], color="success", outline=True, className="w-100 mb-2", href="/portfolio")
                            ], width=12, md=4),
                            dbc.Col([
                                dbc.Button([
                                    html.I(className="fas fa-comments me-2"),
                                    "Ask AI"
                                ], color="info", outline=True, className="w-100 mb-2", href="/ai")
                            ], width=12, md=4),
                        ])
                    ])
                ], className="shadow-sm")
            ])
        ], className="mb-4"),
        
        # Main content area
        dbc.Row([
            # Portfolio overview
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        dbc.Row([
                            dbc.Col([
                                html.H5([
                                    html.I(className="fas fa-briefcase me-2"),
                                    "Top Holdings"
                                ], className="mb-0")
                            ]),
                            dbc.Col([
                                dbc.Button("View All", href="/portfolio", color="link", size="sm", className="float-end")
                            ])
                        ])
                    ]),
                    dbc.CardBody([
                        html.Div(id="dash-top-holdings")
                    ])
                ], className="shadow-sm h-100")
            ], width=12, lg=8, className="mb-4"),
            
            # AI Insights sidebar
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([
                            html.I(className="fas fa-robot me-2"),
                            "AI Insights"
                        ], className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.Div(id="dash-ai-insights", children=[
                            html.P("No AI insights available yet.", className="text-muted mb-2"),
                            html.Small("Add holdings to get personalized recommendations.", className="text-muted"),
                            html.Hr(),
                            dbc.Button([
                                html.I(className="fas fa-robot me-2"),
                                "Get AI Analysis"
                            ], color="info", outline=True, className="w-100", href="/ai")
                        ])
                    ])
                ], className="shadow-sm h-100")
            ], width=12, lg=4, className="mb-4"),
        ]),
        
        # Recent activity
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([
                            html.I(className="fas fa-history me-2"),
                            "Recent Transactions"
                        ], className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.Div(id="dash-recent-activity")
                    ])
                ], className="shadow-sm")
            ])
        ], className="mb-4"),
        
    ], fluid=True),
    
    # Footer
    html.Footer([
        dbc.Container([
            html.Hr(),
            html.P([
                "InvestAI - AI-Powered Portfolio Manager | ",
                html.A("Privacy", href="#", className="text-muted"),
                " | ",
                html.A("Terms", href="#", className="text-muted"),
            ], className="text-center text-muted small")
        ], fluid=True)
    ]),
    
    # Refresh interval (every 5 minutes)
    dcc.Interval(id="dash-interval-refresh", interval=5*60*1000, n_intervals=0)
])


# Load dashboard data
@callback(
    [Output("welcome-message", "children"),
     Output("dash-total-value", "children"),
     Output("dash-gain-loss", "children"),
     Output("dash-gain-loss", "className"),
     Output("dash-holdings-count", "children"),
     Output("dash-return-pct", "children"),
     Output("dash-return-pct", "className"),
     Output("dash-top-holdings", "children"),
     Output("dash-recent-activity", "children")],
    [Input("dash-interval-refresh", "n_intervals")],
    [State("user-session", "data")],
    prevent_initial_call=False
)
def load_dashboard_data(n_intervals, session):
    """Load all dashboard data"""
    default_welcome = "Welcome to your AI-powered portfolio manager"
    default_holdings = dbc.Alert([
        html.I(className="fas fa-info-circle me-2"),
        "No holdings yet. ",
        dcc.Link("Add your first holding", href="/portfolio", className="alert-link"),
        " or ",
        dcc.Link("import from screenshot", href="/import", className="alert-link"),
        "."
    ], color="info", className="mb-0")
    default_activity = html.P("No recent transactions.", className="text-muted mb-0")
    
    if not session or 'token' not in session:
        return (
            default_welcome,
            "Rp 0", "Rp 0", "mb-0 fw-bold", "0",
            "0.00%", "mb-0 fw-bold",
            default_holdings, default_activity
        )
    
    token = session['token']
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get user info
        user_resp = requests.get(f"{BACKEND_URL}/api/auth/me", headers=headers, timeout=10)
        welcome_msg = default_welcome
        if user_resp.status_code == 200:
            user = user_resp.json()
            name = user.get('full_name', '').split()[0] if user.get('full_name') else 'there'
            welcome_msg = f"Welcome back, {name}! Here's your portfolio overview."
        
        # Get portfolios
        portfolios_resp = requests.get(f"{BACKEND_URL}/api/portfolios/", headers=headers, timeout=10)
        
        if portfolios_resp.status_code != 200 or not portfolios_resp.json():
            return (
                welcome_msg,
                "Rp 0", "Rp 0", "mb-0 fw-bold", "0",
                "0.00%", "mb-0 fw-bold",
                default_holdings, default_activity
            )
        
        portfolio = portfolios_resp.json()[0]
        portfolio_id = portfolio['id']
        
        # Get holdings
        holdings_resp = requests.get(
            f"{BACKEND_URL}/api/portfolios/{portfolio_id}/holdings/",
            headers=headers,
            timeout=10
        )
        
        if holdings_resp.status_code != 200:
            return (
                welcome_msg,
                "Rp 0", "Rp 0", "mb-0 fw-bold", "0",
                "0.00%", "mb-0 fw-bold",
                default_holdings, default_activity
            )
        
        holdings = holdings_resp.json()
        
        if not holdings:
            return (
                welcome_msg,
                "Rp 0", "Rp 0", "mb-0 fw-bold", "0",
                "0.00%", "mb-0 fw-bold",
                default_holdings, default_activity
            )
        
        # Get current prices
        symbols = [h['symbol'] for h in holdings]
        prices_resp = requests.get(
            f"{BACKEND_URL}/api/stocks/prices?symbols={','.join(symbols)}",
            headers=headers,
            timeout=30
        )
        
        prices = {}
        if prices_resp.status_code == 200:
            prices = prices_resp.json().get('prices', {})
        
        # Calculate values
        total_value = 0
        total_cost = 0
        holdings_data = []
        
        for h in holdings:
            symbol = h['symbol']
            shares = h['shares']
            avg_cost = float(h['avg_cost'])
            cost = shares * avg_cost
            
            current_price = avg_cost
            if symbol in prices:
                current_price = prices[symbol].get('price', avg_cost)
            
            market_value = shares * current_price
            gain_loss = market_value - cost
            gain_loss_pct = (gain_loss / cost * 100) if cost > 0 else 0
            
            total_value += market_value
            total_cost += cost
            
            holdings_data.append({
                'symbol': symbol,
                'shares': shares,
                'market_value': market_value,
                'gain_loss': gain_loss,
                'gain_loss_pct': gain_loss_pct
            })
        
        total_gain_loss = total_value - total_cost
        total_return_pct = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0
        
        gain_loss_class = f"mb-0 fw-bold {'text-success' if total_gain_loss >= 0 else 'text-danger'}"
        return_class = f"mb-0 fw-bold {'text-success' if total_return_pct >= 0 else 'text-danger'}"
        
        # Build top holdings table (top 5 by value)
        holdings_data.sort(key=lambda x: x['market_value'], reverse=True)
        top_holdings = holdings_data[:5]
        
        holdings_table = dbc.Table([
            html.Thead([
                html.Tr([
                    html.Th("Symbol"),
                    html.Th("Shares", className="text-end"),
                    html.Th("Value", className="text-end"),
                    html.Th("Gain/Loss", className="text-end")
                ])
            ]),
            html.Tbody([
                html.Tr([
                    html.Td(html.Strong(h['symbol'])),
                    html.Td(f"{h['shares']:,}", className="text-end"),
                    html.Td(format_currency(h['market_value']), className="text-end"),
                    html.Td([
                        html.Span(
                            format_percentage(h['gain_loss_pct']),
                            className=f"{'text-success' if h['gain_loss_pct'] >= 0 else 'text-danger'}"
                        )
                    ], className="text-end")
                ]) for h in top_holdings
            ])
        ], striped=True, hover=True, size="sm", className="mb-0")
        
        # Get recent transactions
        tx_resp = requests.get(
            f"{BACKEND_URL}/api/portfolios/{portfolio_id}/holdings/transactions",
            headers=headers,
            timeout=10
        )
        
        activity_content = default_activity
        if tx_resp.status_code == 200:
            transactions = tx_resp.json()
            if transactions:
                tx_items = []
                for tx in transactions[:5]:
                    tx_type = tx['transaction_type']
                    is_buy = tx_type == 'BUY'
                    tx_items.append(
                        html.Div([
                            html.Span(
                                tx_type,
                                className=f"badge {'bg-success' if is_buy else 'bg-danger'} me-2"
                            ),
                            html.Strong(tx['symbol']),
                            html.Span(f" - {tx['shares']} shares @ {format_currency(tx['price'])}"),
                            html.Small(f" ({tx['transaction_date']})", className="text-muted float-end")
                        ], className="mb-2 pb-2 border-bottom")
                    )
                activity_content = html.Div(tx_items)
        
        return (
            welcome_msg,
            format_currency(total_value),
            format_currency(total_gain_loss),
            gain_loss_class,
            str(len(holdings)),
            format_percentage(total_return_pct),
            return_class,
            holdings_table,
            activity_content
        )
        
    except Exception as e:
        return (
            default_welcome,
            "Rp 0", "Rp 0", "mb-0 fw-bold", "0",
            "0.00%", "mb-0 fw-bold",
            html.P(f"Error loading data: {str(e)}", className="text-danger"),
            default_activity
        )


# Logout callback
@callback(
    [Output("url", "pathname", allow_duplicate=True),
     Output("user-session", "data", allow_duplicate=True)],
    Input("logout-btn", "n_clicks"),
    prevent_initial_call=True
)
def handle_logout(n_clicks):
    """Handle logout"""
    if n_clicks:
        return "/login", None
    return dash.no_update, dash.no_update


# Toggle navbar collapse for mobile
@callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
