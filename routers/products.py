from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from database import get_db
from models.product import Product
from schemas.product import ProductCreate, ProductResponse
from utils.files import save_image
from utils.auth import get_current_user, get_admin_user
from typing import List

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductResponse)
def create_product(
    name: str,
    price: float,
    stock: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_admin_user),
    description: str = None,
    image: UploadFile = File(None)
):
    image_url = None
    if image:
        image_url = save_image(image)

    new_product = Product(
        name=name,
        description=description,
        price=price,
        stock=stock,
        image_url=image_url
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@router.get("/", response_model=dict)
def get_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    total = db.query(Product).count()
    products = db.query(Product).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "results": [ProductResponse.model_validate(p) for p in products]
    }


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    name: str = None,
    description: str = None,
    price: float = None,
    stock: int = None,
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_admin_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if name: product.name = name
    if description: product.description = description
    if price: product.price = price
    if stock: product.stock = stock
    if image: product.image_url = save_image(image)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_admin_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}