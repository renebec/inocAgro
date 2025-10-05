"""
Pre-registration validation module for mat1 project
Validates students against alumnos_preregistrados table
"""

import pymysql
from datetime import datetime
import os

def get_db_connection():
    """Get database connection using environment variables"""
    try:
        connection = pymysql.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            user=os.environ.get('DB_USER', 'root'),
            password=os.environ.get('DB_PASSWORD', ''),
            database=os.environ.get('DB_NAME', 'statSat'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None

def validate_preregistration(numero_control):
    """
    Validate if user (student OR teacher) is pre-registered and not already used
    Only checks numero_control - works for both students and teachers
    Returns: (is_valid: bool, message: str, data: dict or None)
    """
    try:
        connection = get_db_connection()
        if not connection:
            return False, "Error de conexión a la base de datos", None

        with connection.cursor() as cursor:
            # Check if student is pre-registered and not used
            query = """
                SELECT * FROM prereg 
                WHERE controlnum = %s AND usado = 0
            """
            cursor.execute(query, (controlnum,))
            result = cursor.fetchone()

        connection.close()

        if result:
            return True, "Usuario autorizado para registro", result
        else:
            # Check if already used
            connection = get_db_connection()
            with connection.cursor() as cursor:
                check_used_query = """
                    SELECT usado, fecha_uso FROM prereg 
                    WHERE controlnum = %s
                """
                cursor.execute(check_used_query, (controlnum,))
                used_result = cursor.fetchone()
            connection.close()

            if used_result and used_result['usado']:
                return False, f"Este número de control ya fue usado para registro el {used_result['fecha_uso']}", None
            else:
                return False, "Número de control no encontrado en la lista de pre-registrados. Contacte a la administración.", None

    except Exception as e:
        print(f"❌ Error validating pre-registration: {e}")
        return False, f"Error del sistema: {e}", None

def mark_preregistration_as_used(controlnum):
    """
    Mark pre-registration entry as used
    Returns: bool (success/failure)
    """
    try:
        connection = get_db_connection()
        if not connection:
            return False

        with connection.cursor() as cursor:
            query = """
                UPDATE prereg 
                SET usado = 1, fecha_uso = %s 
                WHERE controlnum = %s AND usado = 0
            """
            rows_affected = cursor.execute(query, (datetime.now(), numero_control))
            connection.commit()

        connection.close()
        return rows_affected > 0

    except Exception as e:
        print(f"❌ Error marking pre-registration as used: {e}")
        return False

# REMOVED: Name validation - only numero_control is checked now

def get_preregistration_stats():
    """
    Get statistics about pre-registrations for admin purposes
    Returns: dict with stats
    """
    try:
        connection = get_db_connection()
        if not connection:
            return {"error": "Database connection failed"}

        with connection.cursor() as cursor:
            stats_query = """
                SELECT 
                    COUNT(*) as total_preregistered,
                    SUM(CASE WHEN usado = 1 THEN 1 ELSE 0 END) as used_registrations,
                    SUM(CASE WHEN usado = 0 THEN 1 ELSE 0 END) as available_registrations
                FROM alumnos_preregistrados
            """
            cursor.execute(stats_query)
            stats = cursor.fetchone()

        connection.close()
        return stats

    except Exception as e:
        print(f"❌ Error getting pre-registration stats: {e}")
        return {"error": str(e)}