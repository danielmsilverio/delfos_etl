from typing import Any, Dict, List

import pandas as pd


class Transformer:
    @staticmethod
    def process_data(raw_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Recebe lista de dicts da API, converte para DataFrame,
        agrega a cada 10 min e transforma para formato Long (Tidy Data).
        """
        if not raw_data:
            return pd.DataFrame()

        df = pd.DataFrame(raw_data)

        # Converter timestamp para datetime e definir como índice
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)

        # Variáveis para agregar
        # Apenas os nomes que batem com o JSON da API
        metrics = ['wind_speed', 'power', 'ambient_temperature']

        # Filtra apenas colunas que existem no dataframe para evitar erro
        available_metrics = [m for m in metrics if m in df.columns]

        # 1. Agregação (Resample 10min)
        # Cálcular as estatísticas pedidas: mean, min, max, std
        list_agg = ['mean', 'min', 'max', 'std']
        df_agg = df[available_metrics].resample('10min').agg(list_agg)

        # O DataFrame agora tem MultiIndex nas colunas:
        #   (wind_speed, mean), (wind_speed, min)...
        # Transformando para formato longo.

        dfs_to_concat = []

        for metric in available_metrics:
            # Seleciona as colunas dessa métrica
            sub_df = df_agg[metric].copy()

            # Para cada tipo de agregação, criamos linhas
            # Ex: wind_speed_mean, wind_speed_min
            for stat in ['mean', 'min', 'max', 'std']:
                temp_df = sub_df[[stat]].rename(columns={stat: 'value'})
                # Cria o nome do sinal: ex "wind_speed_mean"
                temp_df['signal_name'] = f'{metric}_{stat}'
                dfs_to_concat.append(temp_df)

        if not dfs_to_concat:
            return pd.DataFrame()

        # Concatena tudo num formato vertical
        final_df = pd.concat(dfs_to_concat)

        # Reset index para ter timestamp como coluna
        final_df.reset_index(inplace=True)

        # Remove linhas com NaN (onde não houve dado para calcular)
        final_df.dropna(subset=['value'], inplace=True)

        return final_df
