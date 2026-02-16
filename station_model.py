from models.db import get_cursor # This import is correct

class StationModel:

    @staticmethod
    def get_all_stations():
        with get_cursor(dictionary=True) as (cursor, _):
            cursor.execute("SELECT station_id, station_name FROM stations ORDER BY station_name ASC")
            return cursor.fetchall()

    @staticmethod
    def create_station(station_name: str):
        with get_cursor() as (cursor, conn):
            cursor.execute("INSERT INTO stations (station_name) VALUES (%s)", (station_name,))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def get_station_summary():
        """
        Calculates the assigned, used, and residual funds for each station.
        This query correctly joins stations with fund requests and expenditures.
        """
        query = """
            SELECT
                s.station_name,
                COALESCE(assigned.total_assigned, 0) AS assigned_amount,
                COALESCE(used.total_used, 0) AS used_amount,
                (COALESCE(assigned.total_assigned, 0) - COALESCE(used.total_used, 0)) AS residual_amount
            FROM
                stations s
            LEFT JOIN (
                SELECT
                    station_id,
                    SUM(token_amount) AS total_assigned
                FROM
                    fund_requests
                WHERE
                    rhq_status IN ('TOKEN_PROVIDED', 'APPROVED')
                GROUP BY
                    station_id
            ) AS assigned ON s.station_id = assigned.station_id
            LEFT JOIN (
                SELECT
                    fr.station_id,
                    SUM(eh.amount_spent) AS total_used
                FROM
                    expenditure_history eh
                JOIN
                    fund_requests fr ON eh.request_id = fr.request_id
                GROUP BY
                    fr.station_id
            ) AS used ON s.station_id = used.station_id
            ORDER BY
                s.station_name;
        """
        with get_cursor(dictionary=True) as (cursor, _):
            cursor.execute(query)
            summary = cursor.fetchall()
            return summary
