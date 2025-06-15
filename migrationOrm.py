import requests
from datetime import datetime, time
import time as sleep_time
import os
from Models.corredor import Corredor
from Models.linha import Linha
from Models.veiculo import Veiculo
from Models.itinerario import Itinerario
from Models.parada import Parada, LinhaParada
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert

load_dotenv()

# Configurações
API_URL = "http://api.olhovivo.sptrans.com.br/v2.1"
TOKEN = os.getenv('SPTRANS_API_TOKEN')
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"

# Configuração do SQLAlchemy
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
metadata = MetaData(schema="sptrans")  # Definindo o schema padrão

def autenticar_api():
    auth_url = f"{API_URL}/Login/Autenticar?token={TOKEN}"
    session = requests.Session()
    response = session.post(auth_url)

    if response.status_code == 200 and response.text == 'true':
        print("Autenticação na API SPTrans realizada com sucesso!")
        return session
    else:
        print(f"Falha na autenticação: {response.text}")
        return None

def popular_linhas(api_session):
    db_session = Session()
    total_registros = 0

    for termo in range(10):
        url = f"{API_URL}/Linha/Buscar?termosBusca={termo}"
        response = api_session.get(url)
        
        if response.status_code != 200:
            print(f"Erro ao buscar linhas: {response.text}")
            return
        
        linhas = response.json()        
        
        try:
            for linha in linhas:
                stmt = insert(Linha).values(
                    codigo=linha['cl'],
                    letreironumerico=linha['lt'],
                    modooperacao=linha['tl'],
                    modocircular=linha.get('lc', False),  # Usando get com valor padrão
                    sentido=linha['sl'],
                    descritivoprincipal=linha['tp'],
                    descritivosecundario=linha['ts']
                ).on_conflict_do_nothing(index_elements=['codigo'])
                result = db_session.execute(stmt)
                if result:
                    total_registros += 1

            db_session.commit()
            print(f"Tabela Linha populada com linhas contendo {termo} com sucesso!")
        except Exception as e:
            db_session.rollback()
            print(f"Erro ao popular linhas com linhas contendo {termo}: {e}")
        finally:
            db_session.close()

def popular_linha_parada(api_session):
    db_session = Session()
    
    try:
        # Obtém apenas os códigos das linhas existentes
        codigos_linha = [linha.codigo for linha in db_session.query(Linha.codigo).all()]
        total_relacoes = 0
        total_paradas = 0

        for codigo_linha in codigos_linha:
            url = f"{API_URL}/Parada/BuscarParadasPorLinha?codigoLinha={codigo_linha}"
            response = api_session.get(url)
            
            if response.status_code != 200:
                print(f"Erro ao buscar paradas para linha {codigo_linha}: {response.text}")
                continue
            
            paradas = response.json()
            
            for parada in paradas:
                # Verifica se a parada existe
                if not db_session.query(Parada).filter_by(codigo=parada['cp']).first():
                    # Insere a parada se não existir
                    result = db_session.execute(
                        insert(Parada).values(
                            codigo=parada['cp'],
                            nome=parada['np'],
                            endereco=parada['ed'],
                            latitude=float(parada['py']),
                            longitude=float(parada['px'])
                        ).on_conflict_do_nothing(index_elements=['codigo'])
                    )
                    if result:
                        total_paradas += 1
                
                # Insere a relação LinhaParada
                stmt = insert(LinhaParada).values(
                    codigolinha=codigo_linha,
                    codigoparada=parada['cp']
                ).on_conflict_do_nothing()
                
                result = db_session.execute(stmt)
                if result:
                    total_relacoes += 1
            
            db_session.commit()
        
        print(f"Tabelas Parada e LinhaParada populada com {total_paradas} paradas e {total_relacoes} relações")
    except Exception as e:
        db_session.rollback()
        print(f"Erro ao popular linha_parada: {e}")
    finally:
        db_session.close()

def popular_corredores(api_session):
    url = f"{API_URL}/Corredor"
    response = api_session.get(url)
    
    if response.status_code != 200:
        print(f"Erro ao buscar corredores: {response.text}")
        return
    
    corredores = response.json()
    
    db_session = Session()
    
    try:
        for corredor in corredores:
            stmt = insert(Corredor).values(
                codigo=corredor['cc'],
                nome=corredor['nc'],
            ).on_conflict_do_nothing(index_elements=['codigo'])
            
            db_session.execute(stmt)
        
        db_session.commit()
        print("Tabela Corredor populada com sucesso!")
    except Exception as e:
        db_session.rollback()
        print(f"Erro ao popular corredores: {e}")
    finally:
        db_session.close()

