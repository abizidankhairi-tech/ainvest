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
            dbc.NavbarToggler(id="navbar-toggler-alerts"),
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
                    ], href="/strategies")),
                    dbc.NavItem(dbc.NavLink([
                        html.I(className="fas fa-bell me-1"),
                        "Alerts"
                    ], href="/alerts", active=True)),
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
                            ], id="logout-btn-alerts")
                        ],
                        label="Account",
                        nav=True,
                        in_navbar=True
                    )
                ], className="ms-auto", navbar=True),
                id="navbar-collapse-alerts",
                navbar=True
            )
        ], fluid=True),
        color="dark",
        dark=True,
        className="mb-4",
        sticky="top"
    )


def format_currency(value):
    """Format value as Indonesian Rupiah"""
    if value is None:
        return "-"
    return f"Rp {value:,.0f}"


def create_alert_card(alert):
    """Create an alert card"""
    status = alert.get("status", "active")
    status_color = {
        "active": "success",
        "triggered": "warning",
        "expired": "secondary",
        "cancelled": "secondary"
    }.get(status, "info")
    
    alert_type = alert.get("alert_type", "price_target")
    type_icon = {
        "price_target": "fa-bullseye",
        "stop_loss": "fa-shield-alt",
        "price_above": "fa-arrow-up",
        "price_below": "fa-arrow-down"
    }.get(alert_type, "fa-bell")
    
    type_color = "text-success" if "above" in alert_type or alert_type == "price_target" else "text-danger"
    
    current_price = alert.get("current_price")
    trigger_price = alert.get("trigger_price")
    distance_pct = alert.get("distance_pct")
    
    # Progress toward trigger
    progress_value = 0
    if current_price and trigger_price:
        if alert.get("trigger_condition") == "above":
            progress_value = min(100, (current_price / trigger_price) * 100)
        else:
            progress_value = min(100, (trigger_price / current_price) * 100)
    
    return dbc.Card([
        dbc.CardHeader([
            dbc.Row([
                dbc.Col([
                    html.H5([
                        html.I(className=f"fas {type_icon} me-2 {type_color}"),
                        alert.get("symbol", "N/A")
                    ], className="mb-0")
                ]),
                dbc.Col([
                    dbc.Badge(status.upper(), color=status_color)
                ], className="text-end")
            ])
        ]),
        dbc.CardBody([
            html.P(alert.get("message", ""), className="fw-bold mb-2"),
            
            dbc.Row([
                dbc.Col([
                    html.Small([
                        html.Strong("Current: "),
                        html.Span(
                            format_currency(current_price) if current_price else "Loading...",
                            className="text-primary"
                        )
                    ], className="d-block mb-1"),
                    html.Small([
                        html.Strong("Target: "),
                        html.Span(format_currency(trigger_price))
                    ], className="d-block mb-1")
                ], width=6),
                dbc.Col([
                    html.Small([
                        html.Strong("Distance: "),
                        html.Span(
                            f"{distance_pct:+.2f}%" if distance_pct else "-",
                            className="text-success" if distance_pct and distance_pct > 0 else "text-danger"
                        )
                    ], className="d-block mb-1"),
                    html.Small([
                        html.Strong("Condition: "),
                        html.Span(alert.get("trigger_condition", "").upper())
                    ], className="d-block mb-1")
                ], width=6)
            ]),
            
            dbc.Progress(
                value=progress_value,
                color="success" if progress_value < 90 else "warning",
                className="my-3",
                style={"height": "6px"}
            ),
            
            html.Div([
                html.Small([
                    html.I(className="fas fa-clock me-1"),
                    f"Created: {alert.get('created_at', '')[:10] if alert.get('created_at') else 'N/A'}"
                ], className="text-muted")
            ]) if status == "active" else html.Div([
                html.Small([
                    html.I(className="fas fa-check-circle me-1 text-warning"),
                    f"Triggered: {alert.get('triggered_at', '')[:10] if alert.get('triggered_at') else 'N/A'}"
                ])
            ]) if status == "triggered" else None,
            
            html.Hr(),
            
            dbc.ButtonGroup([
                dbc.Button([
                    html.I(className="fas fa-edit me-1"),
                    "Edit"
                ], id={"type": "btn-edit-alert", "index": alert.get("id")}, 
                   color="primary", size="sm", outline=True) if status == "active" else None,
                dbc.Button([
                    html.I(className="fas fa-trash me-1"),
                ], id={"type": "btn-delete-alert", "index": alert.get("id")}, 
                   color="danger", size="sm", outline=True)
            ])
        ])
    ], className="mb-3 shadow-sm")


