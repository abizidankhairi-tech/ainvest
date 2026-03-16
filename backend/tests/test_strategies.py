"""
Tests for Strategies and Alerts API
"""
import pytest
from fastapi import status


class TestEntryStrategies:
    """Tests for entry strategy endpoints"""
    
    def test_create_entry_strategy_success(self, client, auth_headers, test_portfolio):
        """Test creating an entry strategy"""
        response = client.post(
            "/api/strategies/entry",
            headers=auth_headers,
            json={
                "symbol": "BBRI",
                "total_capital": 10000000,
                "buy_zones": [
                    {"zone_num": 1, "min_price": 4200, "max_price": 4400, "allocation": 40},
                    {"zone_num": 2, "min_price": 4000, "max_price": 4199, "allocation": 35},
                    {"zone_num": 3, "min_price": 3800, "max_price": 3999, "allocation": 25}
                ],
                "alert_enabled": True
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["symbol"] == "BBRI"
        assert data["total_capital"] == 10000000
        assert data["status"] == "active"
        assert len(data["buy_zones"]) == 3
    
    def test_create_entry_strategy_invalid_allocation(self, client, auth_headers, test_portfolio):
        """Test creating entry strategy with invalid allocation (not 100%)"""
        response = client.post(
            "/api/strategies/entry",
            headers=auth_headers,
            json={
                "symbol": "BBCA",
                "total_capital": 5000000,
                "buy_zones": [
                    {"zone_num": 1, "min_price": 9000, "max_price": 9200, "allocation": 50},
                    {"zone_num": 2, "min_price": 8800, "max_price": 8999, "allocation": 30}
                    # Total = 80%, not 100%
                ],
                "alert_enabled": True
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "100%" in response.json()["detail"]
    
    def test_get_entry_strategies(self, client, auth_headers, test_portfolio):
        """Test getting entry strategies"""
        # First create one
        client.post(
            "/api/strategies/entry",
            headers=auth_headers,
            json={
                "symbol": "TLKM",
                "total_capital": 5000000,
                "buy_zones": [
                    {"zone_num": 1, "min_price": 3700, "max_price": 3900, "allocation": 100}
                ],
                "alert_enabled": True
            }
        )
        
        response = client.get("/api/strategies/entry", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_entry_strategy_by_id(self, client, auth_headers, test_portfolio):
        """Test getting a specific entry strategy"""
        # Create one first
        create_response = client.post(
            "/api/strategies/entry",
            headers=auth_headers,
            json={
                "symbol": "ASII",
                "total_capital": 8000000,
                "buy_zones": [
                    {"zone_num": 1, "min_price": 5000, "max_price": 5200, "allocation": 100}
                ],
                "alert_enabled": True
            }
        )
        strategy_id = create_response.json()["id"]
        
        response = client.get(
            f"/api/strategies/entry/{strategy_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["symbol"] == "ASII"
    
    def test_update_entry_strategy(self, client, auth_headers, test_portfolio):
        """Test updating an entry strategy"""
        # Create one first
        create_response = client.post(
            "/api/strategies/entry",
            headers=auth_headers,
            json={
                "symbol": "BMRI",
                "total_capital": 6000000,
                "buy_zones": [
                    {"zone_num": 1, "min_price": 5500, "max_price": 5700, "allocation": 100}
                ],
                "alert_enabled": True
            }
        )
        strategy_id = create_response.json()["id"]
        
        response = client.put(
            f"/api/strategies/entry/{strategy_id}?status_update=completed",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_delete_entry_strategy(self, client, auth_headers, test_portfolio):
        """Test deleting an entry strategy"""
        # Create one first
        create_response = client.post(
            "/api/strategies/entry",
            headers=auth_headers,
            json={
                "symbol": "UNVR",
                "total_capital": 3000000,
                "buy_zones": [
                    {"zone_num": 1, "min_price": 4000, "max_price": 4200, "allocation": 100}
                ],
                "alert_enabled": True
            }
        )
        strategy_id = create_response.json()["id"]
        
        response = client.delete(
            f"/api/strategies/entry/{strategy_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestExitStrategies:
    """Tests for exit strategy endpoints"""
    
    def test_create_exit_strategy_success(self, client, auth_headers, test_holding):
        """Test creating an exit strategy"""
        response = client.post(
            "/api/strategies/exit",
            headers=auth_headers,
            json={
                "holding_id": test_holding.id,
                "tp1_price": 10000,
                "tp1_allocation": 30,
                "tp2_price": 11000,
                "tp2_allocation": 40,
                "tp3_price": 12000,
                "tp3_allocation": 30,
                "stop_loss": 8000,
                "alert_enabled": True
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["symbol"] == "BBCA"
        assert data["tp1_price"] == 10000
        assert data["stop_loss"] == 8000
    
    def test_create_exit_strategy_nonexistent_holding(self, client, auth_headers):
        """Test creating exit strategy for non-existent holding"""
        response = client.post(
            "/api/strategies/exit",
            headers=auth_headers,
            json={
                "holding_id": 99999,
                "tp1_price": 10000,
                "tp1_allocation": 100,
                "alert_enabled": True
            }
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_exit_strategies(self, client, auth_headers, test_holding):
        """Test getting exit strategies"""
        # Create one first
        client.post(
            "/api/strategies/exit",
            headers=auth_headers,
            json={
                "holding_id": test_holding.id,
                "tp1_price": 10000,
                "tp1_allocation": 100,
                "alert_enabled": True
            }
        )
        
        response = client.get("/api/strategies/exit", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_delete_exit_strategy(self, client, auth_headers, test_holding):
        """Test deleting an exit strategy"""
        # Create one first
        create_response = client.post(
            "/api/strategies/exit",
            headers=auth_headers,
            json={
                "holding_id": test_holding.id,
                "tp1_price": 10000,
                "tp1_allocation": 100,
                "alert_enabled": True
            }
        )
        strategy_id = create_response.json()["id"]
        
        response = client.delete(
            f"/api/strategies/exit/{strategy_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestAlerts:
    """Tests for alerts endpoints"""
    
    def test_create_alert_success(self, client, auth_headers):
        """Test creating a price alert"""
        response = client.post(
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
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["symbol"] == "BBCA"
        assert data["trigger_price"] == 10000
        assert data["status"] == "active"
    
    def test_create_alert_invalid_type(self, client, auth_headers):
        """Test creating alert with invalid type"""
        response = client.post(
            "/api/alerts/",
            headers=auth_headers,
            json={
                "alert_type": "invalid_type",
                "symbol": "BBCA",
                "trigger_price": 10000,
                "trigger_condition": "above"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_alert_invalid_condition(self, client, auth_headers):
        """Test creating alert with invalid condition"""
        response = client.post(
            "/api/alerts/",
            headers=auth_headers,
            json={
                "alert_type": "price_target",
                "symbol": "BBCA",
                "trigger_price": 10000,
                "trigger_condition": "invalid"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_get_alerts(self, client, auth_headers):
        """Test getting user's alerts"""
        # Create an alert first
        client.post(
            "/api/alerts/",
            headers=auth_headers,
            json={
                "alert_type": "stop_loss",
                "symbol": "BBRI",
                "trigger_price": 4000,
                "trigger_condition": "below"
            }
        )
        
        response = client.get("/api/alerts/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_alerts_filtered(self, client, auth_headers):
        """Test getting alerts with status filter"""
        # Create an alert
        client.post(
            "/api/alerts/",
            headers=auth_headers,
            json={
                "alert_type": "price_above",
                "symbol": "TLKM",
                "trigger_price": 4000,
                "trigger_condition": "above"
            }
        )
        
        response = client.get(
            "/api/alerts/?status_filter=active",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_update_alert(self, client, auth_headers):
        """Test updating an alert"""
        # Create an alert first
        create_response = client.post(
            "/api/alerts/",
            headers=auth_headers,
            json={
                "alert_type": "price_target",
                "symbol": "ASII",
                "trigger_price": 5500,
                "trigger_condition": "above"
            }
        )
        alert_id = create_response.json()["id"]
        
        response = client.put(
            f"/api/alerts/{alert_id}?trigger_price=6000",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_delete_alert(self, client, auth_headers):
        """Test deleting an alert"""
        # Create an alert first
        create_response = client.post(
            "/api/alerts/",
            headers=auth_headers,
            json={
                "alert_type": "stop_loss",
                "symbol": "UNVR",
                "trigger_price": 3500,
                "trigger_condition": "below"
            }
        )
        alert_id = create_response.json()["id"]
        
        response = client.delete(
            f"/api/alerts/{alert_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
    
    def test_check_alerts(self, client, auth_headers):
        """Test checking alerts against current prices"""
        response = client.post("/api/alerts/check", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "triggered" in data
        assert "checked" in data


class TestNotifications:
    """Tests for notification endpoints"""
    
    def test_get_notifications(self, client, auth_headers):
        """Test getting user notifications"""
        response = client.get("/api/alerts/notifications", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_unread_count(self, client, auth_headers):
        """Test getting unread notification count"""
        response = client.get("/api/alerts/notifications/count", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "unread_count" in data
    
    def test_mark_all_notifications_read(self, client, auth_headers):
        """Test marking all notifications as read"""
        response = client.put(
            "/api/alerts/notifications/read-all",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
