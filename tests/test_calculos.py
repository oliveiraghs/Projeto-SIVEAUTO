import unittest
import pandas as pd
import numpy as np

# Lógica isolada de deteção (Réplica da lógica do ColetaController para validação matemática)
def detetar_outlier_teste(valor, media, desvio):
    # Se não houver desvio padrão (ex: amostra única), não é outlier
    if pd.isna(desvio) or desvio == 0:
        return False
    
    # Cálculo do Z-Score: Quantos desvios o valor está afastado da média?
    z_score = abs((valor - media) / desvio)
    
    # Regra definida no projeto: Z-Score > 2.0 é anomalia
    return z_score > 2.0

class TesteAuditoriaPrecos(unittest.TestCase):

    def test_preco_normal(self):
        """Teste 1: Um preço ligeiramente acima da média não deve ser marcado."""
        media = 100000
        desvio = 5000
        preco = 105000 # 1 desvio acima (Dentro do aceitável)
        
        is_outlier = detetar_outlier_teste(preco, media, desvio)
        self.assertFalse(is_outlier, "Erro: Preço normal foi marcado incorretamente como outlier.")

    def test_preco_absurdo(self):
        """Teste 2: Um preço muito acima da média deve ser detetado."""
        media = 100000
        desvio = 5000
        preco = 200000 # 20 desvios acima (Absurdo/Erro de digitação)
        
        is_outlier = detetar_outlier_teste(preco, media, desvio)
        self.assertTrue(is_outlier, "Erro: Preço absurdo passou despercebido.")

    def test_cenario_real_com_pandas(self):
        """Teste 3: Simulação completa de um dataset com erro."""
        # Cenário: 5 pesquisadores coletaram preços reais, 1 errou o zero
        dados = [
            70000, 71000, 69000, 70500, 70200, # Preços Reais
            1000000 # O Erro (1 milhão num carro de 70k)
        ]
        
        df = pd.DataFrame(dados, columns=['valor'])
        
        # 1. Calcular estatísticas
        media = df['valor'].mean()
        desvio = df['valor'].std()
        
        # 2. Aplicar filtro
        df['is_outlier'] = df['valor'].apply(lambda x: detetar_outlier_teste(x, media, desvio))
        
        # 3. Verificar resultados
        outliers = df[df['is_outlier'] == True]
        
        print(f"\n--- 📝 Relatório do Teste Automatizado ---")
        print(f"Preços analisados: {dados}")
        print(f"Outliers detetados: {outliers['valor'].tolist()}")
        
        # Validações Finais
        self.assertEqual(len(outliers), 1, "Deveria ter encontrado exatamente 1 outlier.")
        self.assertEqual(outliers.iloc[0]['valor'], 1000000, "O outlier detetado não é o valor esperado.")

if __name__ == '__main__':
    unittest.main()