from flask import render_template,flash,redirect,url_for,session,request,g,abort,jsonify
from app import app,db,redis_store
from OAuth import OAuthSignIn
from flask_login import login_user, logout_user,current_user
from models import User,Product

from os import urandom
import random,json


# Saving uid in session cookies
def after_this_request(f):
    if not hasattr(g, 'after_request_callbacks'):
        g.after_request_callbacks = []
    g.after_request_callbacks.append(f)
    return f

@app.after_request
def call_after_request_callbacks(response):
    for callback in getattr(g, 'after_request_callbacks', ()):
        callback(response)
    return response

@app.before_request
def save_session_cookie():
    # cookie exists
    if not request.cookies.get('sessionuid') is None:
        #user has been on the site for a while
        if current_user.is_anonymous and len(request.cookies.get('sessionuid').split('.'))==2:
                #user logged out from his facebook id therefore delete his session, and start new
                uid = base64.standard_b64encode(urandom(10))
        elif current_user.is_anonymous and len(request.cookies.get('sessionuid').split('.'))!=2:
                uid = request.cookies.get('sessionuid')
        elif not current_user.is_anonymous:
                uid = 'fb.'+current_user.id

    else:
        # if no cookie exists then set random cookie
        uid = random.randint(10000000, 99999999)

    @after_this_request
    def remember_sessionuid(response):
        response.set_cookie('sessionuid', str(uid))

    g.uid = uid

# App vies start
@app.route('/')
@app.route('/index')
def index():
    user = current_user  # fake user
    products = Product.query.all()

    for product in products:
        product = checkMinimumPrice(product)

    return render_template("index.html",
                           title='Home',
                           user=user,
                           products=products)

# App vies start
@app.route('/product/<pid>', methods=['GET'])
def productpage(pid):
    uid = request.cookies.get('sessionuid')
    if uid is not None:
        cart = redis_store.hgetall('cart:' + uid)
        print '---cart---'
        product = Product.query.filter_by(id=pid).first_or_404()
        if pid in cart:
            print 'YEYEYEYEEY'
            print cart[pid]
            product.incart = cart[pid]
        else:
            print "NOENEONEON"
            product.incart = 0

        product = checkMinimumPrice(product)
        return render_template("product.html",
               title=product.name,
               product=product)

@app.route('/cart')
def showcart():
    uid = request.cookies.get('sessionuid')
    cart = {}
    if uid is not None:
        cart = redis_store.hgetall('cart:' + uid)
        newcart ={}
        total = 0
        #         print type(cart.items())

        for x in cart:
            product = Product.query.filter_by(id=x).first()
            print "TOTAL"
            print total
            # if product is not None:
            # ensure that admin has not deleted the product while it was in someones cart
            a = {}
            oos={}
            deleted = {}
            product = checkMinimumPrice(product)
            print product.name
            print '--------SQ---'
            print product.quantity
            print '--------PQ---'
            print int(cart[x])

            if product.quantity > 0:
                #see if product is in stock on the backend
                a['stockquantity'] = product.quantity
                a['quantity'] = int(cart[x])
                a['importantmessage'] =''
                if a['stockquantity'] < a['quantity']:
                    #insufficient stock, auto update stock on redis and cart page
                    a['quantity'] = a['stockquantity']
                    a['importantmessage'] = "Quantity changed from " + str(cart[x]) + "->" + str(a['stockquantity'])
                    redis_store.hset('cart:' + uid, x,a['stockquantity'])
                    print a['importantmessage']
                a['name'] = product.name
                a['id'] = product.id
                a['maxprice'] = product.price
                a['status'] = 'available'
                #Dealing with coupon
                if product.minpricecoupon is not 0:
                    a['minprice'] = product.minpricecoupon.afterprice
                    if product.minpricecoupon.upto > 0:
                        a['couponused'] = product.minpricecoupon.name + " upto Rs." + product.minpricecoupon.upto
                    else:
                        a['couponused'] = product.minpricecoupon.name
                else:
                    a['minprice'] = product.price
                    a['couponused'] = ''

                a['total'] = a['quantity'] * a['minprice']
                total += a['total']
                newcart[x] = a
            else:
                # if product is not in stock
                oos['quantity'] = int(cart[x])
                oos['name'] = product.name
                oos['id'] = product.id
                oos['maxprice'] = product.price
                oos['couponused'] = ''
                oos['minprice'] = product.price
                if product.quantity == -1:
                    #Deleted product
                    oos['status'] = 'deleted'
                    oos['quantity'] = 0
                else:
                    #Out of Stock
                    oos['status'] = 'oos'

                newcart[x] = oos


            # else:
                #if admin has deleted the product, auto-delete it from cart
                # rare case, that it has been removed from database
                # redis_store.hset('cart:' + uid,x,-1)

    return render_template("cart.html",
                           title="Your Cart",
                           cart=newcart,
                           total=total)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html',title='Sign In')


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, name, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(id=social_id).first()
    if not user:
        user = User(id=social_id, email=email, name=name)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))


def checkMinimumPrice(product):
    product.minpricecoupon = {}
    if len(product.coupons) >= 1:
        for coupon in product.coupons:
            pricemultiplied = product.price * coupon.multiplier
            coupon.afterprice = (product.price-coupon.upto) if (pricemultiplied > coupon.upto and coupon.upto > 0) else pricemultiplied
            coupon.afterprice = coupon.afterprice - (0 if coupon.flatoff is None else coupon.flatoff)
        product.minpricecoupon = min(product.coupons, key=lambda c: c.afterprice)

    else:
        product.minpricecoupon = 0
    return product
