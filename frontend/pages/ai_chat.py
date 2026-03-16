import dash
from dash import html, dcc, Input, Output, State, callback, ctx
import dash_bootstrap_components as dbc
import requests
import os
import json
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
            dbc.NavbarToggler(id="navbar-toggler-ai"),
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
                    ], href="/ai", active=True)),
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
                            ], id="logout-btn-ai")
                        ],
                        label="Account",
                        nav=True,
                        in_navbar=True
                    )
                ], className="ms-auto", navbar=True),
                id="navbar-collapse-ai",
                navbar=True
            )
        ], fluid=True),
        color="dark",
        dark=True,
        className="mb-4",
        sticky="top"
    )


def create_message_bubble(content, is_user=False, timestamp=None):
    """Create a chat message bubble"""
    if is_user:
        return html.Div([
            html.Div([
                html.Div(content, className="p-3 rounded-3 bg-primary text-white"),
                html.Small(timestamp or "", className="text-muted mt-1 d-block text-end")
            ], className="d-flex flex-column align-items-end", style={"maxWidth": "80%"})
        ], className="d-flex justify-content-end mb-3")
    else:
        return html.Div([
            html.Div([
                html.I(className="fas fa-robot fa-lg text-info me-2")
            ], className="flex-shrink-0"),
            html.Div([
                html.Div([
                    dcc.Markdown(content, className="mb-0")
                ], className="p-3 rounded-3 bg-light"),
                html.Small(timestamp or "", className="text-muted mt-1 d-block")
            ], style={"maxWidth": "80%"})
        ], className="d-flex mb-3")


def create_quick_action_button(icon, label, action_id):
    """Create a quick action button"""
    return dbc.Button([
        html.I(className=f"fas {icon} me-2"),
        label
    ], id=action_id, color="outline-primary", size="sm", className="me-2 mb-2")