def create_notification_item(notification):
    """Create a notification list item"""
    icon_class = "fa-bell"
    icon_color = "text-info"
    
    if notification.get("type") == "alert":
        icon_class = "fa-exclamation-circle"
        icon_color = "text-warning"
    elif notification.get("type") == "success":
        icon_class = "fa-check-circle"
        icon_color = "text-success"
    elif notification.get("type") == "error":
        icon_class = "fa-times-circle"
        icon_color = "text-danger"
    
    bg_class = "" if notification.get("is_read") else "bg-light"
    
    return dbc.ListGroupItem([
        dbc.Row([
            dbc.Col([
                html.I(className=f"fas {icon_class} fa-lg {icon_color}")
            ], width="auto"),
            dbc.Col([
                html.Div([
                    html.Strong(notification.get("title", "Notification")),
                    html.Span(" - ", className="text-muted"),
                    html.Small(notification.get("created_at", "")[:16] if notification.get("created_at") else "", className="text-muted")
                ]),
                html.P(notification.get("message", ""), className="mb-0 small text-muted")
            ]),
            dbc.Col([
                dbc.Button([
                    html.I(className="fas fa-check")
                ], id={"type": "btn-mark-read", "index": notification.get("id")}, 
                   color="light", size="sm", className="border-0") if not notification.get("is_read") else None
            ], width="auto")
        ], className="align-items-center")
    ], className=bg_class, action=True, href=notification.get("action_url"))


