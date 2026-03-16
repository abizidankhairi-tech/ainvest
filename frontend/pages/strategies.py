import dash
from dash import html, dcc, Input, Output, State, callback, ctx, ALL
import dash_bootstrap_components as dbc
import requests
import os
from datetime import datetime

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def create_navbar():
    """Create the navigation bar"""
    return dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand([
                html.I(className="fas fa-chart-line me-2"),
                "InvestAI"
            ], href="/dashboard", className="fw-bold"),
            dbc.NavbarToggler(id="navbar-toggler-strategies"),
            dbc.Collapse(
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink([
                        html.I(className="fas fa-tachometer-alt me-1"),
                        "Dashboard"
                    ], href="/dashboard")),
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
                    ], href="/strategies", active=True)),
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
                            ], id="logout-btn-strategies")
                        ],
                        label="Account",
                        nav=True,
                        in_navbar=True
                    )
                ], className="ms-auto", navbar=True),
                id="navbar-collapse-strategies",
                navbar=True
            )
        ], fluid=True),
        color="dark",
        dark=True,
        className="mb-4",
        sticky="top"
    )


def create_buy_zone_row(zone_num, min_price="", max_price="", allocation=""):
    """Create a buy zone input row"""
    return dbc.Row([
        dbc.Col([
            dbc.Label(f"Zone {zone_num}", className="fw-bold small")
        ], width=1),
        dbc.Col([
            dbc.Input(
                id={"type": "zone-min", "index": zone_num},
                type="number",
                placeholder="Min Price",
                value=min_price,
                min=0
            )
        ], width=3),
        dbc.Col([
            dbc.Input(
                id={"type": "zone-max", "index": zone_num},
                type="number",
                placeholder="Max Price",
                value=max_price,
                min=0
            )
        ], width=3),
        dbc.Col([
            dbc.InputGroup([
                dbc.Input(
                    id={"type": "zone-alloc", "index": zone_num},
                    type="number",
                    placeholder="Allocation",
                    value=allocation,
                    min=0,
                    max=100
                ),
                dbc.InputGroupText("%")
            ])
        ], width=3),
        dbc.Col([
            html.Span(id={"type": "zone-amount", "index": zone_num}, className="text-muted small")
        ], width=2)
    ], className="mb-2 align-items-center")


def format_currency(value):
    """Format value as Indonesian Rupiah"""
    if value is None:
        return "-"
    return f"Rp {value:,.0f}"