# AI Chat page layout
ai_chat_layout = html.Div([
    create_navbar(),
    
    dbc.Container([
        dbc.Row([
            # Main chat area
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        dbc.Row([
                            dbc.Col([
                                html.H5([
                                    html.I(className="fas fa-robot me-2 text-info"),
                                    "AI Investment Assistant"
                                ], className="mb-0")
                            ]),
                            dbc.Col([
                                dbc.Button([
                                    html.I(className="fas fa-trash-alt me-1"),
                                    "Clear Chat"
                                ], id="btn-clear-chat", color="outline-danger", size="sm", className="float-end")
                            ])
                        ])
                    ]),
                    dbc.CardBody([
                        # Quick actions
                        html.Div([
                            html.P("Quick Actions:", className="text-muted small mb-2"),
                            create_quick_action_button("fa-chart-pie", "Analyze Portfolio", "btn-analyze-portfolio"),
                            create_quick_action_button("fa-search-dollar", "Stock Analysis", "btn-stock-analysis"),
                            create_quick_action_button("fa-bullseye", "Entry Strategy", "btn-entry-strategy"),
                            create_quick_action_button("fa-lightbulb", "Market Insights", "btn-market-insights"),
                        ], className="mb-3 p-3 bg-light rounded"),
                        
                        # Chat messages container
                        html.Div(
                            id="chat-messages",
                            className="overflow-auto",
                            style={"height": "400px", "overflowY": "auto"}
                        ),
                        
                        # Loading indicator
                        html.Div(
                            id="chat-loading",
                            children=[
                                dbc.Spinner(color="primary", size="sm"),
                                html.Span(" AI is thinking...", className="ms-2 text-muted")
                            ],
                            style={"display": "none"},
                            className="mb-3"
                        ),
                        
                        # Input area
                        html.Hr(),
                        dbc.InputGroup([
                            dbc.Textarea(
                                id="chat-input",
                                placeholder="Ask me anything about investing, your portfolio, or specific stocks...",
                                style={"resize": "none"},
                                rows=2
                            ),
                            dbc.Button([
                                html.I(className="fas fa-paper-plane")
                            ], id="btn-send-message", color="primary", className="px-4")
                        ]),
                        html.Small([
                            html.I(className="fas fa-info-circle me-1"),
                            "Your portfolio context is automatically included for personalized advice."
                        ], className="text-muted mt-2 d-block")
                    ])
                ], className="shadow-sm h-100")
            ], width=12, lg=8, className="mb-4"),
            
            # Sidebar
            dbc.Col([
                # AI Insights Card
                dbc.Card([
                    dbc.CardHeader([
                        html.H6([
                            html.I(className="fas fa-lightbulb me-2 text-warning"),
                            "AI Insights"
                        ], className="mb-0")
                    ]),
                    dbc.CardBody([
                        dbc.Spinner([
                            html.Div(id="ai-insights-sidebar")
                        ], color="primary", size="sm")
                    ])
                ], className="shadow-sm mb-4"),
                
                # Recent Queries Card
                dbc.Card([
                    dbc.CardHeader([
                        html.H6([
                            html.I(className="fas fa-history me-2"),
                            "Recent Queries"
                        ], className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.Div(id="recent-queries-list")
                    ], style={"maxHeight": "300px", "overflowY": "auto"})
                ], className="shadow-sm mb-4"),
                
                # Tips Card
                dbc.Card([
                    dbc.CardHeader([
                        html.H6([
                            html.I(className="fas fa-question-circle me-2 text-info"),
                            "Tips"
                        ], className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.Ul([
                            html.Li("Ask about specific stocks: 'Analyze BBCA'", className="small mb-2"),
                            html.Li("Get entry strategies: 'Entry strategy for BBRI with 10M budget'", className="small mb-2"),
                            html.Li("Portfolio advice: 'Should I rebalance?'", className="small mb-2"),
                            html.Li("Market insights: 'How is the banking sector?'", className="small mb-2"),
                        ], className="mb-0 ps-3")
                    ])
                ], className="shadow-sm")
            ], width=12, lg=4)
        ])
    ], fluid=True),
    
    # Store for conversation history
    dcc.Store(id="store-conversation", data=[]),
    
    # Stock analysis modal
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Stock Analysis")),
        dbc.ModalBody([
            dbc.Label("Enter stock symbol:"),
            dbc.Input(id="input-stock-symbol", type="text", placeholder="e.g., BBCA"),
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="btn-cancel-stock", color="secondary"),
            dbc.Button("Analyze", id="btn-confirm-stock", color="primary")
        ])
    ], id="modal-stock-analysis", is_open=False),
    
    # Entry strategy modal
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Entry Strategy")),
        dbc.ModalBody([
            dbc.Label("Stock Symbol:"),
            dbc.Input(id="input-entry-symbol", type="text", placeholder="e.g., BBRI", className="mb-3"),
            dbc.Label("Investment Amount (Rp):"),
            dbc.Input(id="input-entry-capital", type="number", placeholder="e.g., 10000000", min=100000),
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="btn-cancel-entry", color="secondary"),
            dbc.Button("Get Strategy", id="btn-confirm-entry", color="primary")
        ])
    ], id="modal-entry-strategy", is_open=False),
])


# Callbacks

