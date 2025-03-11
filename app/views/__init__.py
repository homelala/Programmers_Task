import traceback
from funcy import first
from flask import jsonify
from flask_apispec import marshal_with

from app.error import ApiError
from app.serializers.error import ApiErrorSchema
from app.views.reservation import ReservationView

@marshal_with(ApiErrorSchema())
def handle_api_error(e: ApiError):
    traceback.print_exc()
    return e, e.status_code

@marshal_with(ApiErrorSchema())
def handle_not_found(e):
    return ApiError(message=e.message, status_code=404), 404

def handle_unprocessable_entity(e):
    def make_field_to_str(messages):
        if isinstance(messages, list):
            return messages
        return {str(field): make_field_to_str(field_messages) for field, field_messages in messages.items()}

    def find_message(key, errors):
        if isinstance(errors, list):
            if key is None or key == "_schema":
                return errors[0]
            else:
                return ("입력 정보가 유효하지 않습니다.")

        first_key, first_key_errors = first(errors.items())
        return find_message(first_key, first_key_errors)

    errors = make_field_to_str(e.data["messages"])
    message = find_message(None, errors)

    traceback.print_exc()

    return jsonify({"code": 422, "message": message, "errors": errors}), e.code


def register_error_handlers(app):
    app.register_error_handler(ApiError, handle_api_error)
    app.register_error_handler(422, handle_unprocessable_entity)
    app.register_error_handler(ApiError, handle_not_found)

def register_api(app):
    ReservationView.register(app, route_base="/reservation", trailing_slash=False)

    register_error_handlers(app)