def create_entry_strategy_card(strategy):
    """Create an entry strategy card"""
    status_color = {
        "active": "success",
        "completed": "info",
        "cancelled": "secondary"
    }.get(strategy.get("status", "active"), "primary")
    
    current_price = strategy.get("current_price")
    buy_zones = strategy.get("buy_zones", [])
    
    # Find active zone
    active_zone = None
    if current_price and buy_zones:
        for zone in buy_zones:
            if zone.get("min_price", 0) <= current_price <= zone.get("max_price", float('inf')):
                active_zone = zone.get("zone_num")
                break
    
    zone_badges = []
    for zone in buy_zones:
        is_active = zone.get("zone_num") == active_zone
        badge_color = "success" if is_active else "secondary"
        zone_badges.append(
            dbc.Badge(
                f"Z{zone.get('zone_num')}: {format_currency(zone.get('min_price'))}-{format_currency(zone.get('max_price'))} ({zone.get('allocation')}%)",
                color=badge_color,
                className="me-1 mb-1"
            )
        )
    
    deployed_pct = 0
    if strategy.get("total_capital", 0) > 0:
        deployed_pct = (strategy.get("deployed_capital", 0) / strategy.get("total_capital", 1)) * 100
    
    return dbc.Card([
        dbc.CardHeader([
            dbc.Row([
                dbc.Col([
                    html.H5([
                        html.I(className="fas fa-chart-line me-2"),
                        strategy.get("symbol", "N/A")
                    ], className="mb-0")
                ]),
                dbc.Col([
                    dbc.Badge(strategy.get("status", "active").upper(), color=status_color),
                    dbc.Switch(
                        id={"type": "entry-alert-toggle", "index": strategy.get("id")},
                        value=strategy.get("alert_enabled", True),
                        label="Alerts",
                        className="ms-3 d-inline-flex"
                    )
                ], className="text-end")
            ])
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.P([
                        html.Strong("Current Price: "),
                        html.Span(
                            format_currency(current_price) if current_price else "Loading...",
                            className="text-primary fw-bold"
                        )
                    ], className="mb-2"),
                    html.P([
                        html.Strong("Total Capital: "),
                        format_currency(strategy.get("total_capital"))
                    ], className="mb-2"),
                    html.P([
                        html.Strong("Deployed: "),
                        format_currency(strategy.get("deployed_capital", 0)),
                        f" ({deployed_pct:.1f}%)"
                    ], className="mb-2")
                ], width=6),
                dbc.Col([
                    html.P(html.Strong("Buy Zones:"), className="mb-2"),
                    html.Div(zone_badges)
                ], width=6)
            ]),
            dbc.Progress(
                value=deployed_pct,
                color="success",
                className="mb-3",
                style={"height": "8px"}
            ),
            dbc.ButtonGroup([
                dbc.Button([
                    html.I(className="fas fa-shopping-cart me-1"),
                    "Record Buy"
                ], id={"type": "btn-record-buy", "index": strategy.get("id")}, 
                   color="success", size="sm", outline=True),
                dbc.Button([
                    html.I(className="fas fa-history me-1"),
                    "Executions"
                ], id={"type": "btn-view-executions", "index": strategy.get("id")}, 
                   color="info", size="sm", outline=True),
                dbc.Button([
                    html.I(className="fas fa-trash me-1"),
                ], id={"type": "btn-delete-entry", "index": strategy.get("id")}, 
                   color="danger", size="sm", outline=True)
            ])
        ])
    ], className="mb-3 shadow-sm")


def create_exit_strategy_card(strategy):
    """Create an exit strategy card"""
    current_price = strategy.get("current_price")
    avg_cost = strategy.get("avg_cost", 0)
    
    # Calculate P/L
    pl_pct = 0
    if avg_cost and current_price:
        pl_pct = ((current_price - avg_cost) / avg_cost) * 100
    
    tp_targets = []
    for i in range(1, 4):
        tp_price = strategy.get(f"tp{i}_price")
        tp_alloc = strategy.get(f"tp{i}_allocation")
        if tp_price:
            distance = ((tp_price - current_price) / current_price * 100) if current_price else 0
            tp_targets.append(
                html.Div([
                    dbc.Badge(f"TP{i}", color="success", className="me-2"),
                    html.Span(f"{format_currency(tp_price)} ({tp_alloc}%) "),
                    html.Small(f"+{distance:.1f}%", className="text-muted") if distance > 0 else ""
                ], className="mb-1")
            )
    
    stop_loss = strategy.get("stop_loss")
    if stop_loss:
        distance = ((stop_loss - current_price) / current_price * 100) if current_price else 0
        tp_targets.append(
            html.Div([
                dbc.Badge("SL", color="danger", className="me-2"),
                html.Span(f"{format_currency(stop_loss)} "),
                html.Small(f"{distance:.1f}%", className="text-danger") if distance < 0 else ""
            ], className="mb-1")
        )
    
    return dbc.Card([
        dbc.CardHeader([
            dbc.Row([
                dbc.Col([
                    html.H5([
                        html.I(className="fas fa-sign-out-alt me-2"),
                        strategy.get("symbol", "N/A")
                    ], className="mb-0")
                ]),
                dbc.Col([
                    dbc.Switch(
                        id={"type": "exit-alert-toggle", "index": strategy.get("id")},
                        value=strategy.get("alert_enabled", True),
                        label="Alerts",
                        className="d-inline-flex"
                    )
                ], className="text-end")
            ])
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.P([
                        html.Strong("Current: "),
                        html.Span(format_currency(current_price), className="text-primary fw-bold")
                    ], className="mb-1"),
                    html.P([
                        html.Strong("Avg Cost: "),
                        html.Span(format_currency(avg_cost))
                    ], className="mb-1"),
                    html.P([
                        html.Strong("P/L: "),
                        html.Span(
                            f"{pl_pct:+.2f}%",
                            className="text-success fw-bold" if pl_pct >= 0 else "text-danger fw-bold"
                        )
                    ], className="mb-1")
                ], width=5),
                dbc.Col([
                    html.P(html.Strong("Targets:"), className="mb-2"),
                    html.Div(tp_targets)
                ], width=7)
            ]),
            html.Hr(),
            dbc.ButtonGroup([
                dbc.Button([
                    html.I(className="fas fa-edit me-1"),
                    "Edit"
                ], id={"type": "btn-edit-exit", "index": strategy.get("id")}, 
                   color="primary", size="sm", outline=True),
                dbc.Button([
                    html.I(className="fas fa-trash me-1"),
                ], id={"type": "btn-delete-exit", "index": strategy.get("id")}, 
                   color="danger", size="sm", outline=True)
            ])
        ])
    ], className="mb-3 shadow-sm")


