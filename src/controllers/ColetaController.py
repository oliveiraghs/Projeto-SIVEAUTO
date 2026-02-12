import pandas as pd
import numpy as np
from src.services.DatabaseService import DatabaseService

class ColetaController:
    
    @staticmethod
    def buscar_coletas_com_auditoria():
        """
        [ADMIN] Busca todas as coletas e marca outliers (Z-Score > 2).
        """
        conn = DatabaseService.get_connection()
        query = """
            SELECT c.id, u.nome as pesquisador, v.marca, v.modelo, v.versao, 
                   c.local_loja, c.valor_encontrado, c.data_coleta, c.veiculo_id
            FROM coletas c
            JOIN veiculos v ON c.veiculo_id = v.id
            JOIN usuarios u ON c.usuario_id = u.id
            ORDER BY c.data_coleta DESC
        """
        df = pd.read_sql(query, conn)
        conn.close()

        if df.empty: return df

        # Lógica de Outliers (Z-Score)
        stats = df.groupby('veiculo_id')['valor_encontrado'].agg(['mean', 'std']).reset_index()
        df = df.merge(stats, on='veiculo_id', how='left')

        def detectar(row):
            if pd.isna(row['std']) or row['std'] == 0: return False
            return abs((row['valor_encontrado'] - row['mean']) / row['std']) > 2.0

        df['is_outlier'] = df.apply(detectar, axis=1)
        return df.drop(columns=['mean', 'std', 'veiculo_id'])

    @staticmethod
    def registrar_busca(marca, modelo, versao, ano):
        """
        [PS-14] Log de Auditoria: Grava o que o usuário buscou.
        """
        try:
            conn = DatabaseService.get_connection()
            conn.execute(
                "INSERT INTO buscas (marca_buscada, modelo_buscado, versao_buscada, ano_buscado) VALUES (?,?,?,?)", 
                (marca, modelo, versao, int(ano))
            )
            conn.commit()
        except Exception as e:
            print(f"Erro ao logar busca: {e}")
        finally:
            conn.close()

    @staticmethod
    def obter_estatisticas_publicas(marca, modelo, versao, ano):
        """
        [PS-12] Retorna Média e Melhor Oferta, EXCLUINDO outliers para não enganar o público.
        """
        conn = DatabaseService.get_connection()
        
        # 1. Pega ID do Veículo
        v_df = pd.read_sql("SELECT id FROM veiculos WHERE marca=? AND modelo=? AND versao=? AND ano=?", conn, params=(marca, modelo, versao, int(ano)))
        
        if v_df.empty:
            conn.close(); return None

        v_id = int(v_df.iloc[0]['id'])

        # 2. Busca todas as coletas desse carro
        df = pd.read_sql("SELECT valor_encontrado, local_loja FROM coletas WHERE veiculo_id = ?", conn, params=(v_id,))
        conn.close()

        if df.empty: return {"status": "empty"}

        # 3. Filtro de Qualidade (Remove Outliers antes de calcular)
        media_bruta = df['valor_encontrado'].mean()
        desvio = df['valor_encontrado'].std()

        if pd.notna(desvio) and desvio > 0:
            # Mantém apenas quem está DENTRO de 2 desvios padrão
            df_limpo = df[abs((df['valor_encontrado'] - media_bruta) / desvio) <= 2.0]
        else:
            df_limpo = df # Se não tem desvio (ex: 1 coleta), usa o dado que tem

        if df_limpo.empty: return {"status": "outliers_only"} # Caso raro onde tudo é outlier

        # 4. Calcula Estatísticas Finais (Limpas)
        stats = {
            "status": "ok",
            "media": df_limpo['valor_encontrado'].mean(),
            "melhor_preco": df_limpo['valor_encontrado'].min(),
            "total_amostras": len(df_limpo),
            # Pega a loja do melhor preço (do dataset limpo)
            "loja_barata": df_limpo.loc[df_limpo['valor_encontrado'].idxmin()]['local_loja']
        }
        return stats