# Alerts page layout
alerts_layout = html.Div([
    create_navbar(),
    
    dbc.Container([
        # Page header
        dbc.Row([
            dbc.Col([
                html.H2([
                    html.I(className="fas fa-bell me-3 text-warning"),
                    "Alerts & Notifications"
                ]),
                html.P("Manage price alerts and view notifications", className="text-muted")
            ]),
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button([
                        html.I(className="fas fa-sync me-2"),
                        "Check Alerts"
                    ], id="btn-check-alerts", color="info", outline=True, className="me-2"),
                    dbc.Button([
                        html.I(className="fas fa-plus me-2"),
                        "New Alert"
                    ], id="btn-new-alert", color="primary")
                ], className="float-end")
            ])
        ], className="mb-4"),
        
        dbc.Row([
            # Alerts column
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        dbc.Row([
                            dbc.Col([
                                html.H5([
                                    html.I(className="fas fa-crosshairs me-2"),
                                    "Price Alerts"
                                ], className="mb-0")
                            ]),
                            dbc.Col([
                                dbc.Select(
                                    id="select-alert-status",
                                    options=[
                                        {"label": "All", "value": ""},
                                        {"label": "Active", "value": "active"},
                                        {"label": "Triggered", "value": "triggered"},
                                        {"label": "Expired", "value": "expired"}
                                    ],
                                    value="",
                                    size="sm",
                                    style={"width": "120px"}
                                )
                            ], width="auto")
                        ])
                    ]),
                    dbc.CardBody([
                        html.Div(id="alerts-container")
                    ], style={"maxHeight": "600px", "overflowY": "auto"})
                ], className="shadow-sm")
            ], width=12, lg=7, className="mb-4"),
            
            # Notifications column
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        dbc.Row([
                            dbc.Col([
                                html.H5([
                                    html.I(className="fas fa-inbox me-2"),
                                    "Notifications",
                                    dbc.Badge(id="unread-count-badge", color="danger", className="ms-2", pill=True)
                                ], className="mb-0")
                            ]),
                            dbc.Col([
                                dbc.Button([
                                    html.I(className="fas fa-check-double me-1"),
                                    "Mark All Read"
                                ], id="btn-mark-all-read", color="link", size="sm")
                            ], width="auto")
                        ])
                    ]),
                    dbc.CardBody([
                        dbc.ListGroup(id="notifications-container", flush=True)
                    ], style={"maxHeight": "600px", "overflowY": "auto"})
                ], className="shadow-sm")
            ], width=12, lg=5, className="mb-4")
        ]),
        
        # Alert stats row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-bell fa-2x text-success mb-2"),
                            html.H4(id="stat-active-alerts", className="mb-0"),
                            html.Small("Active Alerts", className="text-muted")
                        ], className="text-center")
                    ])
                ], className="shadow-sm")
            ], width=6, lg=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-exclamation-triangle fa-2x text-warning mb-2"),
                            html.H4(id="stat-triggered-alerts", className="mb-0"),
                            html.Small("Triggered Today", className="text-muted")
                        ], className="text-center")
                    ])
                ], className="shadow-sm")
            ], width=6, lg=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-chart-line fa-2x text-info mb-2"),
                            html.H4(id="stat-stocks-watched", className="mb-0"),
                            html.Small("Stocks Watched", className="text-muted")
                        ], className="text-center")
                    ])
                ], className="shadow-sm")
            ], width=6, lg=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-envelope fa-2x text-primary mb-2"),
                            html.H4(id="stat-unread-notifs", className="mb-0"),
                            html.Small("Unread Messages", className="text-muted")
                        ], className="text-center")
                    ])
                ], className="shadow-sm")
            ], width=6, lg=3)
        ], className="mb-4")
    ], fluid=True),
    
    # New Alert Modal
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle([
            html.I(className="fas fa-plus-circle me-2"),
            "Create Price Alert"
        ])),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Stock Symbol"),
                        dbc.Input(
                            id="input-alert-symbol",
                            type="text",
                            placeholder="e.g., BBCA",
                            className="mb-3"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Alert Type"),
                        dbc.Select(
                            id="select-alert-type",
                            options=[
                                {"label": "Price Target", "value": "price_target"},
                                {"label": "Stop Loss", "value": "stop_loss"},
                                {"label": "Price Above", "value": "price_above"},
                                {"label": "Price Below", "value": "price_below"}
                            ],
                            value="price_target",
                            className="mb-3"
                        )
                    ], width=6)
                ]),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Trigger Price (Rp)"),
                        dbc.Input(
                            id="input-alert-price",
                            type="number",
                            placeholder="e.g., 9500",
                            min=0,
                            className="mb-3"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Condition"),
                        dbc.Select(
                            id="select-alert-condition",
                            options=[
                                {"label": "Above or Equal", "value": "above"},
                                {"label": "Below or Equal", "value": "below"}
                            ],
                            value="above",
                            className="mb-3"
                        )
                    ], width=6)
                ]),
                
                dbc.Label("Custom Message (optional)"),
                dbc.Input(
                    id="input-alert-message",
                    type="text",
                    placeholder="Alert message...",
                    className="mb-3"
                ),
                
                html.Hr(),
                
                dbc.Label("Notification Channels"),
                dbc.Checklist(
                    id="input-alert-channels",
                    options=[
                        {"label": "In-App Notification", "value": "in-app"},
                        {"label": "Email (coming soon)", "value": "email", "disabled": True},
                        {"label": "SMS (coming soon)", "value": "sms", "disabled": True}
                    ],
                    value=["in-app"],
                    className="mb-3"
                )
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="btn-cancel-alert", color="secondary"),
            dbc.Button([
                html.I(className="fas fa-bell me-2"),
                "Create Alert"
            ], id="btn-save-alert", color="primary")
        ])
    ], id="modal-new-alert", size="lg", is_open=False),
    
    # Toast for notifications
    dbc.Toast(
        id="alerts-toast",
        header="Notification",
        is_open=False,
        dismissable=True,
        duration=4000,
        icon="success",
        style={"position": "fixed", "top": 80, "right": 20, "width": 350, "zIndex": 9999}
    ),
    
    # Interval for checking alerts
    dcc.Interval(
        id="interval-check-alerts",
        interval=60 * 1000,  # Check every minute
        n_intervals=0,
        disabled=True  # Disabled by default, enable when needed
    ),
    
    # Hidden button for empty state (needed for callback)
    html.Div([
        dbc.Button(id="btn-new-alert-empty", style={"display": "none"})
    ], style={"display": "none"})
])


# Callbacks