@callback(
    [Output("chat-messages", "children"),
     Output("store-conversation", "data"),
     Output("chat-input", "value"),
     Output("chat-loading", "style")],
    [Input("btn-send-message", "n_clicks"),
     Input("btn-analyze-portfolio", "n_clicks"),
     Input("btn-market-insights", "n_clicks"),
     Input("btn-confirm-stock", "n_clicks"),
     Input("btn-confirm-entry", "n_clicks"),
     Input("btn-clear-chat", "n_clicks")],
    [State("chat-input", "value"),
     State("store-conversation", "data"),
     State("user-session", "data"),
     State("input-stock-symbol", "value"),
     State("input-entry-symbol", "value"),
     State("input-entry-capital", "value")],
    prevent_initial_call=True
)
def handle_chat(
    n_send, n_analyze, n_market, n_stock, n_entry, n_clear,
    message, conversation, session, stock_symbol, entry_symbol, entry_capital
):
    """Handle all chat interactions"""
    triggered = ctx.triggered_id
    
    if not session or 'token' not in session:
        return [create_message_bubble("Please login to use the AI assistant.", False)], [], "", {"display": "none"}
    
    token = session['token']
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Handle clear chat
    if triggered == "btn-clear-chat":
        welcome_msg = create_message_bubble(
            "Hello! I'm your AI investment assistant. I can help you with:\n\n"
            "- **Portfolio Analysis** - Get insights on your holdings\n"
            "- **Stock Research** - Analyze specific IDX stocks\n"
            "- **Entry Strategies** - Plan your stock purchases\n"
            "- **Market Insights** - Understand market conditions\n\n"
            "How can I help you today?",
            False,
            datetime.now().strftime("%H:%M")
        )
        return [welcome_msg], [], "", {"display": "none"}
    
    # Show loading
    loading_style = {"display": "block"}
    
    # Build current messages display
    messages_display = []
    for msg in conversation:
        messages_display.append(
            create_message_bubble(msg["content"], msg["role"] == "user", msg.get("timestamp"))
        )
    
    # Determine the query
    query = None
    analysis_type = None
    
    if triggered == "btn-send-message" and message:
        query = message
    elif triggered == "btn-analyze-portfolio":
        query = "Please analyze my portfolio"
        analysis_type = "portfolio"
    elif triggered == "btn-market-insights":
        query = "What are the current market insights for Indonesian stocks? What sectors look promising?"
    elif triggered == "btn-confirm-stock" and stock_symbol:
        query = f"Analyze {stock_symbol} stock"
        analysis_type = "stock"
    elif triggered == "btn-confirm-entry" and entry_symbol and entry_capital:
        query = f"Entry strategy for {entry_symbol}"
        analysis_type = "entry_strategy"
    
    if not query:
        return messages_display, conversation, "", {"display": "none"}
    
    # Add user message
    user_msg = {
        "role": "user",
        "content": query,
        "timestamp": datetime.now().strftime("%H:%M")
    }
    conversation.append(user_msg)
    messages_display.append(create_message_bubble(query, True, user_msg["timestamp"]))
    
    try:
        # Call AI API
        if analysis_type:
            payload = {
                "analysis_type": analysis_type,
                "symbol": stock_symbol or entry_symbol,
                "capital": float(entry_capital) if entry_capital else None
            }
            response = requests.post(
                f"{BACKEND_URL}/api/ai/analyze",
                headers=headers,
                json=payload,
                timeout=60
            )
        else:
            payload = {
                "message": query,
                "conversation_history": [{"role": m["role"], "content": m["content"]} for m in conversation[:-1]],
                "include_portfolio": True
            }
            response = requests.post(
                f"{BACKEND_URL}/api/ai/chat",
                headers=headers,
                json=payload,
                timeout=60
            )
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data.get("response", "Sorry, I couldn't generate a response.")
            
            # Add AI response
            ai_msg = {
                "role": "assistant",
                "content": ai_response,
                "timestamp": datetime.now().strftime("%H:%M")
            }
            conversation.append(ai_msg)
            messages_display.append(create_message_bubble(ai_response, False, ai_msg["timestamp"]))
        else:
            error_msg = "Sorry, there was an error processing your request."
            messages_display.append(create_message_bubble(error_msg, False, datetime.now().strftime("%H:%M")))
            
    except requests.exceptions.Timeout:
        messages_display.append(create_message_bubble(
            "Request timed out. The AI is taking too long to respond. Please try again.",
            False, datetime.now().strftime("%H:%M")
        ))
    except Exception as e:
        messages_display.append(create_message_bubble(
            f"Error: {str(e)}", False, datetime.now().strftime("%H:%M")
        ))
    
    return messages_display, conversation, "", {"display": "none"}


