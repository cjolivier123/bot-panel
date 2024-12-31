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
    
    @app.route("/checkout", methods=["GET", "POST"])
    def checkout():
        if request.method == "POST":
            try:
                plan_name = request.form.get("plan_name")
                if not plan_name:
                    logger.error("No plan_name provided in form data")
                    return "Invalid plan selected", 400
                
                amount = 2.99  # Default amount for Premium Plan
                
                # Set the correct amount based on the plan
                if plan_name == "Lifetime Plan":
                    amount = 19.99
                elif plan_name == "Source Code Plan":
                    amount = 22.99
                
                # For one-time payment plans, set final_amount equal to amount
                final_amount = amount
                
                return render_template("checkout.html",
                                      plan_name=plan_name,
                                      amount=amount,
                                      final_amount=final_amount)
                
            except Exception as e:
                logger.error(f"Error in checkout: {str(e)}")
                return "An error occurred while processing your request. Please try again.", 500
        else:
            return redirect(url_for("plans_route"))
    
    @app.route("/apply_promo", methods=["POST"])
    def apply_promo():
        try:
            plan_name = request.form.get("plan_name")
            amount = float(request.form.get("amount"))
            promo_code = request.form.get("promo_code")
            
            final_amount = amount
            if promo_code == "NEWYEAR2025":
                final_amount = amount * 0.5
            else:
                final_amount = amount * 0.9
            
            return render_template("checkout.html",
                                  plan_name=plan_name,
                                  amount=amount,
                                  final_amount=final_amount,
                                  discount_amount=amount - final_amount,
                                  promo_code=promo_code)
            
        except Exception as e:
            logger.error(f"Error in apply_promo: {str(e)}")
            return "An error occurred while applying the promo code. Please try again.", 500
    
    @app.route("/process_payment", methods=["POST"])
    def process_payment():
        try:
            plan_name = request.form.get("plan_name")
            amount = float(request.form.get("amount"))
            final_amount = float(request.form.get("final_amount", amount))
            full_name = request.form.get("full_name")
            email = request.form.get("email")
            promo_code = request.form.get("promo_code")
            
            purchase = Purchase(
                plan_name=plan_name,
                amount=amount,
                final_amount=final_amount,
                full_name=full_name,
                email=email,
                promo_code=promo_code,
                status="completed"
            )
            
            db.session.add(purchase)
            db.session.commit()
            
            return redirect(url_for("thanks_route"))
            
        except Exception as e:
            logger.error(f"Error in process_payment: {str(e)}")
            db.session.rollback()
            return "An error occurred while processing your payment. Please try again.", 500
    

    @app.route("/thanks")
    def thanks_route():
        return render_template("thanks.html")
