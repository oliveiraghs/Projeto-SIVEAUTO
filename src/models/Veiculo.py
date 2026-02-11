from src.services.DatabaseService import DatabaseService

class Veiculo:
    def __init__(self, id, marca, modelo, ano, preco_referencia):
        self.id = id
        self.marca = marca
        self.modelo = modelo
        self.ano = ano
        self.preco_referencia = preco_referencia

    @staticmethod
    def get_todas_marcas():
        """Retorna marcas únicas"""
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT marca FROM veiculos ORDER BY marca")
        lista = [row[0] for row in cursor.fetchall()]
        conn.close()
        return lista

    @staticmethod
    def get_modelos_por_marca(marca):
        """Retorna modelos apenas da marca selecionada"""
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT modelo FROM veiculos WHERE marca = ? ORDER BY modelo", (marca,))
        lista = [row[0] for row in cursor.fetchall()]
        conn.close()
        return lista

    @staticmethod
    def get_anos_por_modelo(modelo):
        """Retorna anos apenas do modelo selecionado"""
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT ano FROM veiculos WHERE modelo = ? ORDER BY ano DESC", (modelo,))
        lista = [row[0] for row in cursor.fetchall()]
        conn.close()
        return lista

    @staticmethod
    def buscar_veiculo_exato(marca, modelo, ano):
        """Busca o veículo final"""
        conn = DatabaseService.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, marca, modelo, ano, preco_referencia 
            FROM veiculos 
            WHERE marca = ? AND modelo = ? AND ano = ?
        """, (marca, modelo, ano))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Veiculo(row[0], row[1], row[2], row[3], row[4])
        return None