@callback(
    [Output("alerts-container", "children"),
     Output("stat-active-alerts", "children"),
     Output("stat-triggered-alerts", "children"),
     Output("stat-stocks-watched", "children")],
    [Input("url", "pathname"),
     Input("select-alert-status", "value")],
    [State("user-session", "data")],
    prevent_initial_call=False
)
def load_alerts(pathname, status_filter, session):
    """Load price alerts"""
    if pathname != "/alerts":
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    if not session or 'token' not in session:
        return dbc.Alert("Please login to view alerts", color="warning"), "0", "0", "0"
    
    token = session['token']
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        url = f"{BACKEND_URL}/api/alerts/"
        if status_filter:
            url += f"?status_filter={status_filter}"
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            alerts = response.json()
            
            if not alerts:
                empty_content = html.Div([
                    html.I(className="fas fa-bell-slash fa-3x text-muted mb-3"),
                    html.H5("No Alerts", className="text-muted"),
                    html.P("Create your first price alert to get notified.", className="text-muted"),
                    dbc.Button([
                        html.I(className="fas fa-plus me-2"),
                        "Create Alert"
                    ], id="btn-new-alert-empty", color="primary")
                ], className="text-center py-5")
                return empty_content, "0", "0", "0"
            
            # Calculate stats
            active_count = len([a for a in alerts if a.get("status") == "active"])
            triggered_count = len([a for a in alerts if a.get("status") == "triggered"])
            unique_symbols = len(set([a.get("symbol") for a in alerts]))
            
            alert_cards = [create_alert_card(a) for a in alerts]
            return html.Div(alert_cards), str(active_count), str(triggered_count), str(unique_symbols)
        
        return dbc.Alert(f"Error loading alerts: {response.status_code}", color="danger"), "0", "0", "0"
        
    except Exception as e:
        return dbc.Alert(f"Error: {str(e)}", color="danger"), "0", "0", "0"


@callback(
    [Output("notifications-container", "children"),
     Output("unread-count-badge", "children"),
     Output("stat-unread-notifs", "children")],
    [Input("url", "pathname")],
    [State("user-session", "data")],
    prevent_initial_call=False
)
def load_notifications(pathname, session):
    """Load notifications"""
    if pathname != "/alerts":
        return dash.no_update, dash.no_update, dash.no_update
    
    if not session or 'token' not in session:
        return [], "", "0"
    
    token = session['token']
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get notifications
        response = requests.get(
            f"{BACKEND_URL}/api/alerts/notifications?limit=20",
            headers=headers,
            timeout=10
        )
        
        # Get unread count
        count_response = requests.get(
            f"{BACKEND_URL}/api/alerts/notifications/count",
            headers=headers,
            timeout=10
        )
        
        notifications = []
        unread_count = 0
        
        if response.status_code == 200:
            notifications = response.json()
        
        if count_response.status_code == 200:
            unread_count = count_response.json().get("unread_count", 0)
        
        if not notifications:
            return [
                dbc.ListGroupItem([
                    html.Div([
                        html.I(className="fas fa-inbox fa-2x text-muted mb-2"),
                        html.P("No notifications yet", className="text-muted mb-0")
                    ], className="text-center py-4")
                ])
            ], "", "0"
        
        notification_items = [create_notification_item(n) for n in notifications]
        badge_text = str(unread_count) if unread_count > 0 else ""
        
        return notification_items, badge_text, str(unread_count)
        
    except Exception as e:
        return [dbc.ListGroupItem(f"Error: {str(e)}")], "", "0"


@callback(
    Output("modal-new-alert", "is_open"),
    [Input("btn-new-alert", "n_clicks"),
     Input("btn-new-alert-empty", "n_clicks"),
     Input("btn-cancel-alert", "n_clicks"),
     Input("btn-save-alert", "n_clicks")],
    [State("modal-new-alert", "is_open")],
    prevent_initial_call=True
)
def toggle_alert_modal(n_new, n_empty, n_cancel, n_save, is_open):
    """Toggle alert modal"""
    triggered = ctx.triggered_id
    if triggered in ["btn-new-alert", "btn-new-alert-empty"]:
        return True
    return False


