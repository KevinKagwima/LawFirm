from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session, make_response
from flask_redis import FlaskRedis
from flask_caching import Cache, CachedResponse
from flask_login import login_required, fresh_login_required
from Models.base_model import db, get_local_time

admin_bp = Blueprint("admin", __name__)
cache = Cache()
redis_client = FlaskRedis()