# Strategies page layout
strategies_layout = html.Div([
    create_navbar(),
    
    dbc.Container([
        # Page header
        dbc.Row([
            dbc.Col([
                html.H2([
                    html.I(className="fas fa-crosshairs me-3 text-primary"),
                    "Entry & Exit Strategies"
                ]),
                html.P("Plan your buy zones and take-profit targets", className="text-muted")
            ]),
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button([
                        html.I(className="fas fa-plus me-2"),
                        "New Entry Strategy"
                    ], id="btn-new-entry-strategy", color="success"),
                    dbc.Button([
                        html.I(className="fas fa-plus me-2"),
                        "New Exit Strategy"
                    ], id="btn-new-exit-strategy", color="primary")
                ], className="float-end")
            ])
        ], className="mb-4"),
        
        # Tabs for Entry/Exit strategies
        dbc.Tabs([
            dbc.Tab([
                html.Div(id="entry-strategies-container", className="mt-3")
            ], label="Entry Strategies", tab_id="tab-entry"),
            dbc.Tab([
                html.Div(id="exit-strategies-container", className="mt-3")
            ], label="Exit Strategies", tab_id="tab-exit")
        ], id="strategies-tabs", active_tab="tab-entry"),
        
    ], fluid=True),
    
    # New Entry Strategy Modal
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle([
            html.I(className="fas fa-plus-circle me-2"),
            "Create Entry Strategy"
        ])),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Stock Symbol"),
                        dbc.Input(
                            id="input-entry-symbol",
                            type="text",
                            placeholder="e.g., BBCA",
                            className="mb-3"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Total Capital (Rp)"),
                        dbc.Input(
                            id="input-entry-capital",
                            type="number",
                            placeholder="e.g., 10000000",
                            min=100000,
                            className="mb-3"
                        )
                    ], width=6)
                ]),
                
                html.Hr(),
                
                html.H6([
                    html.I(className="fas fa-layer-group me-2"),
                    "Buy Zones"
                ], className="mb-3"),
                html.P("Define price ranges and capital allocation for each zone", className="text-muted small"),
                
                html.Div([
                    dbc.Row([
                        dbc.Col([html.Strong("Zone", className="small")], width=1),
                        dbc.Col([html.Strong("Min Price", className="small")], width=3),
                        dbc.Col([html.Strong("Max Price", className="small")], width=3),
                        dbc.Col([html.Strong("Allocation", className="small")], width=3),
                        dbc.Col([html.Strong("Amount", className="small")], width=2)
                    ], className="mb-2"),
                    create_buy_zone_row(1),
                    create_buy_zone_row(2),
                    create_buy_zone_row(3),
                ], id="buy-zones-container"),
                
                html.Div(id="allocation-warning", className="mt-2"),
                
                dbc.Checkbox(
                    id="input-entry-alerts",
                    label="Enable price alerts for buy zones",
                    value=True,
                    className="mt-3"
                )
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="btn-cancel-entry-strategy", color="secondary"),
            dbc.Button([
                html.I(className="fas fa-save me-2"),
                "Create Strategy"
            ], id="btn-save-entry-strategy", color="success")
        ])
    ], id="modal-new-entry-strategy", size="lg", is_open=False),
    
    # New Exit Strategy Modal
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle([
            html.I(className="fas fa-plus-circle me-2"),
            "Create Exit Strategy"
        ])),
        dbc.ModalBody([
            dbc.Form([
                dbc.Label("Select Holding"),
                dcc.Dropdown(
                    id="dropdown-exit-holding",
                    placeholder="Select a holding...",
                    className="mb-3"
                ),
                
                html.Div(id="holding-details", className="mb-3"),
                
                html.Hr(),
                
                html.H6([
                    html.I(className="fas fa-bullseye me-2"),
                    "Take Profit Targets"
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("TP1 Price"),
                        dbc.Input(id="input-tp1-price", type="number", placeholder="Price", min=0)
                    ], width=6),
                    dbc.Col([
                        dbc.Label("TP1 Allocation (%)"),
                        dbc.Input(id="input-tp1-alloc", type="number", placeholder="%", min=0, max=100)
                    ], width=6)
                ], className="mb-2"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("TP2 Price"),
                        dbc.Input(id="input-tp2-price", type="number", placeholder="Price", min=0)
                    ], width=6),
                    dbc.Col([
                        dbc.Label("TP2 Allocation (%)"),
                        dbc.Input(id="input-tp2-alloc", type="number", placeholder="%", min=0, max=100)
                    ], width=6)
                ], className="mb-2"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("TP3 Price"),
                        dbc.Input(id="input-tp3-price", type="number", placeholder="Price", min=0)
                    ], width=6),
                    dbc.Col([
                        dbc.Label("TP3 Allocation (%)"),
                        dbc.Input(id="input-tp3-alloc", type="number", placeholder="%", min=0, max=100)
                    ], width=6)
                ], className="mb-3"),
                
                html.Hr(),
                
                html.H6([
                    html.I(className="fas fa-shield-alt me-2 text-danger"),
                    "Stop Loss"
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Stop Loss Price"),
                        dbc.Input(id="input-stop-loss", type="number", placeholder="Price", min=0)
                    ], width=6)
                ], className="mb-3"),
                
                dbc.Checkbox(
                    id="input-exit-alerts",
                    label="Enable price alerts for targets",
                    value=True
                )
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="btn-cancel-exit-strategy", color="secondary"),
            dbc.Button([
                html.I(className="fas fa-save me-2"),
                "Create Strategy"
            ], id="btn-save-exit-strategy", color="success")
        ])
    ], id="modal-new-exit-strategy", size="lg", is_open=False),
    
    # Record Execution Modal
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Record Buy Execution")),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Zone"),
                        dbc.Select(
                            id="input-exec-zone",
                            options=[
                                {"label": "Zone 1", "value": "1"},
                                {"label": "Zone 2", "value": "2"},
                                {"label": "Zone 3", "value": "3"}
                            ]
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Execution Date"),
                        dbc.Input(id="input-exec-date", type="date")
                    ], width=6)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Shares"),
                        dbc.Input(id="input-exec-shares", type="number", min=1, placeholder="Number of shares")
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Price per Share"),
                        dbc.Input(id="input-exec-price", type="number", min=0, placeholder="Buy price")
                    ], width=6)
                ], className="mb-3"),
                dbc.Label("Notes (optional)"),
                dbc.Textarea(id="input-exec-notes", placeholder="Any notes about this execution...")
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="btn-cancel-execution", color="secondary"),
            dbc.Button("Record", id="btn-save-execution", color="success")
        ])
    ], id="modal-record-execution", is_open=False),
    
    # Store for selected strategy ID
    dcc.Store(id="store-selected-strategy-id"),
    
    # Toast for notifications
    dbc.Toast(
        id="strategies-toast",
        header="Notification",
        is_open=False,
        dismissable=True,
        duration=4000,
        icon="success",
        style={"position": "fixed", "top": 80, "right": 20, "width": 350, "zIndex": 9999}
    )
])


