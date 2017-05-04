from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
app = Flask(__name__)

from restaurant_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///restaurants.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

@app.route('/')
@app.route('/restaurants')
def restaurantMenu():
    restaurant = session.query(Restaurant)
    return render_template('restaurantMenu.html', restaurant = restaurant)

@app.route('/restaurants/new', methods = ['GET', 'POST'])
def newRestaurant():
    if request.method == "POST":
        newRestaurant = Restaurant(name = request.form['name'])
        session.add(newRestaurant)
        session.commit()
        flash('New Restaurant created!')
        return redirect(url_for('restaurantMenu'))
    else:
        return render_template('newRestaurant.html')


@app.route('/restaurants/<int:restaurant_id>/edit', methods = ['GET', 'POST'])
def editRestaurant(restaurant_id):
    resQuery = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == "POST":
        if request.form['name']:
            resQuery.name = request.form['name']
            session.add(resQuery)
            session.commit()
            flash('Restaurant updated!')
            return redirect(url_for('restaurantMenu'))
    else:
        return render_template('editRestaurant.html', restaurant = resQuery)

@app.route('/restaurants/<int:restaurant_id>/delete', methods = ['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    resQuery = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == "POST":
        session.delete(resQuery)
        session.commit()
        flash('Restaurant deleted!')
        return redirect(url_for('restaurantMenu'))
    else:
        return render_template('deleteRestaurant.html', restaurant = resQuery)


@app.route('/restaurants/<int:restaurant_id>/menu')
@app.route('/restaurants/<int:restaurant_id>/')
def restaurantItemMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
    return render_template('menu.html', restaurant = restaurant, items = items)

@app.route('/restaurants/<int:restaurant_id>/menu/new', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if request.method == "POST":
        newItem = MenuItem(name = request.form['name'], restaurant_id = restaurant_id)
        session.add(newItem)
        session.commit()
        flash("New menu item created!")
        return redirect(url_for('restaurantItemMenu', restaurant_id = restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id = restaurant_id)

# Task 2: Create route for editMenuItem function here

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/edit', methods = ['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    itemQuery = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == "POST":
        if request.form['name']:
            itemQuery.name = request.form['name']
            session.add(itemQuery)
            session.commit()
            flash("Menu item has been updated!")
            return redirect(url_for('restaurantItemMenu', restaurant_id = restaurant_id))
    else:
        return render_template('updatemenuitem.html', restaurant_id = restaurant_id, menu_id = menu_id, item = itemQuery)

# Task 3: Create a route for deleteMenuItem function here

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/delete', methods = ['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    itemQuery = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(itemQuery)
        session.commit()
        flash("Menu item has been deleted!")
        return redirect(url_for('restaurantItemMenu', restaurant_id = restaurant_id))
    else:
        return render_template('deletemenuitem.html', restaurant_id = restaurant_id, menu_id = menu_id, item = itemQuery)


#Making an API Endpoint (GET Request)
@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
    return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id, id = menu_id)
    return jsonify(MenuItems=[i.serialize for i in items])


if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host = '0.0.0.0', port = 8080)
