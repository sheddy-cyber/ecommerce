from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models.product import Product
from schemas.product import ProductCreate, ProductResponse
from utils.files import save_image
from utils.auth import get_current_user
from typing import List

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductResponse)
def create_product(
    name: str,
    price: float,
    stock: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
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


@router.get("/", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


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
    current_user=Depends(get_current_user)
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
    current_user=Depends(get_current_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}