# Callbacks

@callback(
    Output("entry-strategies-container", "children"),
    [Input("url", "pathname"),
     Input("strategies-tabs", "active_tab")],
    [State("user-session", "data")],
    prevent_initial_call=False
)
def load_entry_strategies(pathname, active_tab, session):
    """Load entry strategies"""
    if pathname != "/strategies" or active_tab != "tab-entry":
        return dash.no_update
    
    if not session or 'token' not in session:
        return dbc.Alert("Please login to view strategies", color="warning")
    
    token = session['token']
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/strategies/entry",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            strategies = response.json()
            
            if not strategies:
                return dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-inbox fa-3x text-muted mb-3"),
                            html.H5("No Entry Strategies", className="text-muted"),
                            html.P("Create your first entry strategy to plan your stock purchases.", className="text-muted"),
                            dbc.Button([
                                html.I(className="fas fa-plus me-2"),
                                "Create Entry Strategy"
                            ], id="btn-new-entry-empty", color="success")
                        ], className="text-center py-5")
                    ])
                ])
            
            strategy_cards = [create_entry_strategy_card(s) for s in strategies]
            return dbc.Row([dbc.Col(card, width=12, lg=6) for card in strategy_cards])
        
        return dbc.Alert(f"Error loading strategies: {response.status_code}", color="danger")
        
    except Exception as e:
        return dbc.Alert(f"Error: {str(e)}", color="danger")


