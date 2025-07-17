# Import config modules
try:
    from config.database import DatabaseConfig
except ImportError:
    try:
        from src.config.database import DatabaseConfig
    except ImportError:
        from ..config.database import DatabaseConfig
import pandas as pd
from datetime import datetime, timedelta

class DashboardManager:
    def __init__(self):
        self.db_config = DatabaseConfig()

    def get_measurement_data(self, parameter_id, start_date=None, end_date=None):
        """Lấy dữ liệu đo cho một thông số trong khoảng thời gian"""
        connection = self.db_config.get_connection()
        if connection:
            try:
                query = """
                    SELECT m.measured_at, m.value, p.name as parameter_name, 
                           p.unit, md.name as model_name
                    FROM measurements m
                    JOIN parameters p ON m.parameter_id = p.id
                    JOIN models md ON p.model_id = md.id
                    WHERE m.parameter_id = %s
                """
                params = [parameter_id]

                if start_date:
                    query += " AND m.measured_at >= %s"
                    params.append(start_date)
                if end_date:
                    query += " AND m.measured_at <= %s"
                    params.append(end_date)

                query += " ORDER BY m.measured_at"

                df = pd.read_sql_query(query, connection, params=params)
                return df
            except Exception as e:
                print(f"Lỗi khi lấy dữ liệu: {e}")
                return pd.DataFrame()
            finally:
                connection.close()
        return pd.DataFrame()

    def get_parameter_statistics(self, parameter_id, start_date=None, end_date=None):
        """Lấy thống kê của một thông số trong khoảng thời gian"""
        df = self.get_measurement_data(parameter_id, start_date, end_date)
        if df.empty:
            return None

        stats = {
            'min': df['value'].min(),
            'max': df['value'].max(),
            'mean': df['value'].mean(),
            'std': df['value'].std(),
            'count': len(df)
        }
        return stats

    def get_parameters_by_model(self, model_id):
        """Lấy danh sách thông số của một model"""
        connection = self.db_config.get_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(
                    """SELECT p.*, m.name as model_name 
                    FROM parameters p
                    JOIN models m ON p.model_id = m.id
                    WHERE p.model_id = %s
                    ORDER BY p.name""",
                    (model_id,)
                )
                return cursor.fetchall()
            except Exception as e:
                print(f"Lỗi khi lấy danh sách thông số: {e}")
                return []
            finally:
                cursor.close()
                connection.close()
        return []

    def get_latest_measurements(self, limit=10):
        """Lấy các kết quả đo gần nhất"""
        connection = self.db_config.get_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(
                    """SELECT m.*, p.name as parameter_name, p.unit,
                           md.name as model_name
                    FROM measurements m
                    JOIN parameters p ON m.parameter_id = p.id
                    JOIN models md ON p.model_id = md.id
                    ORDER BY m.measured_at DESC
                    LIMIT %s""",
                    (limit,)
                )
                return cursor.fetchall()
            except Exception as e:
                print(f"Lỗi khi lấy kết quả đo gần nhất: {e}")
                return []
            finally:
                cursor.close()
                connection.close()
        return []

    def get_measurement_summary(self, days=7):
        """Lấy tổng hợp số lượng đo theo ngày"""
        connection = self.db_config.get_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                start_date = datetime.now() - timedelta(days=days)
                cursor.execute(
                    """SELECT DATE(measured_at) as date, COUNT(*) as count
                    FROM measurements
                    WHERE measured_at >= %s
                    GROUP BY DATE(measured_at)
                    ORDER BY date""",
                    (start_date,)
                )
                return cursor.fetchall()
            except Exception as e:
                print(f"Lỗi khi lấy tổng hợp đo: {e}")
                return []
            finally:
                cursor.close()
                connection.close()
        return []

    def get_total_product(self, model_id):
        """Lấy tổng số sản phẩm đã đo cho một model"""
        connection = self.db_config.get_connection()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                    SELECT COUNT(*) FROM measurements
                    WHERE parameter_id IN (SELECT id FROM parameters WHERE model_id = %s)
                """
                cursor.execute(query, (model_id,))
                result = cursor.fetchone()
                return result[0] if result else 0
            except Exception as e:
                print(f"Lỗi khi lấy tổng số sản phẩm: {e}")
                return 0
            finally:
                cursor.close()
                connection.close()
        return 0

    def get_history_by_model(self, model_id, limit=50):
        """Lấy lịch sử đo các sản phẩm của model - mỗi hàng là 1 sản phẩm"""
        print(f"[DEBUG] get_history_by_model called with model_id={model_id}, limit={limit}")
        connection = self.db_config.get_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                
                # Lấy danh sách thông số của model
                cursor.execute("""
                    SELECT id, name, unit 
                    FROM parameters 
                    WHERE model_id = %s 
                    ORDER BY id
                """, (model_id,))
                parameters = cursor.fetchall()
                
                if not parameters:
                    return []
                
                # Lấy các thời điểm đo khác nhau (group theo thời gian gần nhất)
                # Giả định: các measurement cùng thời gian (trong vòng 30 giây) thuộc cùng 1 sản phẩm
                query_time = """
                    SELECT DISTINCT DATE_FORMAT(m.measured_at, '%Y-%m-%d %H:%i:%s') as time_group,
                           MIN(m.measured_at) as measured_at
                    FROM measurements m
                    JOIN parameters p ON m.parameter_id = p.id
                    WHERE p.model_id = %s
                    GROUP BY DATE_FORMAT(m.measured_at, '%Y-%m-%d %H:%i:%s')
                    ORDER BY measured_at DESC
                    LIMIT %s
                """
                params_time = (model_id, limit)
                print(f"[DEBUG] Executing time query: {query_time}")
                print(f"[DEBUG] With params: {params_time}")
                cursor.execute(query_time, params_time)
                time_groups = cursor.fetchall()
                
                history = []
                for i, time_group in enumerate(time_groups):
                    # Tạo một record cho sản phẩm này
                    product = {
                        'STT': i + 1,
                        'measured_at': time_group['measured_at']
                    }
                    
                    # Lấy giá trị của từng thông số cho time_group này
                    for param in parameters:
                        query_value = """
                            SELECT value 
                            FROM measurements 
                            WHERE parameter_id = %s
                            AND DATE_FORMAT(measured_at, '%Y-%m-%d %H:%i:%s') = %s
                            ORDER BY measured_at DESC
                            LIMIT 1
                        """
                        params_value = (param['id'], time_group['time_group'])
                        print(f"[DEBUG] Executing value query for param {param['name']}: {query_value}")
                        print(f"[DEBUG] With params: {params_value}")
                        cursor.execute(query_value, params_value)
                        
                        result = cursor.fetchone()
                        param_key = f"{param['name']} ({param['unit']})"
                        
                        if result and result['value'] is not None:
                            product[param_key] = f"{result['value']:.3f}"
                        else:
                            product[param_key] = "--"
                    
                    history.append(product)
                
                return history
                
            except Exception as e:
                print(f"Lỗi khi lấy lịch sử đo: {e}")
                return []
            finally:
                cursor.close()
                connection.close()
        return [] 