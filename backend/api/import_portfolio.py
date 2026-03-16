"""
API endpoints for portfolio image import
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from database import get_db
from models.user import User
from models.portfolio import Portfolio
from models.holding import Holding
from api.auth import get_current_user
from services.image_import_service import image_import_service

router = APIRouter(prefix="/api/import", tags=["import"])

# Maximum file size (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024

# Allowed image types
ALLOWED_TYPES = ["image/png", "image/jpeg", "image/jpg", "image/webp"]


class ImportPreviewResponse(BaseModel):
    success: bool
    broker_detected: Optional[str] = None
    holdings: List[dict] = []
    holdings_count: int = 0
    warnings: List[str] = []
    suggestions: List[str] = []
    total_value: Optional[float] = None
    confidence: float = 0
    response_time_ms: int = 0
    ready_to_import: bool = False
    error: Optional[str] = None


class HoldingImport(BaseModel):
    symbol: str
    shares: int
    avg_cost: float
    sector: Optional[str] = None


class ImportConfirmRequest(BaseModel):
    holdings: List[HoldingImport]
    replace_existing: bool = False  # If True, clears existing holdings first


class ImportConfirmResponse(BaseModel):
    success: bool
    imported_count: int
    skipped_count: int
    updated_count: int
    message: str
    holdings: List[dict] = []


def get_user_portfolio(user_id: int, db: Session) -> Portfolio:
    """Get or create user's active portfolio"""
    portfolio = db.query(Portfolio).filter(
        Portfolio.user_id == user_id,
        Portfolio.is_active == True
    ).first()
    
    if not portfolio:
        # Create a default portfolio
        portfolio = Portfolio(
            user_id=user_id,
            name="My Portfolio",
            description="Imported portfolio",
            is_active=True
        )
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)
    
    return portfolio


@router.post("/preview", response_model=ImportPreviewResponse)
async def preview_import(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a portfolio screenshot and get a preview of extracted data.
    
    Supported formats: PNG, JPEG, WebP
    Maximum file size: 5MB
    
    Returns extracted holdings for user review before confirming import.
    """
    # Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type: {file.content_type}. Allowed: {', '.join(ALLOWED_TYPES)}"
        )
    
    # Read file content
    content = await file.read()
    
    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Process image
    result = image_import_service.preview_import(
        image_data=content,
        image_type=file.content_type
    )
    
    return ImportPreviewResponse(**result)


@router.post("/confirm", response_model=ImportConfirmResponse)
def confirm_import(
    import_data: ImportConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Confirm and execute the portfolio import.
    
    Takes the reviewed holdings from preview and imports them into the user's portfolio.
    
    Options:
    - replace_existing: If True, clears all existing holdings before import
    """
    if not import_data.holdings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No holdings to import"
        )
    
    # Get or create portfolio
    portfolio = get_user_portfolio(current_user.id, db)
    
    imported_count = 0
    skipped_count = 0
    updated_count = 0
    
    try:
        # Clear existing holdings if requested
        if import_data.replace_existing:
            db.query(Holding).filter(Holding.portfolio_id == portfolio.id).delete()
            db.commit()
        
        # Process each holding
        for h in import_data.holdings:
            symbol = h.symbol.upper().strip()
            
            if not symbol or h.shares <= 0 or h.avg_cost <= 0:
                skipped_count += 1
                continue
            
            # Check if holding already exists
            existing = db.query(Holding).filter(
                Holding.portfolio_id == portfolio.id,
                Holding.symbol == symbol
            ).first()
            
            if existing:
                if import_data.replace_existing:
                    # This shouldn't happen since we deleted all, but just in case
                    existing.shares = h.shares
                    existing.avg_cost = h.avg_cost
                    if h.sector:
                        existing.sector = h.sector
                    updated_count += 1
                else:
                    # Update existing holding by averaging
                    total_shares = existing.shares + h.shares
                    total_cost = (existing.shares * float(existing.avg_cost)) + (h.shares * h.avg_cost)
                    existing.avg_cost = total_cost / total_shares
                    existing.shares = total_shares
                    updated_count += 1
            else:
                # Create new holding
                new_holding = Holding(
                    portfolio_id=portfolio.id,
                    symbol=symbol,
                    shares=h.shares,
                    avg_cost=h.avg_cost,
                    sector=h.sector or "Unknown"
                )
                db.add(new_holding)
                imported_count += 1
        
        db.commit()
        
        # Fetch updated holdings
        holdings = db.query(Holding).filter(
            Holding.portfolio_id == portfolio.id
        ).all()
        
        holdings_data = [{
            "id": h.id,
            "symbol": h.symbol,
            "shares": h.shares,
            "avg_cost": float(h.avg_cost),
            "sector": h.sector
        } for h in holdings]
        
        return ImportConfirmResponse(
            success=True,
            imported_count=imported_count,
            skipped_count=skipped_count,
            updated_count=updated_count,
            message=f"Successfully imported {imported_count} new holdings, updated {updated_count}, skipped {skipped_count}",
            holdings=holdings_data
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )


@router.get("/supported-brokers")
def get_supported_brokers():
    """Get list of supported broker apps for screenshot import"""
    return {
        "supported_brokers": [
            {
                "name": "IPOT (Indo Premier Online Trading)",
                "status": "fully_supported",
                "notes": "Best results with portfolio summary screen"
            },
            {
                "name": "Stockbit",
                "status": "fully_supported",
                "notes": "Use portfolio holdings view"
            },
            {
                "name": "Ajaib",
                "status": "fully_supported",
                "notes": "Capture the stock holdings screen"
            },
            {
                "name": "Bibit Saham",
                "status": "supported",
                "notes": "Ensure all holdings are visible"
            },
            {
                "name": "MOST (Mandiri Sekuritas)",
                "status": "supported",
                "notes": "Use portfolio summary view"
            },
            {
                "name": "Other Brokers",
                "status": "experimental",
                "notes": "May work if format is similar. Results may vary."
            }
        ],
        "tips": [
            "Ensure the screenshot is clear and not blurry",
            "Capture the complete portfolio view with all stocks visible",
            "Avoid screenshots with popup overlays",
            "PNG format typically gives best results",
            "Make sure share counts and prices are fully visible"
        ]
    }


@router.post("/validate")
async def validate_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Quick validation of uploaded image without full processing.
    Checks file type, size, and basic image validity.
    """
    # Validate file type
    if file.content_type not in ALLOWED_TYPES:
        return {
            "valid": False,
            "error": f"Invalid file type: {file.content_type}",
            "allowed_types": ALLOWED_TYPES
        }
    
    # Read and check size
    content = await file.read()
    
    if len(content) > MAX_FILE_SIZE:
        return {
            "valid": False,
            "error": f"File too large ({len(content) // 1024}KB). Maximum: {MAX_FILE_SIZE // (1024*1024)}MB"
        }
    
    if len(content) < 1000:
        return {
            "valid": False,
            "error": "File too small. This may not be a valid image."
        }
    
    return {
        "valid": True,
        "file_name": file.filename,
        "file_size": len(content),
        "file_type": file.content_type,
        "message": "Image is valid. Ready for processing."
    }
