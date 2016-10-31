from models import User,Product
from flask import render_template,flash,redirect,url_for,session,request,g,abort,jsonify
from app import app,db,redis_store
import json

@app.route('/api/crudproducts', methods=['POST','DELETE','PUT'])
def crud_product():
    if request.method == 'POST':
        product = Product.query.filter_by(name=request.json['name']).all()
        if not 'name' or not 'price' or not 'quantity' in request.json:
            abort(400)
        if len(product) >= 1:
            product = {
                'id': product[0].id,
                'name': product[0].name,
                'price': product[0].price,
                'quantity': product[0].quantity,
                'url':  '/product/'+ str(product[0].id)
            }
            return jsonify({'status': 'warning','message':'Product ID alreadys exists','product':product}), 201
        else:
            product = Product(name=request.json['name'], price=request.json['price'],
                              quantity=request.json['quantity'])
            db.session.add(product)
            db.session.commit()
            product = Product.query.filter_by(name=request.json['name'])
            product = product.first()
            product = {
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'quantity': product.quantity,
                'url': '/product/' + str(product.id)
            }
            return jsonify({'status': 'success', 'product': product}), 201
    elif request.method == 'DELETE':
        print request.method
        if not 'id' in request.json:
            abort(400)
        print 'a'
        print request.json['id']
        p = Product.query.filter_by(id=request.json['id']).all()
        print p
        if p is not None:
            #entry exsists
            p = p[0]
            print 'here'
            p.quantity = -1
            db.session.commit()
            return jsonify({'status': 'success'}), 201

        else:
            return jsonify({'status': 'error', 'messag': 'Product ID doesn\'t exist'}), 201
    elif request.method == 'PUT':
        if not 'id' in request.json:
            abort(400)
        product = Product.query.filter_by(id=request.json['id']).all()
        if len(product)<1:
            return jsonify({'status': 'error','messag':'Product ID doesn\'t exist'}), 201
        else:
            product = product[0]
            if 'name' in request.json:
                product.name = request.json['name']
            if 'price' in request.json:
                product.price = request.json['price']
            if 'quantity' in request.json:
                product.quantity = request.json['quantity']
            db.session.commit()
            product = {
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'quantity': product.quantity,
                'url': '/product/' + str(product.id)
            }
            return jsonify({'status': 'success', 'product': product}), 201
    else:
        return jsonify({'status': 'error', 'message':'Bad Request'})

@app.route('/api/updatecart', methods=['POST'])
def updatecart():
    if not 'sid' or not 'pid' in request.json:
        abort(400)

    uid = request.json['sid']
    pid = request.json['pid']

    extrattribute = request.json['v'] if 'v' in request.json else '-1'
    if request.json['v'] == '':
        extrattribute = -1
    else:
        extrattribute = request.json['v']
    product = Product.query.filter_by(id=pid).first_or_404()

    if request.method == 'POST':
        print product.quantity

        # If not in cart
        if redis_store.hget('cart:' + uid, pid) is None:
            if(extrattribute=='delete'):
                return jsonify({'status': 'error',
                                'message': 'It is not present in cart',
                                'cart': redis_store.hgetall('cart:' + uid)}), 201

            # Increment +1, when product is not in cart, therefore 0-->1
            if(extrattribute==-1):
                extrattribute = 1

            if int(product.quantity) < int(extrattribute):
                redis_store.hset('cart:' + uid, pid, extrattribute)
                return jsonify({'status': 'error',
                                'message': 'Out of Stock. Only ' + str(product.quantity) + ' left.',
                                'cart': redis_store.hgetall('cart:' + uid)}), 201
            else:
                redis_store.hset('cart:' + uid, pid, extrattribute)
                return jsonify({'status': 'success',
                                'message': 'Successfuly added to <a href="/cart">cart</a>',
                                'cart': redis_store.hgetall('cart:' + uid)}), 201
        else:
            currentquantity = redis_store.hget('cart:' + uid, pid)
            if(extrattribute=='delete'):
                redis_store.hdel('cart:' + uid, pid)
                return jsonify({'status': 'success',
                                'message': 'Removed product from cart',
                                'cart': redis_store.hgetall('cart:' + uid)}), 201

            if(extrattribute==-1):
                #Product is in cart, and we have to do a +1 on number of products
                print 'asd'
                if product.quantity > int(currentquantity):
                    redis_store.hincrby('cart:' + uid, pid, 1)
                    return jsonify({'status': 'success',
                                    'message': 'Successfuly added to <a href="/cart">cart</a>',
                                    'cart': redis_store.hgetall('cart:' + uid)}), 201

                else:
                    redis_store.hset('cart:' + uid, pid, product.quantity)
                    return jsonify({'status': 'warning',
                                    'message': 'Insufficient Stock. Only ' + str(product.quantity) + ' left. You already have '  + str(currentquantity) +" in your current cart",
                                    'cart': redis_store.hgetall('cart:' + uid)}), 201
            else:
                #Product is in cart and we have to set it's value to the value in extraattribute
                if product.quantity > int(extrattribute):
                    redis_store.hset('cart:' + uid, pid, extrattribute)
                    return jsonify({'status': 'success',
                                    'message': 'Successfuly added to <a href="/cart">cart</a>',
                                    'cart': redis_store.hgetall('cart:' + uid)}), 201

                else:
                    redis_store.hset('cart:' + uid, pid, product.quantity)
                    return jsonify({'status': 'warning',
                                    'cart': redis_store.hgetall('cart:' + uid)}), 201

@app.route('/api/viewcart/<sid>', methods=['GET'])
def viewcart(sid):
    cart = redis_store.hgetall('cart:' + sid)
    newcart = {}
    if len(cart) > 0:
        print "APIAPI"

        productids = list(cart.keys())
        p = Product.query.filter(Product.id.in_(productids)).all()
        total = 0
        for x in p:
            productdetails = {}
            a = x.id
            print 'aaaaaaaaaa'
            print a
            productdetails['id'] = x.id
            productdetails['name'] = x.name
            productdetails['price'] = x.price
            productdetails['instock'] = x.quantity
            productdetails['incart'] = int(cart[str(a)])
            if productdetails['instock'] > productdetails['incart']:
                productdetails['availability'] = 'available'
            elif productdetails['instock'] < productdetails['incart']:
                productdetails['availability'] = 'outofstock'
            productdetails['total'] = x.price * x.quantity
            total += productdetails['total']
            newcart[str(a)] = productdetails

        return jsonify({'status': 'success',
                        'message' : 'Cart successfuly fetched',
                        'sessionid': sid,
                        'cart':newcart,
                        'total':total}), 201
    else:
        return jsonify({'status': 'error',
                        'message' : 'Either cart empty or invalid session id',
                        'sessionid': sid}), 201
