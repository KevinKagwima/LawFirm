from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session, make_response

case_bp = Blueprint("case", __name__)