@callback(
    Output("exit-strategies-container", "children"),
    [Input("url", "pathname"),
     Input("strategies-tabs", "active_tab")],
    [State("user-session", "data")],
    prevent_initial_call=False
)
def load_exit_strategies(pathname, active_tab, session):
    """Load exit strategies"""
    if pathname != "/strategies" or active_tab != "tab-exit":
        return dash.no_update
    
    if not session or 'token' not in session:
        return dbc.Alert("Please login to view strategies", color="warning")
    
    token = session['token']
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/strategies/exit",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            strategies = response.json()
            
            if not strategies:
                return dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-inbox fa-3x text-muted mb-3"),
                            html.H5("No Exit Strategies", className="text-muted"),
                            html.P("Create exit strategies for your holdings to set take-profit targets and stop losses.", className="text-muted"),
                            dbc.Button([
                                html.I(className="fas fa-plus me-2"),
                                "Create Exit Strategy"
                            ], id="btn-new-exit-empty", color="primary")
                        ], className="text-center py-5")
                    ])
                ])
            
            strategy_cards = [create_exit_strategy_card(s) for s in strategies]
            return dbc.Row([dbc.Col(card, width=12, lg=6) for card in strategy_cards])
        
        return dbc.Alert(f"Error loading strategies: {response.status_code}", color="danger")
        
    except Exception as e:
        return dbc.Alert(f"Error: {str(e)}", color="danger")


@callback(
    Output("modal-new-entry-strategy", "is_open"),
    [Input("btn-new-entry-strategy", "n_clicks"),
     Input("btn-new-entry-empty", "n_clicks"),
     Input("btn-cancel-entry-strategy", "n_clicks"),
     Input("btn-save-entry-strategy", "n_clicks")],
    [State("modal-new-entry-strategy", "is_open")],
    prevent_initial_call=True
)
def toggle_entry_modal(n_new, n_empty, n_cancel, n_save, is_open):
    """Toggle entry strategy modal"""
    triggered = ctx.triggered_id
    if triggered in ["btn-new-entry-strategy", "btn-new-entry-empty"]:
        return True
    return False


