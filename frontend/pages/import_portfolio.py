import dash
from dash import html, dcc, Input, Output, State, callback, ctx
import dash_bootstrap_components as dbc
import requests
import os
import base64
import json

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def create_navbar():
    """Create the navigation bar"""
    return dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand([
                html.I(className="fas fa-chart-line me-2"),
                "InvestAI"
            ], href="/dashboard", className="fw-bold"),
            dbc.NavbarToggler(id="navbar-toggler-import"),
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
                    ], href="/import", active=True)),
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
                                html.I(className="fas fa-sign-out-alt me-2"),
                                "Logout"
                            ], id="logout-btn-import")
                        ],
                        label="Account",
                        nav=True,
                        in_navbar=True
                    )
                ], className="ms-auto", navbar=True),
                id="navbar-collapse-import",
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


# Import page layout
import_layout = html.Div([
    create_navbar(),
    
    dbc.Container([
        # Page header
        dbc.Row([
            dbc.Col([
                html.H2([
                    html.I(className="fas fa-camera me-3 text-success"),
                    "Import Portfolio from Screenshot"
                ]),
                html.P([
                    "Upload a screenshot from your broker app (IPOT, Stockbit, Ajaib) and we'll extract your holdings automatically using AI."
                ], className="text-muted lead")
            ])
        ], className="mb-4"),
        
        dbc.Row([
            # Left column - Upload area
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([
                            html.I(className="fas fa-upload me-2"),
                            "Step 1: Upload Screenshot"
                        ], className="mb-0")
                    ]),
                    dbc.CardBody([
                        # Upload component
                        dcc.Upload(
                            id='upload-image',
                            children=html.Div([
                                html.Div([
                                    html.I(className="fas fa-cloud-upload-alt fa-4x text-muted mb-3"),
                                    html.H5("Drag and drop or click to upload", className="text-muted"),
                                    html.P("PNG, JPEG, WebP - Max 5MB", className="text-muted small")
                                ], className="text-center py-5")
                            ]),
                            style={
                                'width': '100%',
                                'borderWidth': '2px',
                                'borderStyle': 'dashed',
                                'borderRadius': '10px',
                                'borderColor': '#ccc',
                                'backgroundColor': '#fafafa',
                                'cursor': 'pointer'
                            },
                            multiple=False,
                            accept='image/*'
                        ),
                        
                        # Image preview
                        html.Div(id='image-preview', className="mt-3"),
                        
                        # Process button
                        html.Div([
                            dbc.Button([
                                html.I(className="fas fa-magic me-2"),
                                "Extract Holdings"
                            ], id="btn-process-image", color="primary", size="lg", className="w-100 mt-3", disabled=True)
                        ]),
                        
                        # Processing indicator
                        html.Div(
                            id="processing-indicator",
                            children=[
                                dbc.Spinner(color="primary", size="sm"),
                                html.Span(" Analyzing image with AI...", className="ms-2")
                            ],
                            style={"display": "none"},
                            className="mt-3 text-center"
                        )
                    ])
                ], className="shadow-sm mb-4"),
                
                # Supported brokers info
                dbc.Card([
                    dbc.CardHeader([
                        html.H6([
                            html.I(className="fas fa-info-circle me-2"),
                            "Supported Broker Apps"
                        ], className="mb-0")
                    ]),
                    dbc.CardBody([
                        dbc.ListGroup([
                            dbc.ListGroupItem([
                                html.I(className="fas fa-check-circle text-success me-2"),
                                "IPOT (Indo Premier)"
                            ]),
                            dbc.ListGroupItem([
                                html.I(className="fas fa-check-circle text-success me-2"),
                                "Stockbit"
                            ]),
                            dbc.ListGroupItem([
                                html.I(className="fas fa-check-circle text-success me-2"),
                                "Ajaib"
                            ]),
                            dbc.ListGroupItem([
                                html.I(className="fas fa-check-circle text-success me-2"),
                                "Bibit Saham"
                            ]),
                            dbc.ListGroupItem([
                                html.I(className="fas fa-check-circle text-warning me-2"),
                                "Others (may work)"
                            ]),
                        ], flush=True)
                    ])
                ], className="shadow-sm")
            ], width=12, lg=5, className="mb-4"),
            
            # Right column - Preview and confirm
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([
                            html.I(className="fas fa-list-check me-2"),
                            "Step 2: Review & Import"
                        ], className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.Div(id="extraction-result")
                    ])
                ], className="shadow-sm h-100")
            ], width=12, lg=7)
        ]),
        
        # Tips card
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H6([
                                    html.I(className="fas fa-lightbulb me-2 text-warning"),
                                    "Tips for Best Results"
                                ])
                            ])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.Ul([
                                    html.Li("Ensure the screenshot is clear and not blurry"),
                                    html.Li("Capture the complete portfolio view with all stocks visible"),
                                ], className="mb-0 small")
                            ], width=6),
                            dbc.Col([
                                html.Ul([
                                    html.Li("Avoid screenshots with popup overlays"),
                                    html.Li("Make sure share counts and prices are fully visible")
                                ], className="mb-0 small")
                            ], width=6)
                        ])
                    ])
                ], className="shadow-sm mt-4", color="light")
            ])
        ])
    ], fluid=True),
    
    # Store for extracted data
    dcc.Store(id="store-extracted-holdings", data=None),
    
    # Hidden elements needed for callbacks (dynamically shown in extraction-result)
    html.Div([
        dbc.Button(id="btn-confirm-import", style={"display": "none"}),
        dcc.Checklist(id="import-replace-existing", options=[], value=[], style={"display": "none"})
    ], style={"display": "none"}),
    
    # Toast for notifications
    dbc.Toast(
        id="import-toast",
        header="Notification",
        is_open=False,
        dismissable=True,
        duration=4000,
        icon="success",
        style={"position": "fixed", "top": 80, "right": 20, "width": 350, "zIndex": 9999}
    )
])


