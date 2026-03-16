import dash
from dash import html, dcc, Input, Output, State, callback, dash_table, ALL, MATCH, ctx
import dash_bootstrap_components as dbc
import requests
import os
import json

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def format_currency(value):
    """Format number as Indonesian Rupiah"""
    if value is None:
        return "Rp 0"
    return f"Rp {value:,.0f}".replace(",", ".")


def format_percentage(value):
    """Format number as percentage with color"""
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
            dbc.NavbarToggler(id="navbar-toggler-portfolio"),
            dbc.Collapse(
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink([
                        html.I(className="fas fa-tachometer-alt me-1"),
                        "Dashboard"
                    ], href="/dashboard")),
                    dbc.NavItem(dbc.NavLink([
                        html.I(className="fas fa-briefcase me-1"),
                        "Portfolio"
                    ], href="/portfolio", active=True)),
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
                            ], id="logout-btn-portfolio")
                        ],
                        label="Account",
                        nav=True,
                        in_navbar=True
                    )
                ], className="ms-auto", navbar=True),
                id="navbar-collapse-portfolio",
                navbar=True
            )
        ], fluid=True),
        color="dark",
        dark=True,
        className="mb-4",
        sticky="top"
    )


def create_add_holding_modal():
    """Create modal for adding/editing holdings"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(id="holding-modal-title")),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Stock Symbol", html_for="input-symbol"),
                        dbc.InputGroup([
                            dbc.Input(
                                id="input-symbol",
                                type="text",
                                placeholder="e.g., BBCA",
                                maxLength=10
                            ),
                            dbc.Button(
                                html.I(className="fas fa-search"),
                                id="btn-search-stock",
                                color="secondary"
                            )
                        ]),
                        html.Div(id="symbol-search-results", className="mt-2")
                    ], width=12, className="mb-3"),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Number of Shares", html_for="input-shares"),
                        dbc.Input(
                            id="input-shares",
                            type="number",
                            placeholder="e.g., 100",
                            min=1
                        )
                    ], width=6, className="mb-3"),
                    dbc.Col([
                        dbc.Label("Average Cost (Rp)", html_for="input-avg-cost"),
                        dbc.Input(
                            id="input-avg-cost",
                            type="number",
                            placeholder="e.g., 8500",
                            min=1
                        )
                    ], width=6, className="mb-3"),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Sector (Optional)", html_for="input-sector"),
                        dbc.Select(
                            id="input-sector",
                            options=[
                                {"label": "-- Select Sector --", "value": ""},
                                {"label": "Finance", "value": "Finance"},
                                {"label": "Consumer Goods", "value": "Consumer Goods"},
                                {"label": "Infrastructure", "value": "Infrastructure"},
                                {"label": "Mining", "value": "Mining"},
                                {"label": "Technology", "value": "Technology"},
                                {"label": "Healthcare", "value": "Healthcare"},
                                {"label": "Property", "value": "Property"},
                                {"label": "Trade & Services", "value": "Trade & Services"},
                                {"label": "Basic Industry", "value": "Basic Industry"},
                                {"label": "Agriculture", "value": "Agriculture"},
                            ]
                        )
                    ], width=12, className="mb-3"),
                ]),
                html.Div(id="holding-form-error", className="text-danger mb-3"),
                dcc.Store(id="editing-holding-id", data=None)
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="btn-cancel-holding", color="secondary", className="me-2"),
            dbc.Button("Save Holding", id="btn-save-holding", color="primary")
        ])
    ], id="modal-add-holding", is_open=False, size="lg")


def create_transaction_modal():
    """Create modal for recording transactions"""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Record Transaction")),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Transaction Type"),
                        dbc.RadioItems(
                            id="input-tx-type",
                            options=[
                                {"label": "Buy", "value": "BUY"},
                                {"label": "Sell", "value": "SELL"}
                            ],
                            value="BUY",
                            inline=True
                        )
                    ], width=12, className="mb-3"),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Stock Symbol"),
                        dbc.Input(id="input-tx-symbol", type="text", placeholder="e.g., BBCA")
                    ], width=6, className="mb-3"),
                    dbc.Col([
                        dbc.Label("Transaction Date"),
                        dbc.Input(id="input-tx-date", type="date")
                    ], width=6, className="mb-3"),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Shares"),
                        dbc.Input(id="input-tx-shares", type="number", min=1)
                    ], width=4, className="mb-3"),
                    dbc.Col([
                        dbc.Label("Price per Share (Rp)"),
                        dbc.Input(id="input-tx-price", type="number", min=1)
                    ], width=4, className="mb-3"),
                    dbc.Col([
                        dbc.Label("Fees (Rp)"),
                        dbc.Input(id="input-tx-fees", type="number", min=0, value=0)
                    ], width=4, className="mb-3"),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Notes (Optional)"),
                        dbc.Textarea(id="input-tx-notes", placeholder="Add notes...")
                    ], width=12, className="mb-3"),
                ]),
                html.Div(id="tx-form-error", className="text-danger mb-3"),
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="btn-cancel-tx", color="secondary", className="me-2"),
            dbc.Button("Record Transaction", id="btn-save-tx", color="success")
        ])
    ], id="modal-transaction", is_open=False, size="lg")


# Portfolio page layout
portfolio_layout = html.Div([
    create_navbar(),
    
    dbc.Container([
        # Page header - mobile optimized
        dbc.Row([
            dbc.Col([
                html.H4("My Portfolio", className="mb-0 mb-md-1"),
                html.Small("Manage holdings and track performance", className="text-muted d-none d-md-block")
            ], width=12, md=6, className="mb-2 mb-md-0"),
            dbc.Col([
                html.Div([
                    dbc.Button([
                        html.I(className="fas fa-camera"),
                        html.Span(" Import", className="d-none d-sm-inline")
                    ], color="primary", size="sm", className="me-1", id="btn-import-ss"),
                    dbc.Button([
                        html.I(className="fas fa-plus"),
                        html.Span(" Add", className="d-none d-sm-inline")
                    ], color="success", size="sm", className="me-1", id="btn-add-holding-open"),
                    dbc.Button([
                        html.I(className="fas fa-exchange-alt"),
                        html.Span(" Transaction", className="d-none d-md-inline")
                    ], color="info", size="sm", id="btn-record-tx-open"),
                ], className="text-end text-md-end")
            ], width=12, md=6, className="mb-2")
        ], className="mb-3 align-items-center"),
        
        # Portfolio summary cards - mobile optimized
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Small("Total Value", className="text-muted d-block"),
                        html.H4(id="summary-total-value", className="mb-0 fw-bold text-primary", 
                               style={"fontSize": "clamp(1rem, 4vw, 1.5rem)"})
                    ], className="py-2 px-3")
                ], className="shadow-sm h-100")
            ], width=6, lg=3, className="mb-2 px-1 px-sm-2"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Small("Total Cost", className="text-muted d-block"),
                        html.H4(id="summary-total-cost", className="mb-0 fw-bold",
                               style={"fontSize": "clamp(1rem, 4vw, 1.5rem)"})
                    ], className="py-2 px-3")
                ], className="shadow-sm h-100")
            ], width=6, lg=3, className="mb-2 px-1 px-sm-2"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Small("Gain/Loss", className="text-muted d-block"),
                        html.H4(id="summary-gain-loss", className="mb-0 fw-bold",
                               style={"fontSize": "clamp(1rem, 4vw, 1.5rem)"})
                    ], className="py-2 px-3")
                ], className="shadow-sm h-100")
            ], width=6, lg=3, className="mb-2 px-1 px-sm-2"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Small("Return %", className="text-muted d-block"),
                        html.H4(id="summary-return-pct", className="mb-0 fw-bold",
                               style={"fontSize": "clamp(1rem, 4vw, 1.5rem)"})
                    ], className="py-2 px-3")
                ], className="shadow-sm h-100")
            ], width=6, lg=3, className="mb-2 px-1 px-sm-2"),
        ], className="g-2"),
        
        # Holdings table
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        dbc.Row([
                            dbc.Col([
                                html.H5([
                                    html.I(className="fas fa-layer-group me-2"),
                                    "Holdings"
                                ], className="mb-0")
                            ]),
                            dbc.Col([
                                dbc.Button([
                                    html.I(className="fas fa-sync-alt me-1"),
                                    "Refresh Prices"
                                ], id="btn-refresh-prices", color="link", size="sm", className="float-end")
                            ])
                        ])
                    ]),
                    dbc.CardBody([
                        dbc.Spinner([
                            html.Div(id="holdings-table-container")
                        ], color="primary")
                    ])
                ], className="shadow-sm")
            ])
        ], className="mb-4"),
        
        # Recent transactions
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
                        html.Div(id="transactions-container")
                    ])
                ], className="shadow-sm")
            ])
        ], className="mb-4"),
        
    ], fluid=True),
    
    # Modals
    create_add_holding_modal(),
    create_transaction_modal(),
    
    # Data refresh interval (every 5 minutes)
    dcc.Interval(id="interval-refresh", interval=5*60*1000, n_intervals=0),
    
    # Store for portfolio data
    dcc.Store(id="store-portfolio-id", data=None),
    dcc.Store(id="store-holdings-data", data=[]),
])


# Callbacks

@callback(
    Output("modal-add-holding", "is_open"),
    Output("holding-modal-title", "children"),
    Output("input-symbol", "value"),
    Output("input-shares", "value"),
    Output("input-avg-cost", "value"),
    Output("input-sector", "value"),
    Output("editing-holding-id", "data"),
    [Input("btn-add-holding-open", "n_clicks"),
     Input("btn-cancel-holding", "n_clicks"),
     Input("btn-save-holding", "n_clicks")],
    [State("modal-add-holding", "is_open")],
    prevent_initial_call=True
)
def toggle_add_holding_modal(n_open, n_cancel, n_save, is_open):
    """Toggle the add holding modal"""
    triggered = ctx.triggered_id
    
    if triggered == "btn-add-holding-open":
        return True, "Add New Holding", "", None, None, "", None
    elif triggered in ["btn-cancel-holding", "btn-save-holding"]:
        return False, "", "", None, None, "", None
    
    return is_open, "Add New Holding", "", None, None, "", None


@callback(
    Output("modal-transaction", "is_open"),
    [Input("btn-record-tx-open", "n_clicks"),
     Input("btn-cancel-tx", "n_clicks"),
     Input("btn-save-tx", "n_clicks")],
    [State("modal-transaction", "is_open")],
    prevent_initial_call=True
)
def toggle_transaction_modal(n_open, n_cancel, n_save, is_open):
    """Toggle the transaction modal"""
    triggered = ctx.triggered_id
    
    if triggered == "btn-record-tx-open":
        return True
    elif triggered in ["btn-cancel-tx", "btn-save-tx"]:
        return False
    
    return is_open


@callback(
    [Output("holdings-table-container", "children"),
     Output("summary-total-value", "children"),
     Output("summary-total-cost", "children"),
     Output("summary-gain-loss", "children"),
     Output("summary-gain-loss", "className"),
     Output("summary-return-pct", "children"),
     Output("summary-return-pct", "className"),
     Output("store-holdings-data", "data")],
    [Input("interval-refresh", "n_intervals"),
     Input("btn-refresh-prices", "n_clicks"),
     Input("btn-save-holding", "n_clicks")],
    [State("user-session", "data"),
     State("store-portfolio-id", "data")],
    prevent_initial_call=False
)
def load_holdings(n_intervals, n_refresh, n_save, session, portfolio_id):
    """Load holdings and calculate portfolio summary"""
    
    if not session or 'token' not in session:
        return (
            dbc.Alert("Please login to view your portfolio", color="warning"),
            "Rp 0", "Rp 0", "Rp 0", "mb-0 fw-bold", "0.00%", "mb-0 fw-bold", []
        )
    
    token = session['token']
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get or create portfolio
        portfolios_resp = requests.get(
            f"{BACKEND_URL}/api/portfolios/",
            headers=headers,
            timeout=10
        )
        
        if portfolios_resp.status_code != 200:
            return (
                dbc.Alert("Error loading portfolio", color="danger"),
                "Rp 0", "Rp 0", "Rp 0", "mb-0 fw-bold", "0.00%", "mb-0 fw-bold", []
            )
        
        portfolios = portfolios_resp.json()
        
        if not portfolios:
            # Create default portfolio
            create_resp = requests.post(
                f"{BACKEND_URL}/api/portfolios/",
                headers=headers,
                json={"name": "My Portfolio", "description": "Default portfolio"},
                timeout=10
            )
            if create_resp.status_code == 201:
                portfolio = create_resp.json()
            else:
                return (
                    dbc.Alert("Error creating portfolio", color="danger"),
                    "Rp 0", "Rp 0", "Rp 0", "mb-0 fw-bold", "0.00%", "mb-0 fw-bold", []
                )
        else:
            portfolio = portfolios[0]
        
        portfolio_id = portfolio['id']
        
        # Get holdings
        holdings_resp = requests.get(
            f"{BACKEND_URL}/api/portfolios/{portfolio_id}/holdings/",
            headers=headers,
            timeout=10
        )
        
        if holdings_resp.status_code != 200:
            return (
                dbc.Alert("Error loading holdings", color="danger"),
                "Rp 0", "Rp 0", "Rp 0", "mb-0 fw-bold", "0.00%", "mb-0 fw-bold", []
            )
        
        holdings = holdings_resp.json()
        
        if not holdings:
            empty_msg = dbc.Alert([
                html.I(className="fas fa-info-circle me-2"),
                "No holdings yet. Click 'Add Holding' to add your first stock."
            ], color="info")
            return empty_msg, "Rp 0", "Rp 0", "Rp 0", "mb-0 fw-bold", "0.00%", "mb-0 fw-bold", []
        
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
        table_data = []
        
        for h in holdings:
            symbol = h['symbol']
            shares = h['shares']
            avg_cost = float(h['avg_cost'])
            cost = shares * avg_cost
            
            current_price = avg_cost  # Default to avg cost
            change_pct = 0
            
            if symbol in prices:
                current_price = prices[symbol].get('price', avg_cost)
                change_pct = prices[symbol].get('change_pct', 0)
            
            market_value = shares * current_price
            gain_loss = market_value - cost
            gain_loss_pct = (gain_loss / cost * 100) if cost > 0 else 0
            
            total_value += market_value
            total_cost += cost
            
            table_data.append({
                'id': h['id'],
                'symbol': symbol,
                'shares': shares,
                'avg_cost': avg_cost,
                'current_price': current_price,
                'market_value': market_value,
                'cost': cost,
                'gain_loss': gain_loss,
                'gain_loss_pct': gain_loss_pct,
                'day_change_pct': change_pct,
                'sector': h.get('sector', '-')
            })
        
        total_gain_loss = total_value - total_cost
        total_return_pct = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0
        
        # Build table - mobile optimized
        table = html.Div([
            dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th("Stock", style={"minWidth": "80px"}),
                        html.Th("Shares", className="text-end d-none d-md-table-cell"),
                        html.Th("Avg", className="text-end d-none d-lg-table-cell"),
                        html.Th("Price", className="text-end"),
                        html.Th("Value", className="text-end d-none d-sm-table-cell"),
                        html.Th("P/L", className="text-end"),
                        html.Th("%", className="text-end"),
                        html.Th("", className="text-center", style={"width": "70px"})
                    ])
                ]),
                html.Tbody([
                    html.Tr([
                        # Symbol + Shares (mobile compact)
                        html.Td([
                            html.Div([
                                html.Strong(row['symbol'], className="d-block"),
                                html.Small(f"{row['shares']:,} lot", className="text-muted d-md-none"),
                                html.Small(row['sector'], className="text-muted d-none d-md-block")
                            ])
                        ]),
                        # Shares (hidden on mobile)
                        html.Td(f"{row['shares']:,}", className="text-end d-none d-md-table-cell"),
                        # Avg Cost (hidden on tablet)
                        html.Td(format_currency(row['avg_cost']), className="text-end d-none d-lg-table-cell"),
                        # Current Price
                        html.Td([
                            html.Span(format_currency(row['current_price'])),
                            html.Small(
                                f" ({row['day_change_pct']:+.1f}%)",
                                className=f"d-none d-sm-inline {'text-success' if row['day_change_pct'] >= 0 else 'text-danger'}"
                            )
                        ], className="text-end"),
                        # Market Value (hidden on xs)
                        html.Td(format_currency(row['market_value']), className="text-end fw-bold d-none d-sm-table-cell"),
                        # Gain/Loss
                        html.Td([
                            html.Span(
                                format_currency(row['gain_loss']),
                                className=f"{'text-success' if row['gain_loss'] >= 0 else 'text-danger'}"
                            )
                        ], className="text-end"),
                        # Return %
                        html.Td(
                            format_percentage(row['gain_loss_pct']),
                            className=f"text-end fw-bold {'text-success' if row['gain_loss_pct'] >= 0 else 'text-danger'}"
                        ),
                        # Actions
                        html.Td([
                            dbc.ButtonGroup([
                                dbc.Button(
                                    html.I(className="fas fa-edit"),
                                    color="warning",
                                    size="sm",
                                    id={"type": "btn-edit-holding", "index": row['id']},
                                    className="px-2"
                                ),
                                dbc.Button(
                                    html.I(className="fas fa-trash"),
                                    color="danger",
                                    size="sm",
                                    id={"type": "btn-delete-holding", "index": row['id']},
                                    className="px-2"
                                )
                            ], size="sm")
                        ], className="text-center")
                    ]) for row in table_data
                ])
            ], striped=True, hover=True, responsive=True, className="mb-0 table-sm")
        ], className="table-responsive")
        
        # Format summary values
        gain_loss_class = f"mb-0 fw-bold {'text-success' if total_gain_loss >= 0 else 'text-danger'}"
        return_class = f"mb-0 fw-bold {'text-success' if total_return_pct >= 0 else 'text-danger'}"
        
        return (
            table,
            format_currency(total_value),
            format_currency(total_cost),
            format_currency(total_gain_loss),
            gain_loss_class,
            format_percentage(total_return_pct),
            return_class,
            table_data
        )
        
    except requests.exceptions.ConnectionError:
        return (
            dbc.Alert("Cannot connect to server", color="danger"),
            "Rp 0", "Rp 0", "Rp 0", "mb-0 fw-bold", "0.00%", "mb-0 fw-bold", []
        )
    except Exception as e:
        return (
            dbc.Alert(f"Error: {str(e)}", color="danger"),
            "Rp 0", "Rp 0", "Rp 0", "mb-0 fw-bold", "0.00%", "mb-0 fw-bold", []
        )


@callback(
    Output("holding-form-error", "children"),
    Input("btn-save-holding", "n_clicks"),
    [State("input-symbol", "value"),
     State("input-shares", "value"),
     State("input-avg-cost", "value"),
     State("input-sector", "value"),
     State("user-session", "data"),
     State("editing-holding-id", "data")],
    prevent_initial_call=True
)
def save_holding(n_clicks, symbol, shares, avg_cost, sector, session, editing_id):
    """Save a new holding or update existing"""
    if not n_clicks:
        return ""
    
    if not symbol or not shares or not avg_cost:
        return "Please fill in Symbol, Shares, and Average Cost"
    
    if not session or 'token' not in session:
        return "Please login first"
    
    token = session['token']
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get portfolio ID
        portfolios_resp = requests.get(
            f"{BACKEND_URL}/api/portfolios/",
            headers=headers,
            timeout=10
        )
        
        if portfolios_resp.status_code != 200 or not portfolios_resp.json():
            return "Portfolio not found"
        
        portfolio_id = portfolios_resp.json()[0]['id']
        
        # Create holding
        holding_data = {
            "symbol": symbol.upper(),
            "shares": int(shares),
            "avg_cost": float(avg_cost),
            "sector": sector if sector else None
        }
        
        resp = requests.post(
            f"{BACKEND_URL}/api/portfolios/{portfolio_id}/holdings/",
            headers=headers,
            json=holding_data,
            timeout=10
        )
        
        if resp.status_code == 201:
            return ""  # Success, modal will close
        else:
            error = resp.json().get('detail', 'Error saving holding')
            return error
            
    except Exception as e:
        return f"Error: {str(e)}"


@callback(
    Output("transactions-container", "children"),
    [Input("interval-refresh", "n_intervals"),
     Input("btn-save-tx", "n_clicks")],
    [State("user-session", "data")],
    prevent_initial_call=False
)
def load_transactions(n_intervals, n_save, session):
    """Load recent transactions"""
    if not session or 'token' not in session:
        return html.P("Please login to view transactions", className="text-muted")
    
    token = session['token']
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get portfolio
        portfolios_resp = requests.get(
            f"{BACKEND_URL}/api/portfolios/",
            headers=headers,
            timeout=10
        )
        
        if portfolios_resp.status_code != 200 or not portfolios_resp.json():
            return html.P("No portfolio found", className="text-muted")
        
        portfolio_id = portfolios_resp.json()[0]['id']
        
        # Get transactions
        tx_resp = requests.get(
            f"{BACKEND_URL}/api/portfolios/{portfolio_id}/holdings/transactions",
            headers=headers,
            timeout=10
        )
        
        if tx_resp.status_code != 200:
            return html.P("Error loading transactions", className="text-muted")
        
        transactions = tx_resp.json()
        
        if not transactions:
            return html.P("No transactions yet", className="text-muted")
        
        # Build transactions list (last 10)
        tx_items = []
        for tx in transactions[:10]:
            tx_type = tx['transaction_type']
            is_buy = tx_type == 'BUY'
            
            tx_items.append(
                dbc.ListGroupItem([
                    dbc.Row([
                        dbc.Col([
                            html.Span(
                                tx_type,
                                className=f"badge {'bg-success' if is_buy else 'bg-danger'} me-2"
                            ),
                            html.Strong(tx['symbol']),
                            html.Small(f" - {tx['transaction_date']}", className="text-muted")
                        ], width=4),
                        dbc.Col([
                            html.Span(f"{tx['shares']} shares @ {format_currency(tx['price'])}")
                        ], width=4),
                        dbc.Col([
                            html.Strong(format_currency(tx['total_amount']))
                        ], width=4, className="text-end")
                    ])
                ])
            )
        
        return dbc.ListGroup(tx_items, flush=True)
        
    except Exception as e:
        return html.P(f"Error: {str(e)}", className="text-danger")


# Edit holding callback
@callback(
    [Output("modal-add-holding", "is_open", allow_duplicate=True),
     Output("holding-modal-title", "children", allow_duplicate=True),
     Output("input-symbol", "value", allow_duplicate=True),
     Output("input-shares", "value", allow_duplicate=True),
     Output("input-avg-cost", "value", allow_duplicate=True),
     Output("input-sector", "value", allow_duplicate=True),
     Output("editing-holding-id", "data", allow_duplicate=True)],
    Input({"type": "btn-edit-holding", "index": ALL}, "n_clicks"),
    [State("store-holdings-data", "data"),
     State("user-session", "data")],
    prevent_initial_call=True
)
def handle_edit_holding(n_clicks_list, holdings_data, session):
    """Handle edit button click"""
    if not any(n_clicks_list):
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    # Find which button was clicked
    triggered = ctx.triggered_id
    if not triggered or not isinstance(triggered, dict):
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    holding_id = triggered.get('index')
    
    # Find the holding data
    holding = None
    for h in holdings_data:
        if h['id'] == holding_id:
            holding = h
            break
    
    if not holding:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    return (
        True,  # Open modal
        f"Edit {holding['symbol']}",
        holding['symbol'],
        holding['shares'],
        holding['avg_cost'],
        holding.get('sector', ''),
        holding_id
    )


# Delete holding callback
@callback(
    Output("holdings-table-container", "children", allow_duplicate=True),
    Input({"type": "btn-delete-holding", "index": ALL}, "n_clicks"),
    [State("user-session", "data"),
     State("store-holdings-data", "data")],
    prevent_initial_call=True
)
def handle_delete_holding(n_clicks_list, session, holdings_data):
    """Handle delete button click"""
    if not any(n_clicks_list):
        return dash.no_update
    
    if not session or 'token' not in session:
        return dbc.Alert("Please login first", color="warning")
    
    # Find which button was clicked
    triggered = ctx.triggered_id
    if not triggered or not isinstance(triggered, dict):
        return dash.no_update
    
    holding_id = triggered.get('index')
    
    token = session['token']
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get portfolio ID first
        portfolios_resp = requests.get(
            f"{BACKEND_URL}/api/portfolios/",
            headers=headers,
            timeout=10
        )
        
        if portfolios_resp.status_code != 200 or not portfolios_resp.json():
            return dbc.Alert("Portfolio not found", color="danger")
        
        portfolio_id = portfolios_resp.json()[0]['id']
        
        # Delete the holding
        resp = requests.delete(
            f"{BACKEND_URL}/api/portfolios/{portfolio_id}/holdings/{holding_id}",
            headers=headers,
            timeout=10
        )
        
        if resp.status_code == 204:
            # Refresh will happen via interval, return loading indicator
            return dbc.Spinner(
                html.Div("Refreshing...", className="text-muted text-center py-3"),
                color="primary"
            )
        else:
            return dbc.Alert(f"Error deleting holding: {resp.text}", color="danger")
            
    except Exception as e:
        return dbc.Alert(f"Error: {str(e)}", color="danger")


# Update holding (when editing)
@callback(
    Output("holding-form-error", "children", allow_duplicate=True),
    Input("btn-save-holding", "n_clicks"),
    [State("input-symbol", "value"),
     State("input-shares", "value"),
     State("input-avg-cost", "value"),
     State("input-sector", "value"),
     State("user-session", "data"),
     State("editing-holding-id", "data")],
    prevent_initial_call=True
)
def update_holding(n_clicks, symbol, shares, avg_cost, sector, session, editing_id):
    """Update an existing holding"""
    if not n_clicks or not editing_id:
        return dash.no_update
    
    if not symbol or not shares or not avg_cost:
        return "Please fill in Symbol, Shares, and Average Cost"
    
    if not session or 'token' not in session:
        return "Please login first"
    
    token = session['token']
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get portfolio ID
        portfolios_resp = requests.get(
            f"{BACKEND_URL}/api/portfolios/",
            headers=headers,
            timeout=10
        )
        
        if portfolios_resp.status_code != 200 or not portfolios_resp.json():
            return "Portfolio not found"
        
        portfolio_id = portfolios_resp.json()[0]['id']
        
        # Update holding
        holding_data = {
            "shares": int(shares),
            "avg_cost": float(avg_cost),
            "sector": sector if sector else None
        }
        
        resp = requests.put(
            f"{BACKEND_URL}/api/portfolios/{portfolio_id}/holdings/{editing_id}",
            headers=headers,
            json=holding_data,
            timeout=10
        )
        
        if resp.status_code == 200:
            return ""  # Success, modal will close
        else:
            error = resp.json().get('detail', 'Error updating holding')
            return error
            
    except Exception as e:
        return f"Error: {str(e)}"


# Import Screenshot button
@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("btn-import-ss", "n_clicks"),
    prevent_initial_call=True
)
def go_to_import(n_clicks):
    """Navigate to import page"""
    if n_clicks:
        return "/import"
    return dash.no_update


# Logout callback
@callback(
    [Output("url", "pathname", allow_duplicate=True),
     Output("user-session", "data", allow_duplicate=True)],
    Input("logout-btn-portfolio", "n_clicks"),
    prevent_initial_call=True
)
def handle_logout_portfolio(n_clicks):
    """Handle logout from portfolio page"""
    if n_clicks:
        return "/login", None
    return dash.no_update, dash.no_update
