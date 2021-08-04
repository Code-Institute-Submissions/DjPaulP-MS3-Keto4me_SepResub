import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

# Home page
@app.route("/")
@app.route("/get_recipes")
def get_recipes():
    recipes = list(mongo.db.recipes.find())
    return render_template("recipes.html", recipes=recipes)

# Allow users to register on the website
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if the username is already registered in the database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")  
            return redirect(url_for("register"))  

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        #put the new user into a 'session' cookie on website
        session["user"] = request.form.get("username").lower()
        flash("Welcome, Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


# Allow users to login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check to see of username is in the database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure the password matches the one in the database
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome to Keto 4 Me {}".format(
                        request.form.get("username")))
                    return redirect(url_for(
                        "profile", username=session["user"]))    
            else:
                # when the password doesn't match
                flash("Your password and/or Username is incorrect")    
                return redirect(url_for("login"))

        else:
            # If the username does not exist
            flash("Your password and/or Username is incorrect")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # getting the session's username from the database
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # Allowing a user to log out of the website
    flash("You have been Logged Out")
    session.pop("user")
    return redirect(url_for("login")) 


@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    # Allow users to add recipes to the website
    if request.method == "POST":
        recipe = {
            "category_name": request.form.get("category_name"),
            "recipe_name": request.form.get("recipe_name"),
            "image_url": request.form.get("image_url"),
            "serves": request.form.get("serves"),
            "prep_time": request.form.get("prep_time"),
            "ingredients": request.form.get("ingredients"),
            "method": request.form.get("method"),
            "created_by": session["user"]
        }
        mongo.db.recipes.insert_one(recipe)
        flash("Your recipe has been Sumitted, Thank You!")
        return redirect(url_for('get_recipes'))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_recipe.html", categories=categories)


@app.route("/edit_recipe/<recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    # Allow users to edit their recipes
    if request.method == "POST":
        submit = {
            "category_name": request.form.get("category_name"),
            "recipe_name": request.form.get("recipe_name"),
            "image_url": request.form.get("image_url"),
            "serves": request.form.get("serves"),
            "prep_time": request.form.get("prep_time"),
            "ingredients": request.form.get("ingredients"),
            "method": request.form.get("method"),
            "created_by": session["user"]
        }
        mongo.db.recipes.update({"_id": ObjectId(recipe_id)}, submit)
        flash("Your recipe has been Edited and Updated, Thank You!")
        return redirect(url_for('get_recipes'))
    
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("edit_recipe.html", recipe=recipe, categories=categories)


@app.route("/delete_recipe<recipe_id>")
def delete_recipe(recipe_id):
    mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
    flash ("Your recipe has successfully been deleted")
    return redirect(url_for('get_recipes'))


@app.route("/get_categories")
def get_categories():
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("categories.html", categories=categories)  


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)   