def create_holdings_preview_table(holdings):
    """Create a preview table for extracted holdings"""
    if not holdings:
        return html.Div([
            html.I(className="fas fa-inbox fa-3x text-muted mb-3"),
            html.P("No holdings extracted yet.", className="text-muted")
        ], className="text-center py-5")
    
    rows = []
    for i, h in enumerate(holdings):
        rows.append(html.Tr([
            html.Td(dbc.Checkbox(id={"type": "holding-check", "index": i}, value=True)),
            html.Td(html.Strong(h.get("symbol", "N/A"))),
            html.Td(f"{h.get('shares', 0):,}"),
            html.Td(format_currency(h.get("avg_cost"))),
            html.Td(format_currency(h.get("current_price")) if h.get("current_price") else "-"),
            html.Td(
                html.Span(
                    f"{h.get('profit_loss_pct', 0):+.2f}%" if h.get('profit_loss_pct') else "-",
                    className="text-success" if h.get('profit_loss_pct', 0) >= 0 else "text-danger"
                )
            )
        ]))
    
    return dbc.Table([
        html.Thead(html.Tr([
            html.Th("", style={"width": "40px"}),
            html.Th("Symbol"),
            html.Th("Shares"),
            html.Th("Avg Cost"),
            html.Th("Current"),
            html.Th("P/L %")
        ])),
        html.Tbody(rows)
    ], striped=True, hover=True, size="sm", className="mb-0")


# Callbacks

@callback(
    [Output("image-preview", "children"),
     Output("btn-process-image", "disabled")],
    Input("upload-image", "contents"),
    State("upload-image", "filename"),
    prevent_initial_call=True
)
def show_image_preview(contents, filename):
    """Show preview of uploaded image"""
    if contents is None:
        return None, True
    
    # Display image preview
    preview = html.Div([
        html.Img(
            src=contents,
            style={
                "maxWidth": "100%",
                "maxHeight": "300px",
                "borderRadius": "8px",
                "border": "1px solid #ddd"
            }
        ),
        html.P([
            html.I(className="fas fa-file-image me-2"),
            filename
        ], className="text-muted small mt-2 mb-0")
    ], className="text-center")
    
    return preview, False


