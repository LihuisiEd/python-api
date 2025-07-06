from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Ruta no encontrada"}), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Solicitud incorrecta"}), 400

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"error": "Error interno del servidor"}), 500
