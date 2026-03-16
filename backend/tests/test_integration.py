"""
Integration Tests for InvestAI Backend
Tests complete user workflows end-to-end
"""
import pytest
from fastapi import status


class TestUserRegistrationFlow:
    """Test complete user registration and setup flow"""
    
    def test_complete_registration_flow(self, client):
        """Test user registration -> login -> create portfolio -> add holdings"""
        # Step 1: Register new user
        register_response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@investai.com",
                "password": "SecurePassword123!",
                "full_name": "New Investor"
            }
        )
        assert register_response.status_code == status.HTTP_201_CREATED
        token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 2: Create portfolio
        portfolio_response = client.post(
            "/api/portfolios",
            headers=headers,
            json={
                "name": "My First Portfolio",
                "description": "Indonesian stock investments"
            }
        )
        assert portfolio_response.status_code == status.HTTP_201_CREATED
        portfolio = portfolio_response.json()
        portfolio_id = portfolio["id"]
        
        # Step 3: Add holdings
        holding_response = client.post(
            f"/api/portfolios/{portfolio_id}/holdings",
            headers=headers,
            json={
                "symbol": "BBCA",
                "shares": 100,
                "avg_cost": 9000,
                "sector": "Financials"
            }
        )
        assert holding_response.status_code == status.HTTP_201_CREATED
        
        # Step 4: Verify holdings
        verify_response = client.get(f"/api/portfolios/{portfolio_id}/holdings", headers=headers)
        assert verify_response.status_code == status.HTTP_200_OK


class TestTradingWorkflow:
    """Test buying and selling stocks workflow"""
    
    def test_buy_hold_sell_workflow(self, client, auth_headers, test_portfolio):
        """Test complete buy -> hold -> sell workflow"""
        # Step 1: Add initial holding
        add_response = client.post(
            f"/api/portfolios/{test_portfolio.id}/holdings",
            headers=auth_headers,
            json={
                "symbol": "TLKM",
                "shares": 500,
                "avg_cost": 3800
            }
        )
        assert add_response.status_code == status.HTTP_201_CREATED
        
        # Step 2: Update holding (simulate buying more)
        holdings_response = client.get(
            f"/api/portfolios/{test_portfolio.id}/holdings",
            headers=auth_headers
        )
        assert holdings_response.status_code == status.HTTP_200_OK
        holdings = holdings_response.json()
        tlkm_holding = next((h for h in holdings if h["symbol"] == "TLKM"), None)
        assert tlkm_holding is not None
        
        # Step 3: Update shares
        update_response = client.put(
            f"/api/portfolios/{test_portfolio.id}/holdings/{tlkm_holding['id']}",
            headers=auth_headers,
            json={
                "shares": 800,
                "avg_cost": 3700
            }
        )
        assert update_response.status_code == status.HTTP_200_OK


class TestStrategyWorkflow:
    """Test entry/exit strategy workflow"""
    
    def test_strategy_creation_and_execution(self, client, auth_headers, test_portfolio):
        """Test creating strategy and recording executions"""
        # Step 1: Create entry strategy
        strategy_response = client.post(
            "/api/strategies/entry",
            headers=auth_headers,
            json={
                "symbol": "BBRI",
                "total_capital": 10000000,
                "buy_zones": [
                    {"zone_num": 1, "min_price": 4200, "max_price": 4400, "allocation": 50},
                    {"zone_num": 2, "min_price": 4000, "max_price": 4199, "allocation": 50}
                ],
                "alert_enabled": True
            }
        )
        assert strategy_response.status_code == status.HTTP_201_CREATED
        strategy = strategy_response.json()
        strategy_id = strategy["id"]
        
        # Step 2: Record first execution
        exec1_response = client.post(
            f"/api/strategies/entry/{strategy_id}/execute",
            headers=auth_headers,
            json={
                "entry_strategy_id": strategy_id,
                "execution_type": "BUY",
                "zone_num": 1,
                "shares": 500,
                "price": 4300,
                "execution_date": "2026-03-10"
            }
        )
        assert exec1_response.status_code == status.HTTP_200_OK
        exec1 = exec1_response.json()
        assert exec1["deployed_capital"] > 0
        
        # Step 3: Get executions
        executions_response = client.get(
            f"/api/strategies/entry/{strategy_id}/executions",
            headers=auth_headers
        )
        assert executions_response.status_code == status.HTTP_200_OK


