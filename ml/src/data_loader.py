import logging
import pandas as pd
from pathlib import Path
from src.config import RAW_DATA_DIR, PROJECT_ROOT

logger = logging.getLogger(__name__)

class DataLoader:
    """Carrega e explora dados."""
    
    @staticmethod
    def load_dataset(filename: str = "dataset_sentimentos_500.csv") -> pd.DataFrame:
        """
        Carrega dataset de sentimentos.
        
        Args:
            filename: Nome do arquivo
            
        Returns:
            DataFrame com dados
        """
        # Procurar arquivo em múltiplos locais
        possible_paths = [
            RAW_DATA_DIR / filename,
            PROJECT_ROOT / filename,
            PROJECT_ROOT.parent / filename,  # Para o caso de estar em RafaPython
            Path("/workspace") / filename,
            Path("/app/ml/data/raw") / filename,
        ]
        
        data_path = None
        for path in possible_paths:
            if path.exists():
                data_path = path
                logger.info(f"✅ Arquivo encontrado: {path}")
                break
        
        if data_path is None:
            raise FileNotFoundError(
                f"Dataset '{filename}' não encontrado em: {[str(p) for p in possible_paths]}"
            )
        
        # Carregar CSV
        df = pd.read_csv(data_path)
        logger.info(f"Dataset carregado: {df.shape[0]} linhas, {df.shape[1]} colunas")
        
        return df
    
    @staticmethod
    def explore_dataset(df: pd.DataFrame):
        """
        Explora dataset e loga informações.
        
        Args:
            df: DataFrame para explorar
        """
        logger.info("\n" + "="*80)
        logger.info("EXPLORAÇÃO DO DATASET")
        logger.info("="*80)
        
        logger.info(f"\nForma: {df.shape}")
        logger.info(f"\nColunas: {list(df.columns)}")
        logger.info(f"\nTipos de dados:\n{df.dtypes}")
        logger.info(f"\nMissing values:\n{df.isnull().sum()}")
        logger.info(f"\nDistribuição de sentimentos:\n{df['sentimento'].value_counts()}")
        logger.info(f"\nEstatísticas de nota:\n{df['nota'].describe()}")
