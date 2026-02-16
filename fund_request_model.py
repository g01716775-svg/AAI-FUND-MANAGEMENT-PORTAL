# models/fund_request_model.py

from models.db import get_cursor
import decimal

class FundRequestModel:

    @staticmethod
    def get_all_requests():
        with get_cursor(dictionary=True) as (cursor, _):
            cursor.execute("""
                SELECT fr.*, s.station_name, fr.station_status, fr.l1_value, u.department,
                       (SELECT SUM(eh.amount_spent) FROM expenditure_history eh WHERE eh.request_id = fr.request_id) as expenditure,
                       (SELECT eh.note FROM expenditure_history eh WHERE eh.request_id = fr.request_id ORDER BY eh.created_at DESC LIMIT 1) as station_update_note
                FROM fund_requests fr
                JOIN stations s ON fr.station_id = s.station_id
                LEFT JOIN users u ON fr.user_id = u.user_id
            """)
            return cursor.fetchall()

    @staticmethod
    def add_expenditure_entry(request_id, new_expenditure, note=""):
        # Force a note to be provided. This prevents the incorrect top-level success flash message.
        if not note or not note.strip():
            raise ValueError("An expenditure note is required to proceed.")

        with get_cursor(dictionary=True) as (cursor, conn):
            # Get the approved amount and current total expenditure
            cursor.execute("""
                SELECT 
                    fr.amount_granted,
                    (SELECT SUM(eh.amount_spent) FROM expenditure_history eh WHERE eh.request_id = fr.request_id) as current_expenditure
                FROM fund_requests fr
                WHERE fr.request_id = %s
            """, (request_id,))
            request = cursor.fetchone()

            if not request:
                raise ValueError(f"Request with ID {request_id} not found.")

            amount_granted = decimal.Decimal(request.get('amount_granted') or 0.0)
            current_expenditure = decimal.Decimal(request.get('current_expenditure') or 0.0)
            new_expenditure_dec = decimal.Decimal(new_expenditure)

            # Check if the expenditure exceeds the approved amount
            if (current_expenditure + new_expenditure_dec) > amount_granted:
                raise ValueError(f"Spending exceeds limit! Max allowed: {amount_granted}")

            # If validation passes, insert a new history record
            cursor.execute("""
                INSERT INTO expenditure_history (request_id, amount_spent, note)
                VALUES (%s, %s, %s)
            """, (request_id, new_expenditure, note))
            conn.commit()

    @staticmethod
    def get_fund_requests_for_rhq(user):
        with get_cursor(dictionary=True) as (cursor, _):
            cursor.execute("""
                SELECT fr.*, u.station_name, u.department, fr.station_status, fr.l1_value, (SELECT SUM(eh.amount_spent) FROM expenditure_history eh WHERE eh.request_id = fr.request_id) as expenditure
                FROM fund_requests fr
                JOIN users u ON fr.user_id = u.user_id
                WHERE u.role = 'STATION' AND fr.rhq_status != 'ARCHIVED'
                ORDER BY fr.created_at DESC
            """)
            return cursor.fetchall()

    @staticmethod
    def get_expenditure_history(request_id):
        with get_cursor(dictionary=True) as (cursor, _):
            cursor.execute("SELECT * FROM expenditure_history WHERE request_id = %s ORDER BY created_at ASC", (request_id,))
            return cursor.fetchall()


    @staticmethod
    def update_fund_request_status(request_id, status, token, approved, comment):
        with get_cursor() as (cursor, conn):
            # update the request record
            cursor.execute("""
            UPDATE fund_requests
            SET rhq_status = %s, token_amount = %s, amount_granted = %s, rhq_comment = %s
            WHERE request_id = %s
            """, (status, token, approved, comment, request_id))
            
            # ---- Add to pool history for RHQ Dashboard ----
            if status in ("APPROVED", "TOKEN_PROVIDED"):
                deduct = approved if status == "APPROVED" else token
                cursor.execute("""
                INSERT INTO fund_pool_history (action, amount, timestamp)
                VALUES (%s, %s, NOW())
                """, (f"Deducted for Request {request_id}", deduct))

                # Notify the station dashboard to refresh when a request is approved
                if status == "APPROVED":
                    cursor.execute("""
                    UPDATE stations
                    SET dashboard_refresh = TRUE
                    WHERE station_id = (SELECT station_id FROM fund_requests WHERE request_id = %s)
                    """, (request_id,))

                conn.commit()

    @staticmethod
    def get_total_approved_funds():
        """
        Calculates the sum of all granted amounts for requests that are
        currently active (i.e., not pending, rejected, or archived).
        This is the definitive "approved" amount against the current fund pool.
        """
        with get_cursor(dictionary=True) as (cursor, _):
            # This query sums only the amounts that are actively approved.
            # It handles both direct approvals and token-based approvals separately.
            cursor.execute("""
                SELECT SUM(approved_value) as total_approved FROM (
                    SELECT COALESCE(amount_granted, 0) as approved_value FROM fund_requests WHERE rhq_status = 'APPROVED'
                    UNION ALL
                    SELECT COALESCE(token_amount, 0) as approved_value FROM fund_requests WHERE rhq_status = 'TOKEN_PROVIDED'
                ) as approved_amounts;
            """)
            result = cursor.fetchone()
            return result['total_approved'] if result and result['total_approved'] else 0

    @staticmethod
    def get_pool():
        with get_cursor(dictionary=True) as (cursor, _):
            cursor.execute("SELECT total_pool FROM fund_pool WHERE id = 1")
            pool = cursor.fetchone()
            return pool["total_pool"] if pool else 0.0

    @staticmethod
    def update_pool(new_amount):
        with get_cursor() as (cursor, conn):
            cursor.execute("UPDATE fund_pool SET total_pool=%s, updated_at=NOW() WHERE id = 1", (new_amount,))
            if cursor.rowcount == 0: # If no row with id=1 exists, insert it
                cursor.execute("INSERT INTO fund_pool (id, total_pool, updated_at) VALUES (1, %s, NOW())", (new_amount,))
            conn.commit()

    @staticmethod
    def add_pool_history(action, amount):
        with get_cursor() as (cursor, conn):
            cursor.execute(
                "INSERT INTO fund_pool_history (action, amount, timestamp) VALUES (%s, %s, NOW())",
                (action, amount)
            )
            conn.commit()

    @staticmethod
    def reset_fund_pool(new_amount):
        """
        Sets a new total pool amount and archives all existing requests
        to reset the expenditure tracking for the new pool.
        """
        with get_cursor() as (cursor, conn):
            # 1. Archive all current requests so they don't count against the new pool
            cursor.execute("""
                UPDATE fund_requests SET rhq_status = 'DENIED' 
                WHERE rhq_status IS NULL OR rhq_status NOT IN ('PENDING', 'REJECTED', 'DENIED')
            """)
            conn.commit() # Commit the archiving

            # 2. Set the new pool amount
            # This method handles its own connection and commit.
            FundRequestModel.update_pool(new_amount)

    @staticmethod
    def get_pool_history():
        with get_cursor(dictionary=True) as (cursor, _):
            cursor.execute("SELECT action, amount, timestamp FROM fund_pool_history ORDER BY id DESC")
            return cursor.fetchall()

    @staticmethod
    def get_station_summary():
        """
        Retrieves a summary of funds assigned, used, and residual for each station.
        Assigned amount includes funds from 'APPROVED' and 'TOKEN_PROVIDED' requests.
        Used amount is the sum of all expenditures for that station's requests.
        """
        with get_cursor(dictionary=True) as (cursor, _):
            cursor.execute("""
                SELECT
                    u.station_name,
                    COALESCE(SUM(CASE WHEN fr.rhq_status = 'APPROVED' THEN fr.amount_granted ELSE 0 END), 0) +
                    COALESCE(SUM(CASE WHEN fr.rhq_status = 'TOKEN_PROVIDED' THEN fr.token_amount ELSE 0 END), 0) AS assigned_amount, # This was correct
                    (SELECT COALESCE(SUM(eh.amount_spent), 0) FROM expenditure_history eh JOIN fund_requests fr_inner ON eh.request_id = fr_inner.request_id WHERE fr_inner.station_id = u.station_id) AS used_amount # This was correct
                FROM
                    users u
                LEFT JOIN
                    fund_requests fr ON u.station_id = fr.station_id AND fr.rhq_status IN ('APPROVED', 'TOKEN_PROVIDED') # This was correct
                WHERE
                    u.role = 'STATION'
                GROUP BY
                    u.user_id, u.station_name
                ORDER BY
                    u.station_name;
            """)
            summary_data = cursor.fetchall()
            
            # Calculate residual amount in Python for clarity
            for row in summary_data:
                row['residual_amount'] = row['assigned_amount'] - row['used_amount']
            
            return summary_data

    @staticmethod
    def create_request(station_id, user_id, purpose, description, amount):
        with get_cursor() as (cursor, conn):
            cursor.execute("""
               INSERT INTO fund_requests (station_id, user_id, purpose, description, amount_requested, created_at, rhq_status)
                VALUES (%s, %s, %s, %s, %s, NOW(), 'PENDING')
            """, (station_id, user_id, purpose, description, amount))
            conn.commit()

    @staticmethod
    def get_request_status_summary():
        """Gets a count of requests grouped by their RHQ status."""
        with get_cursor(dictionary=True) as (cursor, _):
            cursor.execute("""
                SELECT rhq_status, COUNT(*) as status_count
                FROM fund_requests
                WHERE rhq_status IS NOT NULL AND rhq_status != ''
                GROUP BY rhq_status
            """)
            return cursor.fetchall()

    @staticmethod
    def update_station_status(request_id: int, new_status: str, l1_value=None):
        """Updates the station-side status and L1 value for a fund request."""
        with get_cursor() as (cursor, conn):
            if l1_value is not None:
                query = "UPDATE fund_requests SET station_status = %s, l1_value = %s WHERE request_id = %s"
                cursor.execute(query, (new_status, l1_value, request_id))
            else:
                query = "UPDATE fund_requests SET station_status = %s WHERE request_id = %s"
                cursor.execute(query, (new_status, request_id))
            conn.commit()
            return cursor.rowcount > 0
