from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, func
from app.core.database import get_session
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductRead, ProductListResponse

router = APIRouter()


@router.get("/", response_model=ProductListResponse, summary="List all products")
def list_products(
    session: Session = Depends(get_session),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search by name or description"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """Retrieve available products with category filtering, search, and pagination."""
    statement = select(Product).where(Product.is_active == True)
    
    if category:
        statement = statement.where(Product.category == category)
    if search:
        search_filter = f"%{search}%"
        statement = statement.where(
            (Product.name.ilike(search_filter)) | (Product.description.ilike(search_filter))
        )
    
    # Total count
    count_statement = select(func.count()).select_from(statement.subquery())
    total = session.exec(count_statement).one()

    # Paginated items
    statement = statement.offset(skip).limit(limit)
    items = session.exec(statement).all()

    return ProductListResponse(total=total, items=items)


@router.get("/{product_id}", response_model=ProductRead, summary="Get single product by ID")
def get_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found."
        )
    return product


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED, summary="Create new product")
def create_product(product_in: ProductCreate, session: Session = Depends(get_session)):
    # Check duplicate SKU or slug
    existing = session.exec(
        select(Product).where((Product.sku == product_in.sku) | (Product.slug == product_in.slug))
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A product with the same SKU or slug already exists."
        )

    product = Product.model_validate(product_in)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductRead, summary="Update product")
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    session: Session = Depends(get_session)
):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found."
        )

    update_data = product_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Deactivate product")
def delete_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found."
        )
    product.is_active = False
    session.add(product)
    session.commit()
    return None
