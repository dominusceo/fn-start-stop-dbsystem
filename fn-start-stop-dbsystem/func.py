import io
import json
import logging
import oci
from fdk import response

def handler(ctx, data: io.BytesIO = None):
    try:
        # Obtener el signer con autenticación de recurso principal
        signer = oci.auth.signers.get_resource_principals_signer()
        db_client = oci.database.DatabaseClient(config={}, signer=signer)

        # Leer parámetros del evento
        body = json.load(data)
        action = body.get("action", "").lower()
        compartment_id = body.get("compartment_id")
        db_system_id = body.get("db_system_id")  # opcional

        if action not in ["start", "stop"]:
            return json.dumps({"error": "Acción inválida. Usa 'start' o 'stop'."})
        
        if not compartment_id and not db_system_id:
            return json.dumps({"error": "Debes proporcionar al menos 'compartment_id' o 'db_system_id'."})

        # Función auxiliar para manejar un solo DB System
        def process_db_system(db):
            db_id = db.id
            display_name = db.display_name
            lifecycle_state = db.lifecycle_state

            if action == "stop" and lifecycle_state != "AVAILABLE":
                return {"db_system": display_name, "status": "Ya detenido o no disponible"}
            if action == "start" and lifecycle_state != "STOPPED":
                return {"db_system": display_name, "status": "Ya iniciado o no detenido"}

            try:
                if action == "stop":
                    db_client.stop_db_system(db_id)
                    return {"db_system": display_name, "status": "Detención iniciada"}
                else:
                    db_client.start_db_system(db_id)
                    return {"db_system": display_name, "status": "Inicio iniciado"}
            except oci.exceptions.ServiceError as e:
                return {"db_system": display_name, "status": f"Error: {e.message}"}

        results = []

        if db_system_id:
            db = db_client.get_db_system(db_system_id).data
            result = process_db_system(db)
            results.append(result)
        else:
            db_systems = db_client.list_db_systems(compartment_id).data
            if not db_systems:
                return json.dumps({"message": "No se encontraron DB Systems en el compartimento."})
            for db in db_systems:
                result = process_db_system(db)
                results.append(result)

        return json.dumps({"results": results})

    except Exception as e:
        return json.dumps({"error": str(e)})