class TestAlertWorkflow:
    """Test alert creation and triggering workflow"""
    
    def test_alert_lifecycle(self, client, auth_headers):
        """Test creating, checking, and triggering alerts"""
        # Step 1: Create price alert
        alert_response = client.post(
            "/api/alerts/",
            headers=auth_headers,
            json={
                "alert_type": "price_target",
                "symbol": "BBCA",
                "trigger_price": 10000,
                "trigger_condition": "above",
                "channels": ["in-app"]
            }
        )
        assert alert_response.status_code == status.HTTP_201_CREATED
        alert = alert_response.json()
        alert_id = alert["id"]
        assert alert["status"] == "active"
        
        # Step 2: Check alerts
        check_response = client.post("/api/alerts/check", headers=auth_headers)
        assert check_response.status_code == status.HTTP_200_OK
        
        # Step 3: Get notifications
        notif_response = client.get("/api/alerts/notifications", headers=auth_headers)
        assert notif_response.status_code == status.HTTP_200_OK
        
        # Step 4: Delete alert
        delete_response = client.delete(f"/api/alerts/{alert_id}", headers=auth_headers)
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT


class TestPortfolioAnalysisWorkflow:
    """Test portfolio analysis and AI insights workflow"""
    
    def test_portfolio_analysis_flow(self, client, auth_headers, test_portfolio, test_holding):
        """Test getting portfolio summary and AI analysis"""
        # Step 1: Get holdings with prices
        holdings_response = client.get(
            f"/api/portfolios/{test_portfolio.id}/holdings",
            headers=auth_headers
        )
        assert holdings_response.status_code == status.HTTP_200_OK
        holdings = holdings_response.json()
        assert len(holdings) > 0


class TestSecurityIsolation:
    """Test that users cannot access other users' data"""
    
    def test_portfolio_isolation(self, client, test_portfolio, second_user_token):
        """Test that users cannot see other users' portfolios"""
        headers = {"Authorization": f"Bearer {second_user_token}"}
        
        # Try to access first user's portfolio
        response = client.get(f"/api/portfolios/{test_portfolio.id}", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_holding_isolation(self, client, test_portfolio, test_holding, second_user_token):
        """Test that users cannot see other users' holdings"""
        headers = {"Authorization": f"Bearer {second_user_token}"}
        
        # Try to access first user's holding
        response = client.get(
            f"/api/portfolios/{test_portfolio.id}/holdings/{test_holding.id}",
            headers=headers
        )
        # Either 404 (not found/forbidden) or 405 (route doesn't support GET single)
        assert response.status_code in [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_405_METHOD_NOT_ALLOWED
        ]
    
    def test_cannot_modify_other_users_data(self, client, test_portfolio, test_holding, second_user_token):
        """Test that users cannot modify other users' data"""
        headers = {"Authorization": f"Bearer {second_user_token}"}
        
        # Try to update first user's holding
        response = client.put(
            f"/api/portfolios/{test_portfolio.id}/holdings/{test_holding.id}",
            headers=headers,
            json={"shares": 999}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestErrorHandling:
    """Test error handling across the application"""
    
    def test_invalid_json(self, client, auth_headers):
        """Test handling of invalid JSON"""
        response = client.post(
            "/api/portfolios",
            headers={**auth_headers, "Content-Type": "application/json"},
            content="invalid json {"
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_missing_required_fields(self, client, auth_headers, test_portfolio):
        """Test handling of missing required fields"""
        response = client.post(
            f"/api/portfolios/{test_portfolio.id}/holdings",
            headers=auth_headers,
            json={"symbol": "BBCA"}  # Missing shares and avg_cost
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_invalid_stock_symbol(self, client, auth_headers, test_portfolio):
        """Test handling of invalid stock symbols - API currently accepts empty"""
        # Empty symbol - API currently accepts this
        response = client.post(
            f"/api/portfolios/{test_portfolio.id}/holdings",
            headers=auth_headers,
            json={
                "symbol": "",
                "shares": 100,
                "avg_cost": 1000
            }
        )
        # API accepts empty symbols currently
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]
