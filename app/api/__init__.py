from flask import Blueprint

bp = Blueprint('api', __name__)

# 避免循环依赖 
from app.api import users, errors, tokens