@callback(
    Output("modal-new-exit-strategy", "is_open"),
    [Input("btn-new-exit-strategy", "n_clicks"),
     Input("btn-new-exit-empty", "n_clicks"),
     Input("btn-cancel-exit-strategy", "n_clicks"),
     Input("btn-save-exit-strategy", "n_clicks")],
    [State("modal-new-exit-strategy", "is_open")],
    prevent_initial_call=True
)
def toggle_exit_modal(n_new, n_empty, n_cancel, n_save, is_open):
    """Toggle exit strategy modal"""
    triggered = ctx.triggered_id
    if triggered in ["btn-new-exit-strategy", "btn-new-exit-empty"]:
        return True
    return False


@callback(
    Output("dropdown-exit-holding", "options"),
    [Input("modal-new-exit-strategy", "is_open")],
    [State("user-session", "data")],
    prevent_initial_call=True
)
def load_holdings_for_exit(is_open, session):
    """Load holdings for exit strategy dropdown"""
    if not is_open:
        return []
    
    if not session or 'token' not in session:
        return []
    
    token = session['token']
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/holdings",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            holdings = response.json()
            return [
                {
                    "label": f"{h['symbol']} - {h['shares']} shares @ {format_currency(h.get('avg_cost'))}",
                    "value": h['id']
                }
                for h in holdings
            ]
        return []
        
    except Exception:
        return []