@callback(
    [Output("extraction-result", "children"),
     Output("store-extracted-holdings", "data"),
     Output("processing-indicator", "style"),
     Output("import-toast", "is_open"),
     Output("import-toast", "children"),
     Output("import-toast", "header"),
     Output("import-toast", "icon")],
    [Input("btn-process-image", "n_clicks"),
     Input("btn-confirm-import", "n_clicks")],
    [State("upload-image", "contents"),
     State("store-extracted-holdings", "data"),
     State("import-replace-existing", "value"),
     State("user-session", "data")],
    prevent_initial_call=True
)
def process_image_or_import(n_process, n_import, contents, stored_holdings, replace_existing, session):
    """Process uploaded image or confirm import"""
    triggered = ctx.triggered_id
    
    if not session or 'token' not in session:
        return (
            html.Div([
                dbc.Alert("Please login to import portfolio", color="warning")
            ]),
            None,
            {"display": "none"},
            True, "Please login first", "Error", "danger"
        )
    
    token = session['token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Handle import confirmation
    if triggered == "btn-confirm-import" and stored_holdings:
        try:
            # Prepare holdings for import
            holdings_to_import = [
                {
                    "symbol": h["symbol"],
                    "shares": h["shares"],
                    "avg_cost": h["avg_cost"],
                    "sector": h.get("sector")
                }
                for h in stored_holdings
            ]
            
            response = requests.post(
                f"{BACKEND_URL}/api/import/confirm",
                headers={**headers, "Content-Type": "application/json"},
                json={
                    "holdings": holdings_to_import,
                    "replace_existing": replace_existing or False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                success_msg = result.get("message", "Import successful!")
                
                # Show success result
                success_view = html.Div([
                    html.Div([
                        html.I(className="fas fa-check-circle fa-4x text-success mb-3"),
                        html.H4("Import Successful!", className="text-success"),
                        html.P(success_msg, className="text-muted"),
                        html.Hr(),
                        html.P([
                            html.Strong(f"{result.get('imported_count', 0)}"),
                            " new holdings imported, ",
                            html.Strong(f"{result.get('updated_count', 0)}"),
                            " updated"
                        ]),
                        dbc.Button([
                            html.I(className="fas fa-briefcase me-2"),
                            "View Portfolio"
                        ], href="/portfolio", color="primary", className="mt-3")
                    ], className="text-center py-4")
                ])
                
                return success_view, None, {"display": "none"}, True, success_msg, "Success", "success"
            else:
                error_msg = response.json().get("detail", "Import failed")
                return dash.no_update, dash.no_update, {"display": "none"}, True, error_msg, "Error", "danger"
                
        except Exception as e:
            return dash.no_update, dash.no_update, {"display": "none"}, True, str(e), "Error", "danger"
    
    # Handle image processing
    if triggered == "btn-process-image" and contents:
        try:
            # Parse base64 content
            content_type, content_string = contents.split(',')
            image_data = base64.b64decode(content_string)
            
            # Determine MIME type
            mime_type = "image/png"
            if "jpeg" in content_type or "jpg" in content_type:
                mime_type = "image/jpeg"
            elif "webp" in content_type:
                mime_type = "image/webp"
            
            # Send to backend
            files = {
                "file": ("screenshot.png", image_data, mime_type)
            }
            
            response = requests.post(
                f"{BACKEND_URL}/api/import/preview",
                headers=headers,
                files=files,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    holdings = result.get("holdings", [])
                    warnings = result.get("warnings", [])
                    suggestions = result.get("suggestions", [])
                    confidence = result.get("confidence", 0)
                    broker = result.get("broker_detected", "Unknown")
                    
                    # Build result view
                    result_view = html.Div([
                        # Stats row
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H3(str(len(holdings)), className="mb-0 text-primary"),
                                    html.Small("Holdings Found", className="text-muted")
                                ], className="text-center")
                            ], width=4),
                            dbc.Col([
                                html.Div([
                                    html.H3(f"{confidence*100:.0f}%", className="mb-0 text-success"),
                                    html.Small("Confidence", className="text-muted")
                                ], className="text-center")
                            ], width=4),
                            dbc.Col([
                                html.Div([
                                    html.H3(broker, className="mb-0"),
                                    html.Small("Broker", className="text-muted")
                                ], className="text-center")
                            ], width=4)
                        ], className="mb-4"),
                        
                        html.Hr(),
                        
                        # Warnings
                        html.Div([
                            dbc.Alert([
                                html.I(className="fas fa-exclamation-triangle me-2"),
                                warning
                            ], color="warning", className="py-2")
                            for warning in warnings
                        ]) if warnings else None,
                        
                        # Holdings table
                        html.Div([
                            html.H6([
                                html.I(className="fas fa-list me-2"),
                                "Extracted Holdings"
                            ], className="mb-3"),
                            create_holdings_preview_table(holdings)
                        ]),
                        
                        html.Hr(),
                        
                        # Import options
                        dbc.Checkbox(
                            id="import-replace-existing",
                            label="Replace all existing holdings (clear portfolio first)",
                            value=False,
                            className="mb-3"
                        ),
                        
                        # Confirm button
                        dbc.Button([
                            html.I(className="fas fa-check me-2"),
                            f"Import {len(holdings)} Holdings"
                        ], id="btn-confirm-import", color="success", size="lg", className="w-100",
                           disabled=len(holdings) == 0)
                    ])
                    
                    return result_view, holdings, {"display": "none"}, False, "", "", "info"
                else:
                    error_msg = result.get("error", "Could not extract portfolio data")
                    error_view = html.Div([
                        html.Div([
                            html.I(className="fas fa-times-circle fa-4x text-danger mb-3"),
                            html.H5("Extraction Failed", className="text-danger"),
                            html.P(error_msg, className="text-muted"),
                            html.Hr(),
                            html.P("Please try with a clearer screenshot.", className="small text-muted")
                        ], className="text-center py-4")
                    ])
                    return error_view, None, {"display": "none"}, True, error_msg, "Error", "warning"
            else:
                error_msg = response.json().get("detail", "Processing failed")
                return (
                    dbc.Alert(error_msg, color="danger"),
                    None,
                    {"display": "none"},
                    True, error_msg, "Error", "danger"
                )
                
        except Exception as e:
            return (
                dbc.Alert(f"Error: {str(e)}", color="danger"),
                None,
                {"display": "none"},
                True, str(e), "Error", "danger"
            )
    
    # Default: show empty state
    return (
        html.Div([
            html.Div([
                html.I(className="fas fa-image fa-4x text-muted mb-3"),
                html.H5("Upload a Screenshot", className="text-muted"),
                html.P("Your extracted holdings will appear here.", className="text-muted small")
            ], className="text-center py-5")
        ]),
        None,
        {"display": "none"},
        False, "", "", "info"
    )


# Logout callback
@callback(
    [Output("url", "pathname", allow_duplicate=True),
     Output("user-session", "data", allow_duplicate=True)],
    Input("logout-btn-import", "n_clicks"),
    prevent_initial_call=True
)
def handle_logout_import(n_clicks):
    """Handle logout from import page"""
    if n_clicks:
        return "/login", None
    return dash.no_update, dash.no_update
