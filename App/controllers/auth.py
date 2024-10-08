from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity, verify_jwt_in_request

from App.models import Staff

def login(email, password):
  staff = Staff.query.filter_by(email=email).first()
  if staff and staff.check_password(password):
    return create_access_token(identity=email)
  return None


def setup_jwt(app):
  jwt = JWTManager(app)

  # configure's flask jwt to resolve get_current_identity() to the corresponding staff's ID
  @jwt.user_identity_loader
  def user_identity_lookup(identity):
    staff = Staff.query.filter_by(email=identity).one_or_none()
    if staff:
        return staff.id
    return None

  @jwt.user_lookup_loader
  def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return Staff.query.get(identity)

  return jwt


# Context processor to make 'is_authenticated' available to all templates
def add_auth_context(app):
  @app.context_processor
  def inject_user():
      try:
          verify_jwt_in_request()
          email = get_jwt_identity()
          current_user = Staff.query.get(email)
          is_authenticated = True
      except Exception as e:
          print(e)
          is_authenticated = False
          current_user = None
      return dict(is_authenticated=is_authenticated, current_user=current_user)