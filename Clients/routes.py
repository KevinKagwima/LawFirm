from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session, make_response

client_bp = Blueprint("client", __name__)