def popular_corredor_parada(api_session):
    db_session = Session()
    
    try:
        # Obtém apenas os códigos dos corredores existentes
        codigos_corredores = [corredor.codigo for corredor in db_session.query(Corredor.codigo).all()]
        total_paradas = 0
        total_paradas_atualizadas = 0
        
        for codigo_corredor in codigos_corredores:
            url = f"{API_URL}/Parada/BuscarParadasPorCorredor?codigoCorredor={codigo_corredor}"
            response = api_session.get(url)
            
            if response.status_code != 200:
                print(f"Erro ao buscar paradas para corredor {codigo_corredor}: {response.text}")
                continue
            
            paradas = response.json()
            
            for parada in paradas:
                # Verifica se a parada existe
                paradaExistente = db_session.query(Parada).filter_by(codigo=parada['cp']).first()
                if not paradaExistente:
                    # Insere a parada se não existir
                    result = db_session.execute(
                        insert(Parada).values(
                            codigo=parada['cp'],
                            nome=parada['np'],
                            endereco=parada['ed'],
                            latitude=float(parada['py']),
                            longitude=float(parada['px']),
                            codigocorredor=codigo_corredor
                        ).on_conflict_do_nothing(index_elements=['codigo'])
                    )
                    if result:
                        total_paradas += 1
                else:
                    if paradaExistente.CodigoCorredor != codigo_corredor:
                        result = db_session.execute(
                            update(Parada).where(Parada.codigo==parada['cp'].values(
                                codigocorredor=codigo_corredor    
                            ))
                        )
                        paradaExistente.CodigoCorredor = codigo_corredor
                        total_paradas_atualizadas += 1
            db_session.commit()
        print(f"Tabelas Parada e CorredorParada populada com {total_paradas} registros e {total_relacoes} relações")
    except Exception as e:
        db_session.rollback()
        print(f"Erro ao popular corredor_parada: {e}")
    finally:
        db_session.close()


def popular_veiculos_itinerario(api_session):
    db_session = Session()
    
    try:
        codigos_paradas = [parada.codigo for parada in db_session.query(Parada.codigo).all()]
        codigos_linhas = [linha.codigo for linha in db_session.query(Linha.codigo).all()]
        total_veiculos = 0
        total_itinerario = 0
        
        for codigo_linha in codigos_linhas:
            url = f"{API_URL}/Previsao/Linha?codigoLinha={codigo_linha}"
            response = api_session.get(url)
            
            if response.status_code != 200:
                print(f"Erro ao buscar previsões para linha {codigo_linha}: {response.text}")
                continue
            previsao = response.json()
            for parada in previsao['ps']:
                prefixos_veiculos = [veiculo.prefixo for veiculo in db_session.query(Veiculo.prefixo).all()]
                if parada['cp'] in codigos_paradas:
                    for veiculo in parada['vs']:
                        if veiculo['p'] not in prefixos_veiculos:
                            # Insere a veiculo se não existir
                            result = db_session.execute(
                                insert(Veiculo).values(
                                    prefixo=veiculo['p'],
                                    acessopcd=veiculo['a']
                                ).on_conflict_do_nothing(index_elements=['prefixo'])
                            )
                            if result:
                                total_veiculos += 1
                        #Insere Itinerário
                        stmt = insert(Itinerario).values(
                            codigolinha = codigo_linha,
                            prefixoveiculo = veiculo['p'],
                            datareferencia = veiculo['ta'],
                            codigoparada = parada['cp'],
                            previsaochegada = veiculo['t']
                        ).on_conflict_do_nothing()
                        result = db_session.execute(stmt)
                        if result:
                            total_itinerario += 1
                    db_session.commit()
        print(f"Tabelas Veiculo e Itinerario populadas com {total_veiculos} veiculos e {total_itinerario} itinerarios")
    except Exception as e:
        db_session.rollback()
        print(f"Erro ao popular veiculos e itinerários: {e}")
    finally:
        db_session.close()

def main():
    session = autenticar_api()
    if session is None:
        return
    
    try:
        # Ordem correta de população
        #popular_linhas(session)
        #popular_linha_parada(session)
        #popular_corredores(session)
        #popular_corredor_parada(session)
        popular_veiculos_itinerario(session)
        print("Banco de dados populado com sucesso!")
    except Exception as e:
        print(f"Erro durante a execução: {e}")

if __name__ == "__main__":
    main()