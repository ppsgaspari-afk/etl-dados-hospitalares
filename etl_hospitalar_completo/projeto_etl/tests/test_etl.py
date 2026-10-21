import sys
import contextlib
import uuid
import shutil
import unittest
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import etl_avc as avc
import etl_medicamentos as med
import etl_iam as iam
ROOT=Path(__file__).resolve().parents[1]

@contextlib.contextmanager
def diretorio_teste():
    pasta = ROOT/'work_tests'/uuid.uuid4().hex
    pasta.mkdir(parents=True)
    try:
        yield pasta
    finally:
        shutil.rmtree(pasta)

class IAM(unittest.TestCase):
    def test_consolidacao_de_referencia(self):
        partes=[]
        for nome in ['iam_sintetico_alfa.xlsx','iam_sintetico_beta.xlsx']:
            partes.append(iam.padronizar(pd.read_excel(ROOT/'dados/entrada'/nome)))
        base=pd.concat(partes,ignore_index=True)
        self.assertEqual(len(base),20)
        self.assertFalse(base.isna().any().any())
        self.assertEqual(base.TEMPO_PORTA_ECG.sum(),200)
        self.assertEqual(base.TEMPO_ECG_AGULHA.sum(),590)
    def test_duplicadas(self):
        with self.assertRaises(ValueError):
            iam.padronizar(pd.DataFrame(columns=['Hospital','Unidade de Saúde']))

class AVC(unittest.TestCase):
    def test_alias_e_colunas_ausentes(self):
        r=avc.padronizar(pd.DataFrame({' Hóspital ':['X']}))
        self.assertEqual(list(r.columns),avc.COLUNAS)
        self.assertEqual(r.UNIDADE[0],'X')
        self.assertTrue(pd.isna(r.DATA[0]))
    def test_cabecalhos_duplicados(self):
        with self.assertRaisesRegex(ValueError,'duplicadas'):
            avc.padronizar(pd.DataFrame(columns=['Hospital','UNIDADE']))
    def test_pipeline_e_linhas_origem(self):
        with diretorio_teste() as d:
            base,pend=avc.executar(ROOT/'dados/entrada_avc',Path(d))
            self.assertEqual(len(base),8)
            self.assertEqual(len(pend),7)
            self.assertEqual(base.POSSIVEL_DUPLICATA.sum(),2)
            self.assertEqual(pend[pend.ARQUIVO_ORIGEM.eq('avc_beta.xlsx')].LINHA_ORIGEM.tolist(),[2,3,4])
            self.assertTrue(pd.isna(base.DATA[2]))
            self.assertTrue(pd.isna(base.TEMPO_PORTA_AGULHA[2]))
            self.assertIn('negativo',pend.PROBLEMAS[1])
            self.assertIn('cronologia',pend.PROBLEMAS[3])
            saved=pd.read_excel(Path(d)/'consolidado_avc_demo.xlsx',sheet_name=None)
            self.assertEqual(list(saved),['Base','Pendencias'])
            self.assertEqual(len(saved['Base']),8)
    def test_entrada_vazia(self):
        with diretorio_teste() as d:
            with self.assertRaises(FileNotFoundError): avc.executar(Path(d),Path(d))
    def test_chaves_incompletas_nao_duplicam(self):
        df=pd.DataFrame([[None,None,None,0,0]]*2,columns=avc.COLUNAS)
        df['ARQUIVO_ORIGEM']='teste';df['LINHA_ORIGEM']=[2,3]
        base,pend=avc.transformar(df)
        self.assertFalse(base.POSSIVEL_DUPLICATA.any())
        self.assertEqual(len(pend),2)
    def test_tempo_nao_finito(self):
        df=pd.DataFrame([['X','13/03/2026','40–59',float('inf'),50]],columns=avc.COLUNAS)
        df['ARQUIVO_ORIGEM']='teste';df['LINHA_ORIGEM']=2
        base,pend=avc.transformar(df)
        self.assertIn('não finito',pend.PROBLEMAS[0])

class Medicamentos(unittest.TestCase):
    def test_conversao(self):
        for valor,esperado in [('R$ 1.234,56',1234.56),('25,50',25.5),(0,0),(12.5,12.5),('12.50',12.5)]:
            self.assertEqual(med.converter_valor(valor),esperado)
        for valor in [None,'inválido',float('inf'),True,'']:
            self.assertIsNone(med.converter_valor(valor))
    def test_pipeline_meses_precos_e_pendencias(self):
        with diretorio_teste() as d:
            out=Path(d)/'saida.xlsx'
            r=med.consolidar(ROOT/'dados/entrada_medicamentos',out)
            self.assertEqual(r.ANO.tolist(),[2025]*3+[2026]*3)
            self.assertEqual(r['TENECTEPLASE 40 mg'].tolist(),[100,101,102,110,111,112])
            self.assertEqual(r['ALTEPLASE 20 mg'][0],1230.5)
            self.assertTrue(pd.isna(r['ALTEPLASE 20 mg'][4]))
            self.assertTrue(pd.isna(r['ALTEPLASE 50 mg'][5]))
            sheets=pd.read_excel(out,sheet_name=None)
            self.assertEqual(len(sheets['Pendencias']),2)
            self.assertEqual(len(sheets['Origens']),28)
    def test_duplicatas_nao_somadas(self):
        import shutil
        with diretorio_teste() as d:
            src=ROOT/'dados/entrada_medicamentos/valores_sinteticos_2025.xlsx'
            shutil.copy(src,Path(d)/'a_2025.xlsx');shutil.copy(src,Path(d)/'b_2025.xlsx')
            with self.assertRaisesRegex(ValueError,'duplicado'):
                med.consolidar(Path(d),Path(d)/'saida.xlsx')
    def test_ano_ausente(self):
        import shutil
        with diretorio_teste() as d:
            shutil.copy(ROOT/'dados/entrada_medicamentos/valores_sinteticos_2025.xlsx',Path(d)/'sem_ano.xlsx')
            with self.assertRaisesRegex(ValueError,'ano'):
                med.consolidar(Path(d),Path(d)/'saida.xlsx')
    def test_entrada_vazia(self):
        with diretorio_teste() as d:
            with self.assertRaises(FileNotFoundError):med.consolidar(Path(d),Path(d)/'saida.xlsx')

if __name__=='__main__': unittest.main()