@callback(
    [Output("alerts-toast", "is_open"),
     Output("alerts-toast", "children"),
     Output("alerts-toast", "header"),
     Output("alerts-toast", "icon"),
     Output("alerts-container", "children", allow_duplicate=True),
     Output("stat-active-alerts", "children", allow_duplicate=True)],
    [Input("btn-save-alert", "n_clicks")],
    [State("input-alert-symbol", "value"),
     State("select-alert-type", "value"),
     State("input-alert-price", "value"),
     State("select-alert-condition", "value"),
     State("input-alert-message", "value"),
     State("input-alert-channels", "value"),
     State("user-session", "data")],
    prevent_initial_call=True
)
def save_alert(n_clicks, symbol, alert_type, price, condition, message, channels, session):
    """Save new alert"""
    if not n_clicks:
        return False, "", "", "info", dash.no_update, dash.no_update
    
    if not session or 'token' not in session:
        return True, "Please login to create alerts", "Error", "danger", dash.no_update, dash.no_update
    
    if not symbol or not price:
        return True, "Please fill in symbol and price", "Validation Error", "warning", dash.no_update, dash.no_update
    
    token = session['token']
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    try:
        payload = {
            "alert_type": alert_type,
            "symbol": symbol.upper(),
            "trigger_price": float(price),
            "trigger_condition": condition,
            "message": message if message else None,
            "channels": channels if channels else ["in-app"]
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/alerts/",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 201:
            # Reload alerts
            reload_response = requests.get(
                f"{BACKEND_URL}/api/alerts/",
                headers=headers,
                timeout=15
            )
            
            if reload_response.status_code == 200:
                alerts = reload_response.json()
                active_count = len([a for a in alerts if a.get("status") == "active"])
                alert_cards = [create_alert_card(a) for a in alerts]
                return True, f"Alert for {symbol.upper()} created!", "Success", "success", html.Div(alert_cards), str(active_count)
            
            return True, "Alert created! Refresh to see.", "Success", "success", dash.no_update, dash.no_update
        
        error_msg = response.json().get("detail", "Failed to create alert")
        return True, error_msg, "Error", "danger", dash.no_update, dash.no_update
        
    except Exception as e:
        return True, str(e), "Error", "danger", dash.no_update, dash.no_update


@callback(
    [Output("alerts-toast", "is_open", allow_duplicate=True),
     Output("alerts-toast", "children", allow_duplicate=True),
     Output("alerts-toast", "header", allow_duplicate=True),
     Output("alerts-toast", "icon", allow_duplicate=True)],
    [Input("btn-check-alerts", "n_clicks")],
    [State("user-session", "data")],
    prevent_initial_call=True
)
def check_alerts_manually(n_clicks, session):
    """Manually check alerts"""
    if not n_clicks:
        return False, "", "", "info"
    
    if not session or 'token' not in session:
        return True, "Please login", "Error", "danger"
    
    token = session['token']
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/alerts/check",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            triggered = result.get("triggered", [])
            checked = result.get("checked", 0)
            
            if triggered:
                msg = f"{len(triggered)} alert(s) triggered! Check notifications."
                return True, msg, "Alerts Triggered", "warning"
            else:
                msg = f"Checked {checked} active alerts. No triggers."
                return True, msg, "Check Complete", "info"
        
        return True, "Failed to check alerts", "Error", "danger"
        
    except Exception as e:
        return True, str(e), "Error", "danger"


@callback(
    [Output("notifications-container", "children", allow_duplicate=True),
     Output("unread-count-badge", "children", allow_duplicate=True),
     Output("stat-unread-notifs", "children", allow_duplicate=True)],
    [Input("btn-mark-all-read", "n_clicks")],
    [State("user-session", "data")],
    prevent_initial_call=True
)
def mark_all_read(n_clicks, session):
    """Mark all notifications as read"""
    if not n_clicks:
        return dash.no_update, dash.no_update, dash.no_update
    
    if not session or 'token' not in session:
        return dash.no_update, dash.no_update, dash.no_update
    
    token = session['token']
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Mark all as read
        requests.put(
            f"{BACKEND_URL}/api/alerts/notifications/read-all",
            headers=headers,
            timeout=10
        )
        
        # Reload notifications
        response = requests.get(
            f"{BACKEND_URL}/api/alerts/notifications?limit=20",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            notifications = response.json()
            notification_items = [create_notification_item(n) for n in notifications]
            return notification_items, "", "0"
        
        return dash.no_update, dash.no_update, dash.no_update
        
    except Exception:
        return dash.no_update, dash.no_update, dash.no_update


# Logout callback
@callback(
    [Output("url", "pathname", allow_duplicate=True),
     Output("user-session", "data", allow_duplicate=True)],
    Input("logout-btn-alerts", "n_clicks"),
    prevent_initial_call=True
)
def handle_logout_alerts(n_clicks):
    """Handle logout from alerts page"""
    if n_clicks:
        return "/login", None
    return dash.no_update, dash.no_update