@callback(
    Output("modal-stock-analysis", "is_open"),
    [Input("btn-stock-analysis", "n_clicks"),
     Input("btn-cancel-stock", "n_clicks"),
     Input("btn-confirm-stock", "n_clicks")],
    [State("modal-stock-analysis", "is_open")],
    prevent_initial_call=True
)
def toggle_stock_modal(n_open, n_cancel, n_confirm, is_open):
    """Toggle stock analysis modal"""
    return not is_open


@callback(
    Output("modal-entry-strategy", "is_open"),
    [Input("btn-entry-strategy", "n_clicks"),
     Input("btn-cancel-entry", "n_clicks"),
     Input("btn-confirm-entry", "n_clicks")],
    [State("modal-entry-strategy", "is_open")],
    prevent_initial_call=True
)
def toggle_entry_modal(n_open, n_cancel, n_confirm, is_open):
    """Toggle entry strategy modal"""
    return not is_open


@callback(
    Output("ai-insights-sidebar", "children"),
    [Input("url", "pathname")],
    [State("user-session", "data")],
    prevent_initial_call=False
)
def load_ai_insights(pathname, session):
    """Load AI insights for sidebar"""
    if pathname != "/ai":
        return dash.no_update
    
    if not session or 'token' not in session:
        return html.P("Login to see insights", className="text-muted small")
    
    token = session['token']
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/ai/insights",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            insights = response.json()
            
            if not insights:
                return html.P("No insights available", className="text-muted small")
            
            insight_cards = []
            for insight in insights:
                icon_class = "fa-exclamation-triangle text-warning"
                if insight["type"] == "opportunity":
                    icon_class = "fa-arrow-up text-success"
                elif insight["type"] == "info":
                    icon_class = "fa-info-circle text-info"
                
                insight_cards.append(
                    html.Div([
                        html.Div([
                            html.I(className=f"fas {icon_class} me-2"),
                            html.Strong(insight["title"])
                        ]),
                        html.P(insight["description"], className="small text-muted mb-0")
                    ], className="mb-3 pb-2 border-bottom")
                )
            
            return html.Div(insight_cards)
        
        return html.P("Could not load insights", className="text-muted small")
        
    except Exception as e:
        return html.P(f"Error: {str(e)}", className="text-danger small")


@callback(
    Output("recent-queries-list", "children"),
    [Input("url", "pathname")],
    [State("user-session", "data")],
    prevent_initial_call=False
)
def load_recent_queries(pathname, session):
    """Load recent AI queries"""
    if pathname != "/ai":
        return dash.no_update
    
    if not session or 'token' not in session:
        return html.P("Login to see history", className="text-muted small")
    
    token = session['token']
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/ai/history?limit=5",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            queries = response.json()
            
            if not queries:
                return html.P("No queries yet", className="text-muted small")
            
            query_items = []
            for q in queries:
                query_items.append(
                    html.Div([
                        html.Small(q["query"][:50] + "..." if len(q["query"]) > 50 else q["query"], 
                                  className="fw-bold"),
                        html.Br(),
                        html.Small(q.get("created_at", "")[:10] if q.get("created_at") else "", 
                                  className="text-muted")
                    ], className="mb-2 pb-2 border-bottom")
                )
            
            return html.Div(query_items)
        
        return html.P("Could not load history", className="text-muted small")
        
    except Exception as e:
        return html.P("Error loading history", className="text-muted small")


# Logout callback
@callback(
    [Output("url", "pathname", allow_duplicate=True),
     Output("user-session", "data", allow_duplicate=True)],
    Input("logout-btn-ai", "n_clicks"),
    prevent_initial_call=True
)
def handle_logout_ai(n_clicks):
    """Handle logout from AI page"""
    if n_clicks:
        return "/login", None
    return dash.no_update, dash.no_update
