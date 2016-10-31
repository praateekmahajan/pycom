# pycom
Simple Flask Based ECommerce Cart System based on Redis, Flask, Postgres

### Capabilities
#
### Login with facebook
#### Add Coupon Code 
 ``` python
    import app
    c = models.Coupon(id="flat20",name="Flat 20% off on plastic goods",multiplier=0.8,upto = 0, flatoff = 0)
    p = models.Product.get(id=1)
    p.coupons.append(c)
    db.session.commit()
 ```
#### Add/Remove/Change number of Products to Cart
 

#### Has the following APIs
  - /api/crudproducts with methods POST, PUT and DELETE
    - Add products with attributes name, price and quantity
    - Update product with attribute id
    - Can update the following fields with optional attributes name, price and quantity
  - /api/updatecart with methods POST
    - Update cart with attributes sessionid (sid), productid (pid)
    - Optional attribute extrattribute (v)
      - Default value of '' means, that it will increment the current cart value of the product by +1
      - Set the value of v as delete, if you want to remove the product from cart
      - Set value to a natural number, to add that number of products in the cart
    
  - /api/viewcart/ with methods GET
    - View cart of a given session by using the attribute
    
#### It handles 
 - The rare possibility that, a product is in cart and it got deleted from the backend
 - The case where a product was in stock when it was added, but later was removed from stock
 - The case where a n values of product was in stock, but later value of n had reduced, it auto updates the GUI cart to that lower value of n, in API it returns out of stock


#### What can be improved
 - Add requirements.txt for quick installation
 - Use coupon values in API cart (avoided because coupons weren't required)
 - When a person who has not logged in, adds products to the cart and then logins via facebook, his cart is lost as sessionid changes (avoided because authentication wasn't required)
 - Add API for setting up the coupon system (avoided for the reason mentioned above)
 
#### How to complete an order
 - Get cart details by /api/viewcart/XXXX (XXXX is sessionid)
 - Iterate over the products (say p's) in the cart and get value of p.instock (which tells how many products were in stock at the time of order)
 - Update value of each product using PUT /api/updatecart/ with the following json data {sid:XXXX,pid:p,v:(p.instock - p.incart))

# Installation

```
virtualenv venv
source venv/bin/activate

 //INSTALL THE REQUIRED LIBRARIES (flask_sqlalchemy, flask_redis...etc)
 //SETUP config
python db create_db.py
python db_migrate
```
