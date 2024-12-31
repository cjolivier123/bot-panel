import logging
import os
import uuid
from flask import render_template, redirect, url_for, request
from flask import current_app as app
from models import db, Purchase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_routes(app):
    @app.route("/")
    def home_route():
        return render_template("home.html")
    
    @app.route("/plans")
    def plans_route():
        return render_template("plans.html")
    
    @app.route("/checkout/<purchase_id>", methods=["GET"])
    def checkout_route(purchase_id):
        purchase = Purchase.query.get_or_404(purchase_id)
        return render_template("checkout.html",
                              purchase_id=purchase_id,
                              plan_name=purchase.plan_name,
                              amount=purchase.amount,
                              final_amount=purchase.final_amount or purchase.amount,
                              discount_amount=purchase.amount - purchase.final_amount if purchase.final_amount else None)
    
    @app.route("/create_checkout", methods=["POST"])
    def create_checkout():
        plan_name = request.form.get("plan_name")
        amount = 2.99  # Default amount for Premium Plan
        
        # Set the correct amount based on the plan
        if plan_name == "Lifetime Plan":
            amount = 19.99
        elif plan_name == "Source Code Plan":
            amount = 22.99
        
        # For one-time payment plans, set final_amount equal to amount
        final_amount = amount
        if plan_name in ["Lifetime Plan", "Source Code Plan"]:
            final_amount = amount
        
        purchase = Purchase(
            plan_name=plan_name,
            amount=amount,
            final_amount=amount,
            full_name="",
            email=""
        )
        db.session.add(purchase)
        db.session.commit()
        return redirect(url_for("checkout_route", purchase_id=purchase.id))
    
    @app.route("/apply_promo/<purchase_id>", methods=["POST"])
    def apply_promo(purchase_id):
        purchase = Purchase.query.get_or_404(purchase_id)
        promo_code = request.form.get("promo_code")
        
        # Implement promo code validation and discount calculation
        if promo_code == "NEWYEAR2025":
            purchase.promo_code = promo_code
            purchase.final_amount = purchase.amount * 0.5
        else:
            purchase.final_amount = purchase.amount * 0.9
        db.session.commit()
        return redirect(url_for("checkout_route", purchase_id=purchase_id))
    
    @app.route("/process_payment/<purchase_id>", methods=["POST"])
    def process_payment(purchase_id):
        purchase = Purchase.query.get_or_404(purchase_id)
        
        # TODO: Implement PayPal payment processing
        # For now, we'll just mark the purchase as completed
        purchase.status = "completed"
        db.session.commit()
        
        return redirect(url_for("thanks_route"))
    
    @app.route("/thanks")
    def thanks_route():
        return render_template("thanks.html")