@callback(
    [Output("strategies-toast", "is_open", allow_duplicate=True),
     Output("strategies-toast", "children", allow_duplicate=True),
     Output("strategies-toast", "header", allow_duplicate=True),
     Output("strategies-toast", "icon", allow_duplicate=True),
     Output("entry-strategies-container", "children", allow_duplicate=True)],
    [Input("btn-save-entry-strategy", "n_clicks")],
    [State("input-entry-symbol", "value"),
     State("input-entry-capital", "value"),
     State({"type": "zone-min", "index": ALL}, "value"),
     State({"type": "zone-max", "index": ALL}, "value"),
     State({"type": "zone-alloc", "index": ALL}, "value"),
     State("input-entry-alerts", "value"),
     State("user-session", "data")],
    prevent_initial_call=True
)
def save_entry_strategy(n_clicks, symbol, capital, min_prices, max_prices, allocations, alerts, session):
    """Save new entry strategy"""
    if not n_clicks:
        return False, "", "", "info", dash.no_update
    
    if not session or 'token' not in session:
        return True, "Please login to create strategies", "Error", "danger", dash.no_update
    
    if not symbol or not capital:
        return True, "Please fill in symbol and capital", "Validation Error", "warning", dash.no_update
    
    # Build buy zones
    buy_zones = []
    for i in range(len(min_prices)):
        if min_prices[i] and max_prices[i] and allocations[i]:
            buy_zones.append({
                "zone_num": i + 1,
                "min_price": float(min_prices[i]),
                "max_price": float(max_prices[i]),
                "allocation": float(allocations[i])
            })
    
    if not buy_zones:
        return True, "Please define at least one buy zone", "Validation Error", "warning", dash.no_update
    
    # Validate allocations sum to 100
    total_alloc = sum(z["allocation"] for z in buy_zones)
    if abs(total_alloc - 100) > 0.01:
        return True, f"Allocations must sum to 100% (got {total_alloc}%)", "Validation Error", "warning", dash.no_update
    
    token = session['token']
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    try:
        payload = {
            "symbol": symbol.upper(),
            "total_capital": float(capital),
            "buy_zones": buy_zones,
            "alert_enabled": alerts
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/strategies/entry",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 201:
            # Reload strategies
            reload_response = requests.get(
                f"{BACKEND_URL}/api/strategies/entry",
                headers=headers,
                timeout=15
            )
            
            if reload_response.status_code == 200:
                strategies = reload_response.json()
                strategy_cards = [create_entry_strategy_card(s) for s in strategies]
                new_content = dbc.Row([dbc.Col(card, width=12, lg=6) for card in strategy_cards])
                return True, f"Entry strategy for {symbol.upper()} created!", "Success", "success", new_content
            
            return True, "Strategy created! Refresh to see.", "Success", "success", dash.no_update
        
        error_msg = response.json().get("detail", "Failed to create strategy")
        return True, error_msg, "Error", "danger", dash.no_update
        
    except Exception as e:
        return True, str(e), "Error", "danger", dash.no_update


@callback(
    [Output("strategies-toast", "is_open", allow_duplicate=True),
     Output("strategies-toast", "children", allow_duplicate=True),
     Output("strategies-toast", "header", allow_duplicate=True),
     Output("strategies-toast", "icon", allow_duplicate=True),
     Output("exit-strategies-container", "children", allow_duplicate=True)],
    [Input("btn-save-exit-strategy", "n_clicks")],
    [State("dropdown-exit-holding", "value"),
     State("input-tp1-price", "value"),
     State("input-tp1-alloc", "value"),
     State("input-tp2-price", "value"),
     State("input-tp2-alloc", "value"),
     State("input-tp3-price", "value"),
     State("input-tp3-alloc", "value"),
     State("input-stop-loss", "value"),
     State("input-exit-alerts", "value"),
     State("user-session", "data")],
    prevent_initial_call=True
)
def save_exit_strategy(n_clicks, holding_id, tp1_price, tp1_alloc, tp2_price, tp2_alloc, 
                       tp3_price, tp3_alloc, stop_loss, alerts, session):
    """Save new exit strategy"""
    if not n_clicks:
        return False, "", "", "info", dash.no_update
    
    if not session or 'token' not in session:
        return True, "Please login to create strategies", "Error", "danger", dash.no_update
    
    if not holding_id:
        return True, "Please select a holding", "Validation Error", "warning", dash.no_update
    
    if not tp1_price and not stop_loss:
        return True, "Please set at least one target or stop loss", "Validation Error", "warning", dash.no_update
    
    token = session['token']
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    try:
        payload = {
            "holding_id": int(holding_id),
            "tp1_price": float(tp1_price) if tp1_price else None,
            "tp1_allocation": float(tp1_alloc) if tp1_alloc else None,
            "tp2_price": float(tp2_price) if tp2_price else None,
            "tp2_allocation": float(tp2_alloc) if tp2_alloc else None,
            "tp3_price": float(tp3_price) if tp3_price else None,
            "tp3_allocation": float(tp3_alloc) if tp3_alloc else None,
            "stop_loss": float(stop_loss) if stop_loss else None,
            "alert_enabled": alerts
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/strategies/exit",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 201:
            # Reload strategies
            reload_response = requests.get(
                f"{BACKEND_URL}/api/strategies/exit",
                headers=headers,
                timeout=15
            )
            
            if reload_response.status_code == 200:
                strategies = reload_response.json()
                strategy_cards = [create_exit_strategy_card(s) for s in strategies]
                new_content = dbc.Row([dbc.Col(card, width=12, lg=6) for card in strategy_cards])
                return True, "Exit strategy created!", "Success", "success", new_content
            
            return True, "Strategy created! Refresh to see.", "Success", "success", dash.no_update
        
        error_msg = response.json().get("detail", "Failed to create strategy")
        return True, error_msg, "Error", "danger", dash.no_update
        
    except Exception as e:
        return True, str(e), "Error", "danger", dash.no_update


# Logout callback
@callback(
    [Output("url", "pathname", allow_duplicate=True),
     Output("user-session", "data", allow_duplicate=True)],
    Input("logout-btn-strategies", "n_clicks"),
    prevent_initial_call=True
)
def handle_logout_strategies(n_clicks):
    """Handle logout from strategies page"""
    if n_clicks:
        return "/login", None
    return dash.no_update, dash.no_update
